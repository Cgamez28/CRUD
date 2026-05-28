from database.connection import DatabaseConnection
from models.consumo import Consumo
from datetime import datetime, date

class ConsumoDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_consumo(self, consumo: Consumo):
        """Registro de un Consumo basado en la Clave Primaria compuesta de la reserva."""
        query = """
            INSERT INTO consumo 
            (fechaHoraConsumo, idPersona, numHabitacion, fechaReserva, idServicio)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            consumo.fechaHoraConsumo, consumo.idPersona, consumo.numHabitacion,
            consumo.fechaReserva, consumo.idServicio
        )
        self.db.execute_write_query(query, params)

    def consultar_consumos_por_reserva(self, id_persona: int, num_habitacion: int, fecha_reserva: date):
        """Devuelve los consumos asociados a una reserva en específico."""
        query = """
            SELECT * FROM consumo 
            WHERE idPersona = %s AND numHabitacion = %s AND fechaReserva = %s
        """
        params = (id_persona, num_habitacion, fecha_reserva)
        resultados = self.db.execute_read_query(query, params)
        consumos = []
        for r in resultados:
            c = Consumo(
                fechaHoraConsumo=r['fechahoraconsumo'],
                idPersona=r['idpersona'],
                numHabitacion=r['numhabitacion'],
                fechaReserva=r['fechareserva'],
                idServicio=r['idservicio']
            )
            consumos.append(c)
        return consumos

    def actualizar_consumo(self, consumo: Consumo, old_fecha_hora: datetime):
        """
        Actualiza el idServicio o la fechaHoraConsumo. 
        Al ser parte de la PK, necesitamos la 'old_fecha_hora' para ubicar el registro exacto.
        """
        query = """
            UPDATE consumo 
            SET fechaHoraConsumo = %s, idServicio = %s
            WHERE fechaHoraConsumo = %s AND idPersona = %s AND numHabitacion = %s AND fechaReserva = %s
        """
        params = (
            consumo.fechaHoraConsumo, consumo.idServicio,
            old_fecha_hora, consumo.idPersona, consumo.numHabitacion, consumo.fechaReserva
        )
        self.db.execute_write_query(query, params)

    def eliminar_consumo(self, fecha_hora: datetime, id_persona: int, num_habitacion: int, fecha_reserva: date):
        """Elimina el registro validando su cuádruple PK."""
        query = """
            DELETE FROM consumo 
            WHERE fechaHoraConsumo = %s AND idPersona = %s AND numHabitacion = %s AND fechaReserva = %s
        """
        params = (fecha_hora, id_persona, num_habitacion, fecha_reserva)
        self.db.execute_write_query(query, params)
