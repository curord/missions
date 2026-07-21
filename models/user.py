from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class User:
    """
    Representa un usuari del sistema (pare/administrador o nen/gamer).
    Conté informació sobre punts, nivell i gamificació.
    """

    family_id: int
    name: str
    role: str  # 'admin' o 'child'
    id: Optional[int] = None
    avatar: Optional[str] = None
    favorite_color: Optional[str] = None
    theme: str = "default"
    points: int = 0
    level: int = 1
    birthdate: Optional[str] = None
    last_login: Optional[str] = None
    active: int = 1
    created_at: Optional[str] = None

    # Camps virtuals/gamificació calculats
    streak: int = 0
    level_progress: int = 0
    coins: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la representació en diccionari de l'usuari.
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

