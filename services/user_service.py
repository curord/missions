from datetime import datetime, date, timedelta
from typing import List, Optional, Any
import database
from models.user import User
from repositories.user_repository import UserRepository


class UserService:
    """
    Servei per a centralitzar tota la lògica de negoci associada als usuaris.
    S'encarrega de calcular dinàmicament i optimitzadament en lot les mètriques de gamificació.
    """

    def __init__(self, user_repository: Optional[UserRepository] = None):
        self.user_repo = user_repository or UserRepository()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Obté un usuari amb les mètriques de gamificació calculades.
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None

        self._hydrate_users_in_bulk([user])
        return user

    def get_user_by_name(self, name: str) -> Optional[User]:
        """
        Cerca un usuari pel seu nom de pila (case-insensitive).
        """
        row = database.query_one(
            """
            SELECT *
            FROM users
            WHERE LOWER(name) = LOWER(?)
            """,
            (name,)
        )
        if not row:
            return None
        
        user = self.user_repo._map_to_entity(row)
        self._hydrate_users_in_bulk([user])
        return user

    def get_all_users(self) -> List[User]:
        """
        Llista de tots els usuaris amb hidratació en lot (evita N+1 consultes).
        """
        users = self.user_repo.get_all()
        if not users:
            return []
        self._hydrate_users_in_bulk(users)
        return users

    def get_family_users(self, family_id: int = 1) -> List[User]:
        """
        Llista d'usuaris d'una mateixa família amb hidratació en lot.
        """
        users = self.user_repo.get_by_family_id(family_id)
        if not users:
            return []
        self._hydrate_users_in_bulk(users)
        return users

    def create_user(self, family_id: int, name: str, role: str, avatar: str = "👤", favorite_color: str = "#3b82f6") -> int:
        """
        Crea un nou membre de la família.
        """
        return self.user_repo.create(family_id, name, role, avatar, favorite_color)

    def update_user(self, user_id: int, name: str, role: str, avatar: str = "👤", favorite_color: str = "#3b82f6") -> bool:
        """
        Actualitza les dades d'un membre de la família.
        """
        return self.user_repo.update(user_id, name, role, avatar, favorite_color)


    def get_family_status_summary(self, family_id: int = 1) -> List[dict]:
        """
        Retorna la llista de membres d'una família enriquida amb el recompte de les seves missions
        pendents, les seves validacions pendents i l'indicador d'estat (🟢 / 🟠 / 🔴).
        """
        users = self.get_family_users(family_id)
        summary = []
        for user in users:
            pending_rows = database.query(
                "SELECT COUNT(*) AS total FROM mission_assignments WHERE user_id = ? AND status = 'pending'",
                (user.id,)
            )
            waiting_rows = database.query(
                "SELECT COUNT(*) AS total FROM mission_assignments WHERE user_id = ? AND status = 'waiting_validation'",
                (user.id,)
            )
            pending_count = pending_rows[0]["total"] if pending_rows else 0
            waiting_count = waiting_rows[0]["total"] if waiting_rows else 0

            if waiting_count > 0:
                indicator_color = "red"
                indicator_icon = "🔴"
                indicator_text = "Té validacions pendents"
            elif pending_count > 0:
                indicator_color = "orange"
                indicator_icon = "🟠"
                indicator_text = "Té missions pendents"
            else:
                indicator_color = "green"
                indicator_icon = "🟢"
                indicator_text = "Sense pendents"

            summary.append({
                "user": user,
                "pending_count": pending_count,
                "waiting_count": waiting_count,
                "indicator_color": indicator_color,
                "indicator_icon": indicator_icon,
                "indicator_text": indicator_text
            })
        return summary


    def calculate_level(self, points: int) -> int:
        """
        Calcula el nivell basant-se en els punts totals d'XP.
        Cada nivell requereix 100 XP. El nivell inicial és 1.
        """
        if points < 0:
            return 1
        return (points // 100) + 1

    def calculate_level_progress(self, points: int) -> int:
        """
        Calcula el percentatge de progrés cap al següent nivell.
        Cada nivell requereix 100 XP.
        """
        if points < 0:
            return 0
        return points % 100

    def calculate_streak(self, user_id: int) -> int:
        """
        Calcula la ratxa consecutiva de dies de missions completades d'un usuari.
        """
        dates_rows = database.query(
            """
            SELECT DISTINCT DATE(completed_at) AS comp_date
            FROM mission_assignments
            WHERE user_id = ? AND status = 'completed' AND completed_at IS NOT NULL
            ORDER BY comp_date DESC
            """,
            (user_id,)
        )
        completed_dates = []
        for row in dates_rows:
            try:
                d = datetime.strptime(row["comp_date"], "%Y-%m-%d").date()
                completed_dates.append(d)
            except (ValueError, TypeError):
                continue
        return self._calculate_streak_from_dates(completed_dates)

    def _hydrate_users_in_bulk(self, users: List[User]) -> None:
        """
        Calcula en lot les monedes i la ratxa de dies consecutius per a una llista d'usuaris.
        Redueix el nombre de consultes de (1 + 2*N) a només 3 consultes.
        """
        user_ids = [u.id for u in users if u.id is not None]
        if not user_ids:
            return

        # 1. Recuperar monedes en lot
        placeholders = ",".join("?" for _ in user_ids)
        coins_rows = database.query(
            f"""
            SELECT user_id, SUM(coins) AS total_coins
            FROM mission_assignments
            WHERE user_id IN ({placeholders}) AND status = 'completed'
            GROUP BY user_id
            """,
            tuple(user_ids)
        )
        earned_coins_map = {row["user_id"]: (row["total_coins"] or 0) for row in coins_rows}

        # Recuperar monedes gastades en recompenses en lot
        spent_rows = database.query(
            f"""
            SELECT rh.user_id, SUM(r.points_required) AS spent_coins
            FROM reward_history rh
            JOIN rewards r ON r.id = rh.reward_id
            WHERE rh.user_id IN ({placeholders})
            GROUP BY rh.user_id
            """,
            tuple(user_ids)
        )
        spent_coins_map = {row["user_id"]: (row["spent_coins"] or 0) for row in spent_rows}

        coins_map = {
            uid: max(0, earned_coins_map.get(uid, 0) - spent_coins_map.get(uid, 0))
            for uid in user_ids
        }


        # 2. Recuperar dates de completat per a ratxes en lot
        dates_rows = database.query(
            f"""
            SELECT DISTINCT user_id, DATE(completed_at) AS comp_date
            FROM mission_assignments
            WHERE user_id IN ({placeholders}) AND status = 'completed' AND completed_at IS NOT NULL
            ORDER BY user_id, comp_date DESC
            """,
            tuple(user_ids)
        )
        
        dates_map: dict = {}
        for row in dates_rows:
            uid = row["user_id"]
            if uid not in dates_map:
                dates_map[uid] = []
            try:
                d = datetime.strptime(row["comp_date"], "%Y-%m-%d").date()
                dates_map[uid].append(d)
            except (ValueError, TypeError):
                continue

        # 3. Assignar valors calculats a cada instància
        from services.family_config_service import FamilyConfigService
        family_id = users[0].family_id if (users and users[0].family_id) else 1
        config = FamilyConfigService().get_config(family_id)

        for user in users:
            user.level = self.calculate_level(user.points)
            user.level_progress = self.calculate_level_progress(user.points)
            user.coins = coins_map.get(user.id, 0)
            
            user_dates = dates_map.get(user.id, [])
            user.streak = self._calculate_streak_from_dates(
                user_dates,
                count_weekends=config.count_weekends_streaks
            )


    def _calculate_streak_from_dates(self, completed_dates: List[date], count_weekends: bool = True) -> int:
        """
        Calcula la ratxa consecutiva a partir d'una llista de dates úniques ordenades DESC.
        """
        if not completed_dates:
            return 0

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Si no hi ha cap completat avui ni ahir, la ratxa és 0
        if completed_dates[0] not in (today, yesterday):
            return 0

        streak = 1
        current_date = completed_dates[0]

        for next_date in completed_dates[1:]:
            diff = (current_date - next_date).days
            if diff == 1:
                streak += 1
                current_date = next_date
            elif not count_weekends:
                # Comprovar si les dates entremig son només cap de setmana
                check_date = current_date - timedelta(days=1)
                all_weekend = True
                while check_date > next_date:
                    if check_date.weekday() < 5:
                        all_weekend = False
                        break
                    check_date -= timedelta(days=1)
                if all_weekend:
                    streak += 1
                    current_date = next_date
                else:
                    break
            else:
                break

        return streak


