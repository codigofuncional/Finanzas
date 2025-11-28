import sqlite3
import os

# --- CLASE PRINCIPAL DE LA BASE DE DATOS ---

class GestorFinanzasDB:
    """
    Clase que maneja toda la lógica de conexión y 
    operaciones (CRUD) con la base de datos de finanzas.
    """
    def __init__(self, nombre_db="finanzas_personales.db"):
        """
        Método constructor: se ejecuta al crear un objeto de esta clase.
        Define el nombre del archivo de la DB y la inicializa.
        """
        self.nombre_db = nombre_db
        self.inicializar_db() 

    def conectar(self):
        """Método para crear la conexión a la base de datos."""
        return sqlite3.connect(self.nombre_db)

    def crear_tabla(self):
        """Crea la tabla 'transacciones' si no existe."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        sql_crear_tabla = """
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL,
            monto REAL NOT NULL,
            tipo TEXT NOT NULL  -- Puede ser 'INGRESO' o 'GASTO'
        )
        """
        cursor.execute(sql_crear_tabla)
        conexion.commit()
        conexion.close()

    def inicializar_db(self):
        """Función principal para inicializar la base de datos."""
        self.crear_tabla()
        print(f"✅ Base de datos '{self.nombre_db}' inicializada/verificada.")

    def insertar_transaccion(self, fecha, descripcion, monto, tipo):
        """Inserta una nueva transacción."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        sql_insertar = """
        INSERT INTO transacciones (fecha, descripcion, monto, tipo) 
        VALUES (?, ?, ?, ?)
        """
        try:
            cursor.execute(sql_insertar, (fecha, descripcion, monto, tipo))
            conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"❌ Error al guardar la transacción: {e}")
            return False
        finally:
            conexion.close()

    def obtener_transacciones(self):
        """Devuelve todas las transacciones de la base de datos, ordenadas por fecha."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        sql_select = "SELECT id, fecha, descripcion, monto, tipo FROM transacciones ORDER BY fecha DESC"
        cursor.execute(sql_select)
        transacciones = cursor.fetchall()
        conexion.close()
        return transacciones

    def eliminar_transaccion(self, id_transaccion):
        """Elimina una transacción por su ID."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        sql_delete = "DELETE FROM transacciones WHERE id = ?"
        try:
            cursor.execute(sql_delete, (id_transaccion,))
            conexion.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"❌ Error al eliminar la transacción: {e}")
            return False
        finally:
            conexion.close()

    def obtener_saldo_total(self):
        """Calcula el saldo total, ingresos y gastos."""
        conexion = self.conectar()
        cursor = conexion.cursor()
        
        # Consulta para sumar todos los ingresos
        sql_ingresos = "SELECT SUM(monto) FROM transacciones WHERE tipo = 'INGRESO'"
        cursor.execute(sql_ingresos)
        ingresos = cursor.fetchone()[0] or 0.0 # Si es NULL, es 0
        
        # Consulta para sumar todos los gastos
        sql_gastos = "SELECT SUM(monto) FROM transacciones WHERE tipo = 'GASTO'"
        cursor.execute(sql_gastos)
        gastos = cursor.fetchone()[0] or 0.0 # Si es NULL, es 0
        
        conexion.close()
        
        saldo = ingresos - gastos
        
        return saldo, ingresos, gastos

# --- BLOQUE DE PRUEBA (Se mantiene para verificar la funcionalidad de la clase) ---
if __name__ == "__main__":
    print("--- INICIANDO GESTOR DE FINANZAS DB ---")
    db_manager = GestorFinanzasDB()