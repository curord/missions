from typing import List, Optional
import database
from models.mission import Mission
from models.assignment import Assignment
from models.category import Category


class MissionRepository:
    """
    Repositori per a gestionar operacions relacionades amb missions, categories i assignacions.
    Reutilitza exclusivament les funcions de database.py per a mantenir el comportament existent.
    """

    def get_by_id(self, mission_id: int) -> Optional[Mission]:
        """
        Recupera els detalls d'una missió pel seu identificador.
        """
        row = database.get_mission(mission_id)
        if not row:
            return None
        return self._map_to_mission(row)

    def get_all(self) -> List[Mission]:
        """
        Recupera el catàleg de totes les missions.
        """
        rows = database.get_all_missions()
        return [self._map_to_mission(row) for row in rows]

    def get_categories(self) -> List[Category]:
        """
        Recupera totes les categories de missions ordenades per nom.
        """
        rows = database.get_categories()
        return [
            Category(
                id=row.get("id"),
                name=row.get("name"),
                icon=row.get("icon"),
                color=row.get("color"),
                sort_order=row.get("sort_order", 0),
                active=row.get("active", 1)
            )
            for row in rows
        ]

    def get_user_missions(self, user_id: int) -> List[Assignment]:
        """
        Recupera les assignacions actives i no cancel·lades d'un usuari.
        """
        rows = database.get_user_missions(user_id)
        assignments = [self._map_to_assignment(row) for row in rows]

        # Hydrate gamer_name and assigned_names for each assignment
        for a in assignments:
            user_row = database.query_one("SELECT name FROM users WHERE id = ?", (a.user_id,))
            a.gamer_name = user_row["name"] if user_row else None

            assignee_rows = database.query(
                """
                SELECT u.name
                FROM mission_assignments ma
                JOIN users u ON u.id = ma.user_id
                WHERE ma.mission_id = ? AND ma.status <> 'cancelled'
                """,
                (a.mission_id,)
            )
            a.assigned_names = [r["name"] for r in assignee_rows]

        return assignments

    def get_waiting_validations(self) -> List[Assignment]:
        """
        Recupera les assignacions pendents de validació.
        """
        rows = database.get_waiting_validations()
        return [self._map_to_assignment(row) for row in rows]

    def get_user_mission_history(self, user_id: int) -> List[Assignment]:
        """
        Recupera l'historial complet d'assignacions finalitzades, rebutjades o cancel·lades d'un usuari.
        """
        rows = database.get_user_mission_history(user_id)
        assignments = [self._map_to_assignment(row) for row in rows]

        # Hydrate gamer_name and assigned_names for each assignment
        for a in assignments:
            user_row = database.query_one("SELECT name FROM users WHERE id = ?", (a.user_id,))
            a.gamer_name = user_row["name"] if user_row else None

            assignee_rows = database.query(
                """
                SELECT u.name
                FROM mission_assignments ma
                JOIN users u ON u.id = ma.user_id
                WHERE ma.mission_id = ? AND ma.status <> 'cancelled'
                """,
                (a.mission_id,)
            )
            a.assigned_names = [r["name"] for r in assignee_rows]

        return assignments


    def count_waiting_validations(self) -> int:
        """
        Compta el nombre total de validacions pendents.
        """
        return database.count_waiting_validations()

    def start_mission(self, assignment_id: int, user_id: int) -> None:
        """
        Marca una assignació com a iniciada (en curs).
        """
        database.start_mission(assignment_id, user_id)

    def complete_mission(self, assignment_id: int, user_id: int) -> None:
        """
        Marca una assignació com a pendent de validació.
        """
        database.complete_mission(assignment_id, user_id)


    def approve_mission(self, assignment_id: int, admin_id: int) -> bool:
        """
        Aprova la missió assignada, incrementa els punts del gamer i registra l'historial.
        """
        return database.approve_mission(assignment_id, admin_id)

    def reject_mission(self, assignment_id: int, admin_id: Optional[int] = None, reason: Optional[str] = None) -> None:
        """
        Rebutja la validació d'una missió i en registra el motiu i el validador.
        """
        database.reject_mission(assignment_id, admin_id, reason)



    def assign_mission(self, mission_id: int, user_id: int, assignment_type: str = "owner") -> int:
        """
        Crea una nova assignació de missió per a un usuari i en retorna l'ID.
        """
        return database.execute(
            """
            INSERT INTO mission_assignments (mission_id, user_id, assignment_type, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (mission_id, user_id, assignment_type)
        )

    def update_mission(self, mission_id: int, data: dict) -> None:
        """
        Actualitza els detalls d'una plantilla de missió.
        """
        existing = self.get_by_id(mission_id)


        existing_icon = existing.icon if existing else "🎯"
        existing_repeat_type = existing.repeat_type if existing else "none"

        requires_validation = 1 if data.get("requires_validation") in (1, "1", "on", True) else 0
        active = 1 if data.get("active") in (1, "1", "on", True) else 0

        database.execute(
            """
            UPDATE missions
            SET title = ?, category_id = ?, description = ?, icon = ?, points = ?, 
                difficulty = ?, estimated_minutes = ?, requires_validation = ?, repeat_type = ?, active = ?
            WHERE id = ?
            """,
            (
                data.get("title"),
                int(data.get("category_id")),
                data.get("description"),
                data.get("icon") or existing_icon,
                int(data.get("points") or 10),
                int(data.get("difficulty") or 1),
                int(data.get("estimated_minutes")) if data.get("estimated_minutes") else None,
                requires_validation,
                data.get("repeat_type") or existing_repeat_type,
                active,
                mission_id
            )
        )



    def create_mission(self, data: dict, family_id: int = 1) -> int:
        """
        Crea una nova plantilla de missió a la base de dades i en retorna l'ID.
        """
        requires_validation = 1 if data.get("requires_validation") in (1, "1", "on", True) else 0
        active = 1 if data.get("active") in (1, "1", "on", True) else 0

        return database.execute(
            """
            INSERT INTO missions (
                family_id, category_id, title, description, icon, mission_type_id,
                difficulty, estimated_minutes, points, xp, requires_validation,
                repeat_type, active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                family_id,
                int(data.get("category_id")),
                data.get("title"),
                data.get("description"),
                data.get("icon") or "🎯",
                int(data.get("mission_type_id")) if data.get("mission_type_id") else None,
                int(data.get("difficulty") or 1),
                int(data.get("estimated_minutes")) if data.get("estimated_minutes") else None,
                int(data.get("points") or 10),
                int(data.get("points") or 10),
                requires_validation,
                data.get("repeat_type", "none"),
                active
            )
        )





    def _map_to_mission(self, row: dict) -> Mission:
        """
        Mapeja un diccionari de dades de missió a una entitat de domini Mission.
        """
        return Mission(
            id=row.get("id"),
            family_id=row.get("family_id"),
            category_id=row.get("category_id"),
            title=row.get("title"),
            description=row.get("description"),
            icon=row.get("icon"),
            mission_type_id=row.get("mission_type_id"),
            difficulty=row.get("difficulty", 1),
            estimated_minutes=row.get("estimated_minutes"),
            points=row.get("points", 10),
            xp=row.get("xp", 0),
            requires_validation=row.get("requires_validation", 0),
            repeat_type=row.get("repeat_type", "none"),
            coins=row.get("coins", 0),
            repeat_same_day=row.get("repeat_same_day", 0),
            expire_action=row.get("expire_action", "cancel"),
            color=row.get("color"),
            sort_order=row.get("sort_order", 0),
            active=row.get("active", 1),
            created_at=row.get("created_at"),
            # Virtual fields derived from joints
            category_name=row.get("category_name"),
            category_icon=row.get("category_icon"),
            category_color=row.get("category_color"),
            mission_type=row.get("mission_type")
        )

    def _map_to_assignment(self, row: dict) -> Assignment:
        """
        Mapeja un diccionari de dades d'assignació a una entitat de domini Assignment.
        """
        return Assignment(
            id=row.get("assignment_id") or row.get("id"),
            mission_id=row.get("mission_id"),
            user_id=row.get("user_id"),
            assignment_type=row.get("assignment_type", "owner"),
            assigned_date=row.get("assigned_date"),
            due_date=row.get("due_date"),
            status=row.get("status", "pending"),
            completed_at=row.get("completed_at"),
            completed_by=row.get("completed_by"),
            validated_at=row.get("validated_at"),
            validated_by=row.get("validated_by"),
            comment=row.get("comment"),
            coins=row.get("coins", 0),
            completed_points=row.get("completed_points"),
            # Virtual fields derived from joints
            title=row.get("title"),
            description=row.get("description"),
            icon=row.get("icon"),
            points=row.get("points"),
            requires_validation=row.get("requires_validation"),
            category=row.get("category"),
            color=row.get("color"),
            category_icon=row.get("category_icon"),
            completed_by_name=row.get("completed_by_name"),
            validated_by_name=row.get("validated_by_name"),
            gamer_name=row.get("gamer_name"),
            time_ago=row.get("time_ago"),
            completed_date=row.get("completed_date")
        )

