from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Assignment:
    """
    Representa l'assignació d'una missió a un usuari concret.
    Fa el seguiment de l'estat (pending, waiting_validation, completed) i dels punts/monedes obtinguts.
    """

    mission_id: int
    user_id: int
    id: Optional[int] = None
    assignment_type: str = "owner"
    assigned_date: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "pending"
    completed_at: Optional[str] = None
    completed_by: Optional[int] = None
    validated_at: Optional[str] = None
    validated_by: Optional[int] = None
    comment: Optional[str] = None
    coins: int = 0
    completed_points: Optional[int] = None

    # Camps de suport per a consultes complexes amb JOIN
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    points: Optional[int] = None
    requires_validation: Optional[int] = None
    category: Optional[str] = None
    color: Optional[str] = None
    category_icon: Optional[str] = None
    completed_by_name: Optional[str] = None
    validated_by_name: Optional[str] = None
    gamer_name: Optional[str] = None
    time_ago: Optional[str] = None
    completed_date: Optional[str] = None


    @property
    def assignment_id(self) -> Optional[int]:
        """
        Àlies d'id utilitzat a les plantilles de la interfície.
        """
        return self.id

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la representació en diccionari de l'assignació.
        """
        res = asdict(self)
        # Assegurar que 'assignment_id' s'inclou al to_dict()
        res["assignment_id"] = self.assignment_id
        return res

    def __getitem__(self, key: str) -> Any:
        """
        Permet l'accés estil diccionari per a compatibilitat retroactiva.
        """
        if key == "assignment_id":
            return self.assignment_id
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retorna un valor de camp o el valor per defecte si no existeix.
        """
        if key == "assignment_id":
            return self.assignment_id
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        """
        Comprova si el camp existeix en la instància.
        """
        return key == "assignment_id" or hasattr(self, key)

    def keys(self) -> Any:
        return self.to_dict().keys()

    def values(self) -> Any:
        return self.to_dict().values()

    def items(self) -> Any:
        return self.to_dict().items()

