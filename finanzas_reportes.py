import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import os

# Importamos la clase que ya creaste para manejar la DB
from finanzas_db import GestorFinanzasDB 

# --- FUNCIÓN 1: OBTENER DATOS Y CONVERTIR A DATAFRAME ---

def generar_reporte_pandas():
    """
    Función que lee todas las transacciones de SQLite 
    y las convierte en un DataFrame de Pandas.
    """
    
    # Creamos el objeto de la DB
    db_manager = GestorFinanzasDB()
    
    try:
        # Conexión directa a la base de datos
        conexion = db_manager.conectar()
        
        # Leemos la tabla 'transacciones' directamente a un DataFrame de Pandas
        df = pd.read_sql_query("SELECT * FROM transacciones", conexion)
        
        conexion.close()
        
        # Renombramos las columnas para que Pandas las use más fácilmente
        df.columns = ['id', 'fecha', 'descripcion', 'monto', 'tipo']
        
        return df
        
    except Exception as e:
        print(f"❌ Error en generar_reporte_pandas: {e}")
        # Retornamos un DataFrame vacío en caso de error
        return pd.DataFrame()


# --- FUNCIÓN 2: GENERAR EL GRÁFICO CON MATPLOTLIB ---

def visualizar_resumen(df):
    """
    Toma el DataFrame de Pandas y genera el gráfico de barras con Matplotlib.
    """
    
    # Agrupamos los datos por 'tipo' (INGRESO/GASTO) y sumamos los montos
    resumen_tipo = df.groupby('tipo')['monto'].sum()
    
    if resumen_tipo.empty:
        # Esto solo debería pasar si la base de datos está vacía
        print("No hay datos para visualizar.")
        return

    # 1. Configuración del Gráfico
    plt.figure(figsize=(8, 6))
    
    # 2. Creación del Gráfico
    # Usamos colores personalizados: Rojo para GASTO, Verde para INGRESO
    colores = []
    
    # Aseguramos el orden y color de las barras (muy importante)
    if 'GASTO' in resumen_tipo.index:
        colores.append('#FF6347') # Rojo
    if 'INGRESO' in resumen_tipo.index:
        colores.append('#3CB371') # Verde

    # Creación de las barras. Pandas usa Matplotlib internamente
    resumen_tipo.plot(kind='bar', color=colores) 
    
    # 3. Etiquetas y Estilo
    plt.title('Resumen de Ingresos vs. Gastos', fontsize=16)
    plt.xlabel('Tipo de Transacción', fontsize=12)
    plt.ylabel('Monto Total ($)', fontsize=12)
    plt.xticks(rotation=0) # Evita que los labels se inclinen
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 4. Mostrar los valores en las barras
    for i, v in enumerate(resumen_tipo.values):
        plt.text(i, v + 50, f"${v:,.2f}", ha='center', va='bottom', fontsize=10)
    
    # 5. Muestra el gráfico en una ventana
    plt.tight_layout() # Ajusta los elementos para que no se superpongan
    plt.show()

# --- BLOQUE DE PRUEBA (Se mantiene para verificar la funcionalidad del módulo) ---
if __name__ == "__main__":
    df = generar_reporte_pandas()
    if not df.empty:
        visualizar_resumen(df)
    else:
        print("No se pudo generar el reporte. Asegúrate de tener datos en la DB.")