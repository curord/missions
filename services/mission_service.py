from datetime import datetime
from typing import List, Optional
from models.mission import Mission
from models.assignment import Assignment
from models.category import Category
from repositories.mission_repository import MissionRepository
import database



class MissionService:
    """
    Servei per a centralitzar la lògica de negoci associada a les missions, categories i assignacions.
    Actualment implementa únicament la lògica de lectura.
    """

    def __init__(self, mission_repository: Optional[MissionRepository] = None):
        self.mission_repo = mission_repository or MissionRepository()

    def get_mission_by_id(self, mission_id: int) -> Optional[Mission]:
        """
        Obté una missió pel seu identificador.
        """
        return self.mission_repo.get_by_id(mission_id)

    def get_all_missions(self) -> List[Mission]:
        """
        Obté tot el catàleg de missions.
        """
        return self.mission_repo.get_all()

    def get_categories(self) -> List[Category]:
        """
        Obté la llista de totes les categories.
        """
        return self.mission_repo.get_categories()

    def get_user_missions(self, user_id: int) -> List[Assignment]:
        """
        Obté les assignacions de missions actives d'un usuari, formatant la data de validació/rebuig.
        """
        assignments = self.mission_repo.get_user_missions(user_id)
        for a in assignments:
            if a.validated_at:
                try:
                    dt = datetime.strptime(a.validated_at, "%Y-%m-%d %H:%M:%S")
                    a.validated_date = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    a.validated_date = a.validated_at
        return assignments

    def get_user_mission_history(self, user_id: int) -> List[Assignment]:
        """
        Obté l'historial de missions finalitzades, rebutjades o cancel·lades d'un usuari, formatant la data.
        """
        assignments = self.mission_repo.get_user_mission_history(user_id)
        for a in assignments:
            # Utilitzar validated_at com a data principal si existeix, altrament completed_at
            date_str = a.validated_at or a.completed_at
            if date_str:
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    a.validated_date = dt.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    a.validated_date = date_str
            else:
                a.validated_date = "No disponible"
        return assignments

    def get_admin_personal_missions_summary(self, admin_id: int) -> dict:

        """
        Retorna el resum de les missions personals de l'administrador separat en:
        - pendents: missions pendents de fer
        - en_validacio: missions esperant validació
        - completades_avui: missions completades durant el dia d'avui
        """
        active_assignments = self.get_user_missions(admin_id)
        pending = [a for a in active_assignments if a.status == "pending"]
        waiting = [a for a in active_assignments if a.status == "waiting_validation"]

        history = self.get_user_mission_history(admin_id)
        today_str = datetime.now().strftime("%Y-%m-%d")
        completed_today = []
        for a in history:
            if a.status == "completed":
                date_str = a.validated_at or a.completed_at
                if date_str and date_str.startswith(today_str):
                    completed_today.append(a)

        return {
            "pending": pending,
            "waiting": waiting,
            "completed_today": completed_today,
            "pending_count": len(pending),
            "waiting_count": len(waiting),
            "completed_today_count": len(completed_today)
        }

    def start_mission(self, assignment_id: int, user_id: int) -> None:
        """
        Inicia l'execució d'una missió assignada (estat 'in_progress').
        """
        self.mission_repo.start_mission(assignment_id, user_id)

    def retry_rejected_mission(self, assignment_id: int, user_id: int) -> bool:
        """
        Torna una missió rebutjada a l'estat 'pending' per a permetre-li reintentar-la.
        """
        database.retry_rejected_mission(assignment_id, user_id)
        return True







    def get_waiting_validations(self) -> List[Assignment]:
        """
        Obté les assignacions esperant validació, calculant el temps passat
        des del seu completat de forma dinàmica.
        """
        waiting = self.mission_repo.get_waiting_validations()
        
        for assignment in waiting:
            if assignment.completed_at:
                try:
                    completed = datetime.strptime(
                        assignment.completed_at, 
                        "%Y-%m-%d %H:%M:%S"
                    )
                    delta = datetime.now() - completed
                    
                    if delta.days > 0:
                        assignment.time_ago = f"fa {delta.days} dies"
                    elif delta.seconds >= 3600:
                        assignment.time_ago = f"fa {delta.seconds//3600} h"
                    elif delta.seconds >= 60:
                        assignment.time_ago = f"fa {delta.seconds//60} min"
                    else:
                        assignment.time_ago = "ara mateix"
                        
                    assignment.completed_date = completed.strftime("%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    assignment.time_ago = "desconegut"
                    assignment.completed_date = assignment.completed_at
        
        return waiting



    def can_user_validate_assignment(self, validator_user: Optional[object], assignment: Optional[Assignment]) -> bool:
        """
        Comprova centralitzadament si un usuari té permís per a validar una assignació de missió.
        Permet afegir fàcilment nous rols en el futur sense modificar el flux de negoci principal.
        """
        if not validator_user or not assignment:
            return False

        if assignment.status != "waiting_validation":
            return False

        # L'usuari que ha realitzat/té assignada la missió no la pot validar manualment a ell mateix
        if validator_user.id == assignment.user_id:
            return False

        from services.user_service import UserService
        from services.family_config_service import FamilyConfigService

        owner_user = UserService().get_user_by_id(assignment.user_id)
        if not owner_user:
            return False

        config = FamilyConfigService().get_config(validator_user.family_id if hasattr(validator_user, 'family_id') else 1)

        # Si la missió és d'un nen/gamer, només la poden validar administradors
        if owner_user.role == "child":
            return validator_user.role == "admin"

        # Si la missió és d'un administrador (pare)
        if owner_user.role == "admin":
            if config.admin_validation_mode == "authorized_gamers":
                return validator_user.role in ("child", "admin")
            return validator_user.role == "admin"

        return False

    def get_waiting_validations_for_user(self, user_id: int) -> List[Assignment]:
        """
        Retorna les validacions pendents que un usuari específic té permís per a aprovar.
        """
        from services.user_service import UserService
        user = UserService().get_user_by_id(user_id)
        if not user:
            return []

        all_waiting = self.get_waiting_validations()
        return [a for a in all_waiting if self.can_user_validate_assignment(user, a)]


    def count_waiting_validations(self) -> int:
        """
        Compta el nombre d'assignacions pendents de validació.
        """
        return self.mission_repo.count_waiting_validations()

    def complete_mission(self, assignment_id: int, user_id: int) -> None:
        """
        Marca una assignació com a pendent de validació o l'aprova automàticament
        si la configuració auto_approve_admin_missions està activada per a usuaris administradors.
        """
        from services.user_service import UserService
        from services.family_config_service import FamilyConfigService
        user = UserService().get_user_by_id(user_id)
        config = FamilyConfigService().get_config(user.family_id if user else 1)

        self.mission_repo.complete_mission(assignment_id, user_id)

        if user and user.role == "admin" and config.auto_approve_admin_missions:
            self.approve_mission(assignment_id, user_id)


    def assign_mission(self, mission_id: int, user_id: int, assignment_type: str = "owner") -> int:
        """
        Assigna una missió a un usuari.
        """
        return self.mission_repo.assign_mission(mission_id, user_id, assignment_type)

    def approve_mission(self, assignment_id: int, admin_id: int) -> bool:
        """
        Aprova la missió assignada, incrementa els punts del gamer i en registra l'historial.
        """
        return self.mission_repo.approve_mission(assignment_id, admin_id)

    def reject_mission(self, assignment_id: int, reason: Optional[str] = None, admin_id: Optional[int] = None) -> None:
        """
        Rebutja la validació i passa l'assignació a 'rejected' amb el motiu especificat.
        """
        self.mission_repo.reject_mission(assignment_id, admin_id, reason)



    def update_mission(self, mission_id: int, data: dict) -> None:
        """
        Actualitza els detalls d'una missió.
        """
        self.mission_repo.update_mission(mission_id, data)

    def create_mission(self, data: dict, family_id: int = 1) -> int:
        """
        Crea una nova plantilla de missió per a una família i en retorna l'ID.
        """
        return self.mission_repo.create_mission(data, family_id)




