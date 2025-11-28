from flask import Flask, render_template, request, redirect, url_for, make_response # make_response para anti-caché
from finanzas_db import GestorFinanzasDB 
from datetime import datetime
# 🔥 IMPORTACIONES DE LA GRÁFICA: Deben existir los archivos finanzas_db.py y finanza_reportes.py
from finanzas_reportes import generar_reporte_pandas, visualizar_resumen 

# 1. Inicialización de Flask y Base de Datos
app = Flask(__name__)
db_manager = GestorFinanzasDB()

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def index():
    """
    Ruta principal (GET): Muestra el tablero, el saldo y todas las transacciones.
    """
    saldo, ingresos, gastos = db_manager.obtener_saldo_total()
    transacciones = db_manager.obtener_transacciones()
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Creamos la respuesta (para el anti-caché)
    response = make_response(render_template('index.html', 
                            saldo=saldo, 
                            ingresos=ingresos, 
                            gastos=gastos, 
                            transacciones=transacciones,
                            today_date=today_date))
    
    # 2. <-- ANTI-CACHÉ: Le decimos al navegador que NUNCA guarde esta página en caché
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    
    # Retornamos la respuesta modificada
    return response

# 🔥 NUEVA RUTA PARA LA GRÁFICA 🔥
@app.route('/grafica')
def generar_grafica_web():
    """
    Ruta que genera el DataFrame y llama a la función de Matplotlib para mostrar la gráfica.
    NOTA: El gráfico se abrirá en una ventana separada en el escritorio.
    """
    try:
        # Llama a la función que usa Pandas para obtener los datos
        df_finanzas = generar_reporte_pandas()
        
        if not df_finanzas.empty:
            # Llama a la función que usa Matplotlib para abrir la ventana de la gráfica
            visualizar_resumen(df_finanzas) 
        
        # Redirigimos siempre a la página principal, sin importar si hay datos o no.
        return redirect(url_for('index'))

    except Exception as e:
        print(f"❌ Error al generar la gráfica. Verifica la instalación de Pandas/Matplotlib. Error: {e}")
        # En caso de error, simplemente redirige.
        return redirect(url_for('index'))


@app.route('/agregar', methods=['POST'])
def agregar():
    """
    Ruta para recibir los datos del formulario (POST) e insertarlos en la DB.
    """
    try:
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        monto = float(request.form['monto'])
        tipo = request.form['tipo']
    except Exception as e:
        print(f"Error al procesar el formulario: {e}")
        return redirect(url_for('index'))

    db_manager.insertar_transaccion(fecha, descripcion, monto, tipo)
    
    return redirect(url_for('index'))


@app.route('/eliminar/<int:id_transaccion>', methods=['POST'])
def eliminar(id_transaccion):
    """
    Ruta para eliminar una transacción específica usando su ID.
    """
    db_manager.eliminar_transaccion(id_transaccion)
    
    return redirect(url_for('index'))


# --- BLOQUE DE EJECUCIÓN ---
if __name__ == '__main__':
    # Usamos el modo de depuración para que se recargue automáticamente
    app.run(debug=True)