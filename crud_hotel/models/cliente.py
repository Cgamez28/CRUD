from dataclasses import dataclass
from .persona import Persona

@dataclass
class Cliente(Persona):
    """
    Hereda de Persona. 
    A nivel de Base de Datos es una entidad con FK (idPersona), 
    pero a nivel de aplicación hereda todos los datos para mayor comodidad.
    """
    pass
