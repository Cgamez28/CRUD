from dataclasses import dataclass
from .persona import Persona

@dataclass
class Empleado(Persona):
    """
    Hereda de Persona.
    Representa la tabla 'empleado' que enlaza con 'persona' vía 'idPersona'.
    Añade los atributos específicos del empleado.
    """
    cargo: str = ""
    idArea: int = 0
