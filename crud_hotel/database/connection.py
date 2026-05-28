import os
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

class DatabaseConnection:
    """
    Clase Singleton para gestionar la conexión a la base de datos PostgreSQL.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def _get_connection(self):
        """Inicializa la conexión si no existe."""
        if self._connection is None or self._connection.closed:
            try:
                # Usamos variables de entorno con defaults basados en "hotel_gestion"
                self._connection = psycopg2.connect(
                    host=os.getenv("DB_HOST", "localhost"),
                    database=os.getenv("DB_NAME", "hotel_gestion"),
                    user=os.getenv("DB_USER", "postgres"),
                    password=os.getenv("DB_PASSWORD", "12345"), # Cambiar según local
                    port=os.getenv("DB_PORT", "5432"),
                    client_encoding="UTF8"
                )
            except Error as e:
                print(f"Error al conectar a la base de datos: {e}")
                raise e
        return self._connection

    def close(self):
        """Cierra la conexión activa."""
        if self._connection and not self._connection.closed:
            self._connection.close()
            self._connection = None

    def execute_read_query(self, query, params=None):
        """
        Ejecuta consultas de tipo SELECT.
        Devuelve los resultados como una lista de diccionarios.
        """
        connection = self._get_connection()
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            # Convertimos a listas de diccionarios normales para no ligar al controlador con RealDictRow
            return [dict(row) for row in results]
        except Error as e:
            print(f"Error en ejecución de lectura: {e}")
            raise e
        finally:
            if cursor:
                cursor.close()

    def execute_write_query(self, query, params=None):
        """
        Ejecuta consultas de tipo INSERT, UPDATE, o DELETE.
        Implementa commit/rollback para garantizar la transaccionalidad.
        Si la query utiliza cláusula RETURNING, devolverá la fila o el valor generado.
        """
        connection = self._get_connection()
        cursor = None
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            connection.commit()
            
            # En caso que haya datos retornables (ej. RETURNING idPersona)
            try:
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
            except psycopg2.ProgrammingError:
                # Ocurre si la consulta no devuelve datos (INSERT/UPDATE/DELETE tradicional)
                return None

        except Error as e:
            connection.rollback()
            print(f"Error en ejecución de escritura (Rollback realizado): {e}")
            raise e
        finally:
            if cursor:
                cursor.close()
