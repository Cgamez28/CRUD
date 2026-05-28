from dataclasses import dataclass
from datetime import datetime, date

@dataclass
class Consumo:
    fechaHoraConsumo: datetime
    idPersona: int
    numHabitacion: int
    fechaReserva: date
    idServicio: int
