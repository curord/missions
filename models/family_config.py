from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional


@dataclass
class FamilyConfig:
    """
    Representa els paràmetres de configuració d'una família.
    """

    family_id: int
    auto_approve_admin_missions: bool = False
    rewards_require_delivery: bool = True
    count_weekends_streaks: bool = True
    admin_validation_mode: str = "admin_only"
    updated_at: Optional[str] = None


    def to_dict(self) -> Dict[str, Any]:
        """
        Retorna la representació en diccionari de la configuració.
        """
        return asdict(self)

    def __getitem__(self, key: str) -> Any:
        """
        Permet l'accés estil diccionari per a compatibilitat.
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
        Comprova si el camp existeix a la instància.
        """
        return hasattr(self, key)

    def keys(self) -> Any:
        return self.to_dict().keys()

    def values(self) -> Any:
        return self.to_dict().values()

    def items(self) -> Any:
        return self.to_dict().items()
