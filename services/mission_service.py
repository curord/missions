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
        Obté les assignacions de missions actives d'un usuari.
        """
        return self.mission_repo.get_user_missions(user_id)

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

    def reject_mission(self, assignment_id: int) -> None:
        """
        Rebutja la validació i torna l'estat de la missió assignada a pendent.
        """
        self.mission_repo.reject_mission(assignment_id)

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




