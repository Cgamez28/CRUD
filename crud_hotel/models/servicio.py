from dataclasses import dataclass
from typing import Optional

@dataclass
class Servicio:
    idServicio: Optional[int]
    nombreServicio: str
    costo: float
    detalles: Optional[str] = None
