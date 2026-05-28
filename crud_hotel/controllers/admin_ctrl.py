from daos.empleado_dao import EmpleadoDAO
from daos.servicio_dao import ServicioDAO
from database.connection import DatabaseConnection
from models.empleado import Empleado
from models.servicio import Servicio

class AdminController:
    """
    Controlador exclusivo para los Gerentes/Admin.
    Permite visualizar finanzas, añadir empleados, o cambiar precios del catálogo matriz.
    """
    
    def __init__(self):
        self.empleado_dao = EmpleadoDAO()
        self.servicio_dao = ServicioDAO()
        self.db = DatabaseConnection() # Requerido para lanzar reportes complejos vía consultas SQL Custom

    # ==========================
    # GESTIÓN DE CATÁLOGO (SERVICIOS)
    # ==========================
    def agregar_nuevo_servicio(self, nombre: str, detalles: str, costo: float) -> Servicio:
        if costo <= 0:
            raise ValueError("El costo de un servicio en el hotel no puede ser 0 o menor")
            
        srv = Servicio(idServicio=None, nombreServicio=nombre, detalles=detalles, costo=costo)
        self.servicio_dao.insertar_servicio(srv)
        return srv

    # ==========================
    # GESTIÓN DE RRHH (EMPLEADOS)
    # ==========================
    def obtener_todos_empleados(self):
        """Devuelve la lista completa de empleados activos."""
        return self.empleado_dao.obtener_empleados()

    def contratar_empleado(self, datos_empleado: dict, cargo: str, id_area: int) -> Empleado:
        # Reutilizamos el modelo y DAO de empleado que ya hace doble registro en Persona -> Empleado
        nuevo_empleado = Empleado(
            idPersona=None,
            primerNom=datos_empleado['primerNom'],
            segundoNom=datos_empleado.get('segundoNom'),
            primerApell=datos_empleado['primerApell'],
            segundoApell=datos_empleado.get('segundoApell'),
            calle=datos_empleado.get('calle'),
            carrera=datos_empleado.get('carrera'),
            complemento=datos_empleado.get('complemento'),
            correo=datos_empleado.get('correo'),
            fechaNac=datos_empleado['fechaNac'],
            cargo=cargo,
            idArea=id_area
        )
        telefono_opcional = datos_empleado.get('telefono')
        
        id_generado = self.empleado_dao.insertar_empleado(nuevo_empleado, telefono_opcional)
        nuevo_empleado.idPersona = id_generado
        nuevo_empleado.telefonos = telefono_opcional
        return nuevo_empleado

    # ==========================
    # REPORTES ESTADÍSTICOS
    # ==========================
    def reporte_clientes_frecuentes(self):
        """
        Calcula qué clientes tienen mayor sumatoria económica y un recuento
        de sus reservaciones. Utiliza una SQL limpia debido a que es un reporte de agregación cruzada.
        """
        query = """
            SELECT 
                p.primerNom,
                p.primerApell,
                COUNT(r.numHabitacion) as total_reservas,
                SUM(r.valorReserva) as valor_historico_dejado
            FROM reserva r
            JOIN persona p ON r.idPersona = p.idPersona
            GROUP BY p.idPersona, p.primerNom, p.primerApell
            ORDER BY valor_historico_dejado DESC
        """
        # Ya que esto es un consolidado, usamos el diccionario RealDictCursor base
        return self.db.execute_read_query(query)

    def reporte_ocupacion(self):
        """Muestra el total de habitaciones por categoría filtradas por estado"""
        query = """
            SELECT categoria, estadoActual, COUNT(*) as cantidad
            FROM habitacion
            GROUP BY categoria, estadoActual
            ORDER BY categoria, estadoActual
        """
        return self.db.execute_read_query(query)
