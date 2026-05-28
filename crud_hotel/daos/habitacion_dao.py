from database.connection import DatabaseConnection
from models.habitacion import Habitacion

class HabitacionDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_todas_habitaciones(self):
        """Consulta todas las habitaciones y su respectivo estado"""
        query = "SELECT * FROM habitacion ORDER BY numHabitacion"
        resultados = self.db.execute_read_query(query)
        
        habitaciones = []
        for r in resultados:
            hab = Habitacion(
                numHabitacion=r['numhabitacion'],
                categoria=r['categoria'],
                precioNoche=float(r['precionoche']),
                estadoActual=r['estadoactual']
            )
            habitaciones.append(hab)
        return habitaciones

    def get_habitaciones_disponibles(self):
        """Consulta disponibilidad (estado 'Disponible')"""
        query = "SELECT * FROM habitacion WHERE estadoActual = 'Disponible'"
        resultados = self.db.execute_read_query(query)
        
        habitaciones = []
        for r in resultados:
            hab = Habitacion(
                numHabitacion=r['numhabitacion'],
                categoria=r['categoria'],
                precioNoche=float(r['precionoche']),
                estadoActual=r['estadoactual']
            )
            habitaciones.append(hab)
        return habitaciones

    def update_estado_habitacion(self, num_habitacion: int, nuevo_estado: str):
        """Actualizar el estado de una habitación."""
        query = "UPDATE habitacion SET estadoActual = %s WHERE numHabitacion = %s"
        # Esto retornará None pero ejecutará el Update exitosamente a través del Single connection
        self.db.execute_write_query(query, (nuevo_estado, num_habitacion))
