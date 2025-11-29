# --- 1. IMPORTS Y LIBRERÍAS ---
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import json

# --- 2. GESTIÓN DE BASE DE DATOS (BLINDADA) ---
DB_NAME = 'finanzas_personales.db'

def inicializar_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Aseguramos nombres de columnas estándar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                descripcion TEXT,
                monto REAL,
                tipo TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error DB: {e}")

def obtener_datos():
    """Obtiene datos y renombra columnas para evitar KeyError."""
    conn = sqlite3.connect(DB_NAME)
    # Pedimos las columnas en un orden específico
    try:
        query = "SELECT id, fecha, tipo, descripcion, monto FROM transacciones ORDER BY fecha DESC, id DESC"
        df = pd.read_sql_query(query, conn)
        
        # --- CORRECCIÓN VITAL PARA EL KEYERROR ---
        # Forzamos los nombres de las columnas para que coincidan con el código Python
        if not df.empty:
            df.columns = ['ID', 'Fecha', 'Tipo', 'Descripcion', 'Monto']
        else:
            # Si está vacía, creamos el DataFrame con las columnas esperadas
            df = pd.DataFrame(columns=['ID', 'Fecha', 'Tipo', 'Descripcion', 'Monto'])
            
    except Exception as e:
        print(f"Error leyendo datos: {e}")
        df = pd.DataFrame(columns=['ID', 'Fecha', 'Tipo', 'Descripcion', 'Monto'])
        
    conn.close()
    return df

def agregar_transaccion(fecha, descripcion, monto, tipo):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Lógica: Gasto es negativo para el cálculo interno
        monto_final = -abs(float(monto)) if tipo == 'GASTO' else abs(float(monto))
        
        cursor.execute(
            "INSERT INTO transacciones (fecha, descripcion, monto, tipo) VALUES (?, ?, ?, ?)",
            (fecha, descripcion, monto_final, tipo)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error guardando: {e}")
        return False

def eliminar_transaccion_db(transaccion_id):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transacciones WHERE id = ?", (transaccion_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

inicializar_db()

# --- 3. CONFIGURACIÓN APP ---
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'], suppress_callback_exceptions=True)

# --- 4. LAYOUT ---
app.layout = html.Div(style={'maxWidth': '1200px', 'margin': 'auto', 'padding': '20px'}, children=[
    
    dcc.Store(id='senal-actualizacion', data=0),

    html.H1("💰 Gestor de Finanzas Web", style={'textAlign': 'center', 'color': '#2E86C1'}),
    
    # SALDO
    html.Div(id='seccion-saldo', style={'textAlign': 'center', 'margin': '20px 0'}),
    
    html.Hr(),

    # FORMULARIO
    html.Div([
        html.H4("➕ Añadir Movimiento", style={'color': '#2E86C1'}),
        html.Div([
            # CORRECCIÓN VITAL PARA LA FECHA: Usamos type='text' para compatibilidad total
            html.Div([
                html.Label("Fecha (YYYY-MM-DD):"),
                dcc.Input(id='input-fecha', type='text', value=datetime.today().strftime('%Y-%m-%d'), placeholder='2025-01-01', style={'width': '100%'})
            ], style={'flex': '1'}),
            
            html.Div([
                html.Label("Tipo:"),
                dcc.Dropdown(
                    id='input-tipo',
                    options=[{'label': '📉 Gasto', 'value': 'GASTO'}, {'label': '📈 Ingreso', 'value': 'INGRESO'}],
                    value='GASTO',
                    clearable=False
                )
            ], style={'flex': '1'}),

            html.Div([
                html.Label("Monto ($):"),
                dcc.Input(id='input-monto', type='number', placeholder='0.00', min=0, style={'width': '100%'})
            ], style={'flex': '1'}),

            html.Div([
                html.Label("Descripción:"),
                dcc.Input(id='input-desc', type='text', placeholder='Ej: Supermercado', style={'width': '100%'})
            ], style={'flex': '2'}),
            
            html.Button('Guardar', id='btn-guardar', n_clicks=0, 
                        style={'backgroundColor': '#28B463', 'color': 'white', 'height': '38px', 'marginTop': '25px'})
            
        ], style={'display': 'flex', 'gap': '15px', 'alignItems': 'center'}),
        
        html.Div(id='notificacion-guardado', style={'marginTop': '10px', 'textAlign': 'center'})
    ], style={'backgroundColor': '#F8F9F9', 'padding': '15px', 'borderRadius': '8px'}),

    html.Hr(),

    # VISUALIZACIÓN
    html.Div([
        html.Div([
            html.H4("📋 Historial", style={'color': '#2E86C1'}),
            html.Div(id='contenedor-tabla') 
        ], className='six columns'),

        html.Div([
            html.H4("📊 Distribución", style={'color': '#2E86C1'}),
            dcc.Graph(id='grafica-pastel')
        ], className='six columns'),

    ], className='row')
])

# --- 5. CALLBACKS ---

@app.callback(
    Output('notificacion-guardado', 'children'),
    Output('input-monto', 'value'),
    Output('input-desc', 'value'),
    Output('senal-actualizacion', 'data'),
    Input('btn-guardar', 'n_clicks'),
    State('input-fecha', 'value'),
    State('input-monto', 'value'),
    State('input-tipo', 'value'),
    State('input-desc', 'value'),
    State('senal-actualizacion', 'data'),
    prevent_initial_call=True
)
def guardar_callback(n_clicks, fecha, monto, tipo, desc, senal_actual):
    if not fecha or not monto or not desc:
        return html.Span("⚠️ Faltan datos", style={'color': 'red'}), dash.no_update, dash.no_update, dash.no_update
    
    if agregar_transaccion(fecha, desc, monto, tipo):
        return html.Span("✅ Guardado", style={'color': 'green'}), '', '', (senal_actual or 0) + 1
    else:
        return html.Span("❌ Error DB", style={'color': 'red'}), dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('senal-actualizacion', 'data', allow_duplicate=True),
    Input({'type': 'btn-eliminar', 'index': dash.ALL}, 'n_clicks'),
    State('senal-actualizacion', 'data'),
    prevent_initial_call=True
)
def eliminar_callback(n_clicks_list, senal_actual):
    ctx = dash.callback_context
    if not ctx.triggered: return dash.no_update
    
    try:
        clicked_id_str = ctx.triggered[0]['prop_id'].split('.')[0]
        clicked_id_json = json.loads(clicked_id_str)
        transaccion_id = clicked_id_json['index']
        
        # Verificar que sea un click real
        click_val = ctx.triggered[0]['value']
        if not click_val or click_val == 0:
            return dash.no_update

        eliminar_transaccion_db(transaccion_id)
        return (senal_actual or 0) + 1
    except:
        return dash.no_update

@app.callback(
    Output('contenedor-tabla', 'children'),
    Output('grafica-pastel', 'figure'),
    Output('seccion-saldo', 'children'),
    Input('senal-actualizacion', 'data')
)
def refrescar_todo(senal):
    df = obtener_datos()
    
    # Cálculos seguros usando las columnas forzadas
    if df.empty:
        saldo, ingresos, gastos = 0, 0, 0
    else:
        # Aquí usamos 'Monto' con mayúscula porque lo forzamos en obtener_datos()
        saldo = df['Monto'].sum()
        ingresos = df[df['Monto'] > 0]['Monto'].sum()
        gastos = abs(df[df['Monto'] < 0]['Monto'].sum())
    
    estilo_num = {'fontSize': '20px', 'fontWeight': 'bold', 'margin': '0 15px'}
    html_saldo = html.Div([
        html.Span(f"Total: ${saldo:,.2f}", style={**estilo_num, 'color': '#2E86C1'}),
        html.Span(f"Ingresos: ${ingresos:,.2f}", style={**estilo_num, 'color': '#28B463'}),
        html.Span(f"Gastos: ${gastos:,.2f}", style={**estilo_num, 'color': '#C0392B'})
    ])

    # Gráfica
    if df.empty:
        fig = px.pie(names=['Vacio'], values=[1], title="Sin datos")
    else:
        df['Abs'] = df['Monto'].abs()
        fig = px.pie(df, values='Abs', names='Tipo', title='Resumen', color='Tipo',
                     color_discrete_map={'GASTO':'#C0392B', 'INGRESO':'#28B463'})

    # Tabla Manual
    if df.empty:
        tabla = html.Div("Sin transacciones")
    else:
        rows = []
        for i, row in df.iterrows():
            color = '#28B463' if row['Monto'] >= 0 else '#C0392B'
            rows.append(html.Tr([
                html.Td(row['Fecha']),
                html.Td(row['Tipo']),
                html.Td(row['Descripcion']),
                html.Td(f"${row['Monto']:,.2f}", style={'color': color, 'fontWeight': 'bold'}),
                html.Td(html.Button('🗑️', id={'type': 'btn-eliminar', 'index': row['ID']}))
            ]))
            
        tabla = html.Table([
            html.Tr([html.Th("Fecha"), html.Th("Tipo"), html.Th("Desc"), html.Th("Monto"), html.Th("X")])
        ] + rows, style={'width': '100%'})

    return tabla, fig, html_saldo

if __name__ == '__main__':
    print("Abriendo en http://127.0.0.1:8080/")
    app.run(debug=True, port=8080)