from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Persona:
    idPersona: Optional[int]
    primerNom: str
    primerApell: str
    fechaNac: date
    segundoNom: Optional[str] = None
    segundoApell: Optional[str] = None
    calle: Optional[str] = None
    carrera: Optional[str] = None
    complemento: Optional[str] = None
    correo: Optional[str] = None
    telefonos: Optional[str] = None
