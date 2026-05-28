from datetime import date
from models.cliente import Cliente
from models.reserva import Reserva
from daos.cliente_dao import ClienteDAO
from daos.reserva_dao import ReservaDAO
from daos.habitacion_dao import HabitacionDAO

class RecepcionController:
    """
    Controlador para el recepcionista.
    Encargado de manejar flujo de clientes, estado base de habitaciones y asignaciones (Reservas).
    """
    
    def __init__(self):
        self.cliente_dao = ClienteDAO()
        self.reserva_dao = ReservaDAO()
        self.habitacion_dao = HabitacionDAO()

    def registrar_cliente(self, datos_cliente: dict) -> Cliente:
        """
        Recibe un diccionario con los datos del formulario de la UI y los pasa al DAO.
        Retorna la instancia del Cliente creado.
        """
        nuevo_cliente = Cliente(
            idPersona=None,
            primerNom=datos_cliente['primerNom'],
            segundoNom=datos_cliente.get('segundoNom'),
            primerApell=datos_cliente['primerApell'],
            segundoApell=datos_cliente.get('segundoApell'),
            calle=datos_cliente.get('calle'),
            carrera=datos_cliente.get('carrera'),
            complemento=datos_cliente.get('complemento'),
            correo=datos_cliente.get('correo'),
            fechaNac=datos_cliente['fechaNac']
        )
        telefono_opcional = datos_cliente.get('telefono')
        
        # Validar edad lógica (opcional)
        hoy = date.today()
        if nuevo_cliente.fechaNac > hoy:
            raise ValueError("La fecha de nacimiento no puede estar en el futuro.")

        # Pasamos el teléfono al DAO para que se incorpore a la misma transacción
        id_generado = self.cliente_dao.insertar_cliente(nuevo_cliente, telefono_opcional)
        nuevo_cliente.idPersona = id_generado
        nuevo_cliente.telefonos = telefono_opcional
        return nuevo_cliente

    def obtener_clientes(self):
        """Obtiene la lista de todos los clientes registrados."""
        return self.cliente_dao.obtener_clientes()

    def ver_estado_habitaciones(self):
        """Devuelve un listado completo para el panel central de recepción"""
        return self.habitacion_dao.get_todas_habitaciones()

    def crear_reserva(self, id_cliente: int, num_habitacion: int, fecha_llegada: date, fecha_salida: date, valor: float) -> Reserva:
        """
        Intenta realizar una reserva en la fecha indicada.
        Realiza la validación de negocio cruzando estados.
        """
        # Regla 1: Fechas con sentido
        if fecha_llegada > fecha_salida:
            raise ValueError("La fecha de llegada no puede ser posterior a la fecha de salida")
            
        # Regla 2: Validar si la habitación está realmente "Disponible" ahora mismo
        todas = self.habitacion_dao.get_todas_habitaciones()
        hab = next((h for h in todas if h.numHabitacion == num_habitacion), None)
        
        if not hab:
            raise ValueError("La habitación indicada no existe.")
            
        if hab.estadoActual != 'Disponible':
            raise ValueError(f"No se puede reservar. El estado de la habitación {num_habitacion} es {hab.estadoActual}.")

        # Si pasa las validaciones, creamos el modelo
        reserva = Reserva(
            idPersona=id_cliente,
            numHabitacion=num_habitacion,
            fechaReserva=date.today(), # La reserva se asienta hoy
            fechaLlegada=fecha_llegada,
            fechaSalida=fecha_salida,
            valorReserva=valor,
            tiempoMaxCancelacion=24
        )
        
        # Guardamos a BBDD
        self.reserva_dao.insertar_reserva(reserva)
        
        # Cambiamos su estado en BBDD a "Reservada" (o "Ocupada" si el check-in es hoy mismo)
        nuevo_estado = 'Ocupada' if fecha_llegada == date.today() else 'Reservada'
        self.habitacion_dao.update_estado_habitacion(num_habitacion, nuevo_estado)
        
        return reserva
