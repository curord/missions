from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Mission:
    """
    Representa una plantilla de missió configurable.
    Defineix la recompensa en XP i monedes, la dificultat i les regles de validació.
    """

    family_id: int
    category_id: int
    title: str
    id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    mission_type_id: Optional[int] = None
    difficulty: int = 1
    estimated_minutes: Optional[int] = None
    points: int = 10
    xp: int = 0
    requires_validation: int = 0
    repeat_type: str = "none"
    coins: int = 0
    repeat_same_day: int = 0
    expire_action: str = "cancel"
    color: Optional[str] = None
    sort_order: int = 0
    active: int = 1
    created_at: Optional[str] = None

    # Camps virtuals afegits per consultes amb JOIN
    category_name: Optional[str] = None
    category_icon: Optional[str] = None
    category_color: Optional[str] = None
    mission_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la representació en diccionari de la missió.
        """
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        """
        Permet l'accés estil diccionari per a compatibilitat retroactiva.
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retorna un valor de camp o el valor per defecte si no existeix.
        """
        return getattr(self, key, default)

    def __contains__(self, key: str) -> bool:
        """
        Comprova si el camp existeix en la instància.
        """
        return hasattr(self, key)

    def keys(self) -> Any:
        return self.to_dict().keys()

    def values(self) -> Any:
        return self.to_dict().values()

    def items(self) -> Any:
        return self.to_dict().items()

