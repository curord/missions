from datetime import datetime
from typing import List, Optional
from models.mission import Mission
from models.assignment import Assignment
from models.category import Category
from repositories.mission_repository import MissionRepository


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

    def count_waiting_validations(self) -> int:
        """
        Compta el nombre d'assignacions pendents de validació.
        """
        return self.mission_repo.count_waiting_validations()

    def complete_mission(self, assignment_id: int, user_id: int) -> None:
        """
        Marca una assignació com a pendent de validació.
        """
        self.mission_repo.complete_mission(assignment_id, user_id)

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

    def reject_mission(self, assignment_id: int, reason: Optional[str] = None) -> None:
        """
        Rebutja la validació i passa l'assignació a 'rejected' amb el motiu especificat.
        """
        self.mission_repo.reject_mission(assignment_id, reason)


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




