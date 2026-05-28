from database.connection import DatabaseConnection
from models.cliente import Cliente

class ClienteDAO:
    def __init__(self):
        self.db = DatabaseConnection()

    def insertar_cliente(self, cliente: Cliente, num_telefono: str = None) -> int:
        """
        Inserta datos en persona con RETURNING idPersona,
        luego inserta ese ID en cliente y, si se provee, el teléfono en la tabla telefono,
        todo de manera transaccional.
        """
        # 1. Inserción en tabla Persona
        query_persona = """
            INSERT INTO persona 
            (primerNom, segundoNom, primerApell, segundoApell, calle, carrera, complemento, correo, fechaNac) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING idPersona
        """
        params_persona = (
            cliente.primerNom, cliente.segundoNom, cliente.primerApell, cliente.segundoApell,
            cliente.calle, cliente.carrera, cliente.complemento, cliente.correo, cliente.fechaNac
        )
        
        # Como es una transacción manual donde usamos el ID, abrimos conexión y controlamos explícitamente:
        conn = self.db._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query_persona, params_persona)
            id_persona_generado = cursor.fetchone()[0]
            
            # 2. Inserción en tabla Cliente
            query_cliente = "INSERT INTO cliente (idPersona) VALUES (%s)"
            cursor.execute(query_cliente, (id_persona_generado,))
            
            # 3. Inserción en tabla Telefono (si hay)
            if num_telefono:
                query_telefono = "INSERT INTO telefono (idPersona, numTelefono) VALUES (%s, %s)"
                cursor.execute(query_telefono, (id_persona_generado, num_telefono))
            
            conn.commit()
            cliente.idPersona = id_persona_generado
            return id_persona_generado
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def actualizar_cliente(self, cliente: Cliente):
        """
        Actualiza los datos de la Persona asociada a este Cliente.
        """
        query = """
            UPDATE persona 
            SET primerNom = %s, segundoNom = %s, primerApell = %s, segundoApell = %s,
                calle = %s, carrera = %s, complemento = %s, correo = %s, fechaNac = %s
            WHERE idPersona = %s
        """
        params = (
            cliente.primerNom, cliente.segundoNom, cliente.primerApell, cliente.segundoApell,
            cliente.calle, cliente.carrera, cliente.complemento, cliente.correo, cliente.fechaNac,
            cliente.idPersona
        )
        self.db.execute_write_query(query, params)

    def obtener_clientes(self):
        """Devuelve todos los clientes con sus datos de persona y teléfonos agregados."""
        query = """
            SELECT p.*, string_agg(t.numTelefono, ', ') as telefonos
            FROM persona p
            INNER JOIN cliente c ON p.idPersona = c.idPersona
            LEFT JOIN telefono t ON p.idPersona = t.idPersona
            GROUP BY p.idPersona
            ORDER BY p.idPersona
        """
        resultados = self.db.execute_read_query(query)
        clientes = []
        for r in resultados:
            c = Cliente(
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
                fechaNac=r['fechanac']
            )
            clientes.append(c)
        return clientes
