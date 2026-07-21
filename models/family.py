from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class Family:
    """
    Representa una família dins del sistema de missions.
    Una família agrupa administradors (pares) i gamers (nens).
    """

    name: str
    id: Optional[int] = None
    created_at: Optional[str] = None
    active: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la representació en diccionari de la família.
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

