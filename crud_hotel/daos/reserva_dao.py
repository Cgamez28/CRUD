from database.connection import DatabaseConnection
from models.reserva import Reserva
from datetime import date

class ReservaDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_reserva(self, reserva: Reserva):
        """Inserta una nueva reserva en base a su PK compuesta."""
        query = """
            INSERT INTO reserva 
            (idPersona, numHabitacion, fechaReserva, fechaLlegada, fechaSalida, valorReserva, tiempoMaxCancelacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            reserva.idPersona, reserva.numHabitacion, reserva.fechaReserva,
            reserva.fechaLlegada, reserva.fechaSalida, reserva.valorReserva,
            reserva.tiempoMaxCancelacion
        )
        self.db.execute_write_query(query, params)

    def consultar_reservas(self):
        """Consulta todas las reservas con toda su PK compuesta."""
        query = "SELECT * FROM reserva"
        resultados = self.db.execute_read_query(query)
        reservas = []
        for r in resultados:
            res = Reserva(
                idPersona=r['idpersona'],
                numHabitacion=r['numhabitacion'],
                fechaReserva=r['fechareserva'],
                fechaLlegada=r['fechallegada'],
                fechaSalida=r['fechasalida'],
                valorReserva=float(r['valorreserva']),
                tiempoMaxCancelacion=r.get('tiempomaxcancelacion', 24)
            )
            reservas.append(res)
        return reservas

    def actualizar_reserva(self, reserva_actualizada: Reserva, old_fecha_reserva: date):
        """
        Actualiza una reserva. Requiere la PK original para lograrlo, dado que
        el usuario podría haber actualizado campos como `fechaReserva` o incluso la PK entera.
        """
        query = """
            UPDATE reserva 
            SET idPersona = %s, numHabitacion = %s, fechaReserva = %s, 
                fechaLlegada = %s, fechaSalida = %s, valorReserva = %s, tiempoMaxCancelacion = %s
            WHERE idPersona = %s AND numHabitacion = %s AND fechaReserva = %s
        """
        params = (
            reserva_actualizada.idPersona, reserva_actualizada.numHabitacion, reserva_actualizada.fechaReserva,
            reserva_actualizada.fechaLlegada, reserva_actualizada.fechaSalida, reserva_actualizada.valorReserva,
            reserva_actualizada.tiempoMaxCancelacion,
            # PK Antigua explícita para la cláusula WHERE:
            reserva_actualizada.idPersona, reserva_actualizada.numHabitacion, old_fecha_reserva
        )
        self.db.execute_write_query(query, params)

    def eliminar_reserva(self, id_persona: int, num_habitacion: int, fecha_reserva: date):
        """Borra usando strict match con su Clave Primaria Compuesta."""
        query = "DELETE FROM reserva WHERE idPersona = %s AND numHabitacion = %s AND fechaReserva = %s"
        params = (id_persona, num_habitacion, fecha_reserva)
        self.db.execute_write_query(query, params)
