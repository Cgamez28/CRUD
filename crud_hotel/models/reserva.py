from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Reserva:
    idPersona: int
    numHabitacion: int
    fechaReserva: date
    fechaLlegada: date
    fechaSalida: date
    valorReserva: float
    tiempoMaxCancelacion: int = 24
