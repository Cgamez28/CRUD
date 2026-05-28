from datetime import datetime, date
from models.consumo import Consumo
from daos.consumo_dao import ConsumoDAO
from daos.habitacion_dao import HabitacionDAO
from daos.servicio_dao import ServicioDAO

class ServicioController:
    """
    Controlador para el personal de servicio/room service/mantenimiento.
    Permite alterar los bloques de estado sin crear reservas y enviar cobros a las cuentas del huésped.
    """
    
    def __init__(self):
        self.consumo_dao = ConsumoDAO()
        self.habitacion_dao = HabitacionDAO()
        self.servicio_dao = ServicioDAO()

    def obtener_habitaciones(self):
        """Obtiene las habitaciones para listar en su estado actual."""
        return self.habitacion_dao.get_todas_habitaciones()

    def obtener_servicios(self):
        """Obtiene los servicios disponibles para el menú desplegable."""
        return self.servicio_dao.consultar_servicios()

    def cambiar_estado_habitacion(self, num_habitacion: int, nuevo_estado: str):
        """
        Ej: Personal de limpieza marca una habitación ocupada como 'Mantenimiento' al encontrar un defecto,
        o como 'Disponible' tras limpiarla luego del check-out.
        """
        estados_validos = ['Disponible', 'Ocupada', 'Reservada', 'Mantenimiento']
        if nuevo_estado not in estados_validos:
            raise ValueError(f"Estado '{nuevo_estado}' no permitido en las reglas de dominio.")
            
        self.habitacion_dao.update_estado_habitacion(num_habitacion, nuevo_estado)

    def registrar_consumo_extra(self, id_persona: int, num_habitacion: int, fecha_reserva: date, id_servicio: int):
        """
        Registra un cargo (como Room Service o SPA) a la llave compuesta de una reserva activa.
        """
        # Validación de que el servicio existe
        servicios_disponibles = self.servicio_dao.consultar_servicios()
        if not any(s.idServicio == id_servicio for s in servicios_disponibles):
            raise ValueError("El servicio solicitado no existe en el catálogo del hotel.")
            
        nuevo_consumo = Consumo(
            fechaHoraConsumo=datetime.now(),
            idPersona=id_persona,
            numHabitacion=num_habitacion,
            fechaReserva=fecha_reserva,
            idServicio=id_servicio
        )
        
        self.consumo_dao.insertar_consumo(nuevo_consumo)
        return nuevo_consumo
