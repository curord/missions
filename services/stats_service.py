from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, date
from services.user_service import UserService
from services.mission_service import MissionService
from services.reward_service import RewardService
from repositories.stats_repository import StatsRepository


class StatsService:
    """
    Servei per a centralitzar tota la lògica de negoci i el càlcul previ de mètrics
    per al Centre d'Estadístiques. Garanteix que cap plantilla Jinja realitzi càlculs.
    """

    def __init__(
        self,
        stats_repo: Optional[StatsRepository] = None,
        user_service: Optional[UserService] = None,
        mission_service: Optional[MissionService] = None,
        reward_service: Optional[RewardService] = None
    ):
        self.stats_repo = stats_repo or StatsRepository()
        self.user_service = user_service or UserService()
        self.mission_service = mission_service or MissionService()
        self.reward_service = reward_service or RewardService()

    def get_user_stats_summary(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Calcula i organitza totes les dades individuals d'un usuari per a la Pestanya 1.
        """
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return None

        # 1. Càlcul de KPI i Perfil
        next_level_xp = 100 - (user.points % 100) if user.points >= 0 else 100

        # 2. Activitat
        act_counts = self.stats_repo.get_user_activity_counts(user.id)
        completed = act_counts.get("completed", 0)
        rejected = act_counts.get("rejected", 0)
        total_eval = completed + rejected
        
        success_rate = round((completed / total_eval) * 100, 1) if total_eval > 0 else 0.0

        # 3. Recompenses
        rewards_summary = self.stats_repo.get_user_rewards_summary(user.id)

        # 4. Historial i Categories
        history = self.mission_service.get_user_mission_history(user.id)
        categories = self.mission_service.get_categories()

        # 5. Calendari GitHub diari de l'usuari (últims 90 dies)
        user_calendar = self._build_github_calendar(
            self.stats_repo.get_user_daily_activity(user.id, days=90)
        )

        return {
            "user": user,
            "kpi": {
                "level": user.level,
                "xp": user.points,
                "next_level_xp": next_level_xp,
                "coins": user.coins,
                "streak": user.streak,
                "missions_completed": completed
            },
            "activity": {
                "completed": completed,
                "pending": act_counts.get("pending_total", 0),
                "waiting_validation": act_counts.get("waiting_validation", 0),
                "rejected": rejected,
                "cancelled": act_counts.get("cancelled", 0),
                "total_assignments": sum(act_counts.values()) - act_counts.get("pending_total", 0),
                "success_rate": success_rate
            },
            "rewards": rewards_summary,
            "history": history,
            "categories": categories,
            "calendar": user_calendar
        }

    def get_user_evolution_series(self, user_id: int, period: str = "total") -> Dict[str, Any]:
        """
        Retorna les dades d'evolució temporal estructurades per a ser consumides per Chart.js.
        """
        rows = self.stats_repo.get_evolution_points_by_period(user_id, period)
        
        labels = []
        xp_series = []
        coins_series = []
        approved_series = []
        rejected_series = []

        cumulative_xp = 0
        cumulative_coins = 0

        for r in rows:
            labels.append(r["date_key"] or "Sense data")
            cumulative_xp += (r["xp_gained"] or 0)
            cumulative_coins += (r["coins_gained"] or 0)
            
            xp_series.append(cumulative_xp)
            coins_series.append(cumulative_coins)
            approved_series.append(r["approved_count"] or 0)
            rejected_series.append(r["rejected_count"] or 0)

        return {
            "labels": labels,
            "datasets": {
                "xp": xp_series,
                "coins": coins_series,
                "approved": approved_series,
                "rejected": rejected_series
            }
        }

    def get_family_stats_summary(self, family_id: int = 1) -> Dict[str, Any]:
        """
        Calcula les dades de la Pestanya 2 (Estadístiques Familiars), incloent resum global,
        targetes de membres individuals per al modal, comparatives i calendari.
        """
        members = self.user_service.get_family_users(family_id)
        if not members:
            return {}

        # 1. Resum global de la família
        fam_summary = self.stats_repo.get_family_summary(family_id)

        # 2. Mètriques individuals per a cada membre
        members_detail = []
        total_streaks = 0

        for m in members:
            act = self.stats_repo.get_user_activity_counts(m.id)
            comp = act.get("completed", 0)
            rej = act.get("rejected", 0)
            tot = comp + rej
            succ = round((comp / tot) * 100, 1) if tot > 0 else 0.0
            
            rew = self.stats_repo.get_user_rewards_summary(m.id)
            total_streaks += m.streak

            members_detail.append({
                "id": m.id,
                "name": m.name,
                "role": m.role,
                "avatar": m.avatar,
                "favorite_color": m.favorite_color,
                "level": m.level,
                "xp": m.points,
                "next_level_xp": 100 - (m.points % 100) if m.points >= 0 else 100,
                "coins": m.coins,
                "streak": m.streak,
                "completed": comp,
                "pending": act.get("pending_total", 0),
                "waiting": act.get("waiting_validation", 0),
                "rejected": rej,
                "cancelled": act.get("cancelled", 0),
                "success_rate": succ,
                "rewards_bought": rew["total_bought"],
                "coins_spent": rew["total_coins_spent"]
            })

        # 3. Mitjanes familiars
        num_members = len(members)
        family_averages = {
            "avg_xp": round(fam_summary["total_xp"] / num_members, 1) if num_members > 0 else 0,
            "avg_missions": round(fam_summary["completed_count"] / num_members, 1) if num_members > 0 else 0,
            "avg_streak": round(total_streaks / num_members, 1) if num_members > 0 else 0
        }

        # 4. Calendari familiar (darrers 90 dies)
        family_calendar = self._build_github_calendar(
            self.stats_repo.get_family_daily_activity(family_id, days=90)
        )

        # 5. Estats de recompenses familiars
        rewards_stats = self.stats_repo.get_family_rewards_stats(family_id)

        return {
            "summary": fam_summary,
            "averages": family_averages,
            "members": members_detail,
            "calendar": family_calendar,
            "rewards_stats": rewards_stats
        }

    def get_leaderboards(self, family_id: int = 1, period: str = "total") -> Dict[str, List[Dict[str, Any]]]:
        """
        Genera els rànquings (Classificacions) per a la Pestanya 3 ordenats per cada categoria.
        """
        members = self.user_service.get_family_users(family_id)
        if not members:
            return {}

        rankings_raw = []
        for m in members:
            act = self.stats_repo.get_user_activity_counts(m.id)
            comp = act.get("completed", 0)
            rej = act.get("rejected", 0)
            tot = comp + rej
            succ = round((comp / tot) * 100, 1) if tot > 0 else 0.0
            rew = self.stats_repo.get_user_rewards_summary(m.id)

            rankings_raw.append({
                "id": m.id,
                "name": m.name,
                "avatar": m.avatar,
                "role": m.role,
                "xp": m.points,
                "coins": m.coins,
                "completed": comp,
                "streak": m.streak,
                "best_streak": m.streak, # fallback en absència de registre històric
                "rewards_count": rew["total_bought"],
                "success_rate": succ
            })

        # Generar rànquings ordenats amb posició
        def rank_by(key: str, reverse: bool = True) -> List[Dict[str, Any]]:
            sorted_list = sorted(rankings_raw, key=lambda x: x[key], reverse=reverse)
            result = []
            for idx, item in enumerate(sorted_list, start=1):
                badge = "🥇" if idx == 1 else ("🥈" if idx == 2 else ("🥉" if idx == 3 else f"#{idx}"))
                item_copy = dict(item)
                item_copy["position"] = idx
                item_copy["badge"] = badge
                result.append(item_copy)
            return result

        return {
            "xp": rank_by("xp"),
            "coins": rank_by("coins"),
            "completed": rank_by("completed"),
            "streak": rank_by("streak"),
            "best_streak": rank_by("best_streak"),
            "rewards": rank_by("rewards_count"),
            "success_rate": rank_by("success_rate")
        }

    def _build_github_calendar(self, daily_rows: List[Dict[str, Any]], days: int = 90) -> List[Dict[str, Any]]:
        """
        Construeix una llista de dies dels darrers N dies per a generar el calendari estil GitHub,
        assignant nivells d'activitat (🟩 Molta, 🟨 Mitjana, 🟥 Sense activitat).
        """
        activity_map = {r["date_str"]: r["completed_count"] for r in daily_rows}
        
        today = date.today()
        calendar_grid = []

        for i in range(days - 1, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            count = activity_map.get(d_str, 0)
            
            if count >= 3:
                level_class = "activity-high"
                label = "Molta activitat"
                color_emoji = "🟩"
            elif count >= 1:
                level_class = "activity-medium"
                label = "Activitat mitjana"
                color_emoji = "🟨"
            else:
                level_class = "activity-none"
                label = "Sense activitat"
                color_emoji = "🟥"

            calendar_grid.append({
                "date": d_str,
                "formatted_date": d.strftime("%d/%m/%Y"),
                "count": count,
                "level_class": level_class,
                "label": label,
                "color_emoji": color_emoji
            })

        return calendar_grid
