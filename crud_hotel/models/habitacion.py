from dataclasses import dataclass

@dataclass
class Habitacion:
    numHabitacion: int
    categoria: str
    precioNoche: float
    estadoActual: str = 'Disponible'
