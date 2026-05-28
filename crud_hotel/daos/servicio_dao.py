from database.connection import DatabaseConnection
from models.servicio import Servicio

class ServicioDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_servicio(self, servicio: Servicio):
        query = "INSERT INTO servicio (nombreServicio, detalles, costo) VALUES (%s, %s, %s)"
        params = (servicio.nombreServicio, servicio.detalles, servicio.costo)
        self.db.execute_write_query(query, params)

    def consultar_servicios(self):
        query = "SELECT * FROM servicio"
        resultados = self.db.execute_read_query(query)
        servicios = []
        for r in resultados:
            srv = Servicio(
                idServicio=r['idservicio'],
                nombreServicio=r['nombreservicio'],
                detalles=r.get('detalles'),
                costo=float(r['costo'])
            )
            servicios.append(srv)
        return servicios

    def actualizar_servicio(self, servicio: Servicio):
        query = "UPDATE servicio SET nombreServicio = %s, detalles = %s, costo = %s WHERE idServicio = %s"
        params = (servicio.nombreServicio, servicio.detalles, servicio.costo, servicio.idServicio)
        self.db.execute_write_query(query, params)

    def eliminar_servicio(self, id_servicio: int):
        query = "DELETE FROM servicio WHERE idServicio = %s"
        self.db.execute_write_query(query, (id_servicio,))
