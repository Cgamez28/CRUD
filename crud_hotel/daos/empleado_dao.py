from database.connection import DatabaseConnection
from models.empleado import Empleado

class EmpleadoDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_empleado(self, empleado: Empleado, num_telefono: str = None) -> int:
        """
        Inserta datos en persona con RETURNING idPersona,
        luego inserta ese ID en empleado y, si se provee, en telefono transaccionalmente.
        """
        query_persona = """
            INSERT INTO persona 
            (primerNom, segundoNom, primerApell, segundoApell, calle, carrera, complemento, correo, fechaNac) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING idPersona
        """
        params_persona = (
            empleado.primerNom, empleado.segundoNom, empleado.primerApell, empleado.segundoApell,
            empleado.calle, empleado.carrera, empleado.complemento, empleado.correo, empleado.fechaNac
        )
        
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            # 1. Tabla Persona
            cursor.execute(query_persona, params_persona)
            id_persona_generado = cursor.fetchone()[0]
            
            # 2. Tabla Empleado
            query_empleado = "INSERT INTO empleado (idPersona, cargo, idArea) VALUES (%s, %s, %s)"
            cursor.execute(query_empleado, (id_persona_generado, empleado.cargo, empleado.idArea))
            
            # 3. Tabla Telefono
            if num_telefono:
                query_telefono = "INSERT INTO telefono (idPersona, numTelefono) VALUES (%s, %s)"
                cursor.execute(query_telefono, (id_persona_generado, num_telefono))
            
            conn.commit()
            empleado.idPersona = id_persona_generado
            return id_persona_generado
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def actualizar_empleado(self, empleado: Empleado):
        """Actualiza los datos del empleado. Como abarca dos tablas, lo hace transaccionalmente."""
        query_persona = """
            UPDATE persona 
            SET primerNom = %s, segundoNom = %s, primerApell = %s, segundoApell = %s,
                calle = %s, carrera = %s, complemento = %s, correo = %s, fechaNac = %s
            WHERE idPersona = %s
        """
        params_persona = (
            empleado.primerNom, empleado.segundoNom, empleado.primerApell, empleado.segundoApell,
            empleado.calle, empleado.carrera, empleado.complemento, empleado.correo, empleado.fechaNac,
            empleado.idPersona
        )

        query_empleado = "UPDATE empleado SET cargo = %s, idArea = %s WHERE idPersona = %s"
        params_empleado = (empleado.cargo, empleado.idArea, empleado.idPersona)

        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query_persona, params_persona)
            cursor.execute(query_empleado, params_empleado)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def obtener_empleados(self):
        """Devuelve todos los empleados con sus datos de persona y teléfonos."""
        query = """
            SELECT p.*, e.cargo, e.idArea, string_agg(t.numTelefono, ', ') as telefonos
            FROM persona p
            INNER JOIN empleado e ON p.idPersona = e.idPersona
            LEFT JOIN telefono t ON p.idPersona = t.idPersona
            GROUP BY p.idPersona, e.cargo, e.idArea
            ORDER BY p.idPersona
        """
        resultados = self.db.execute_read_query(query)
        empleados = []
        for r in resultados:
            emp = Empleado(
                idPersona=r['idpersona'],
                primerNom=r['primernom'],
                segundoNom=r.get('segundonom'),
                primerApell=r['primerapell'],
                segundoApell=r.get('segundoapell'),
                calle=r.get('calle'),
                carrera=r.get('carrera'),
                complemento=r.get('complemento'),
                correo=r.get('correo'),
                telefonos=r.get('telefonos'),
                fechaNac=r['fechanac'],
                cargo=r['cargo'],
                idArea=r['idarea']
            )
            empleados.append(emp)
        return empleados
