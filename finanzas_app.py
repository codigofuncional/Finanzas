import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

# Importamos la clase que creaste en el archivo finanzas_db.py
from finanzas_db import GestorFinanzasDB 
# 🔥 NUEVA IMPORTACIÓN: Traemos las dos funciones de tu archivo finanza_reportes.py
from finanzas_reportes import generar_reporte_pandas, visualizar_resumen 

# --- CLASE PRINCIPAL DE LA APLICACIÓN (TKINTER) ---

class AppFinanzas(tk.Tk):
    """
    Clase que representa la ventana principal de la aplicación.
    Hereda de tk.Tk, convirtiéndose en la ventana.
    """
    def __init__(self):
        super().__init__()
        
        # 1. Configuración de la Ventana
        self.title("💰 Gestor de Finanzas Personales (Desktop)")
        self.geometry("750x600") # Aumentamos un poco el tamaño
        
        # 2. Inicializar la Base de Datos
        self.db = GestorFinanzasDB()
        
        # 3. Crear los Widgets de la Interfaz
        self.crear_widgets()
        
        # 4. Cargar y Mostrar los datos iniciales
        self.actualizar_vista()
        
    def crear_widgets(self):
        """Define y posiciona todos los elementos de la interfaz."""
        
        # --- 3A. Frame de Entrada de Datos ---
        frame_entrada = ttk.LabelFrame(self, text="➕ Nueva Transacción", padding="10 10 10 10")
        frame_entrada.pack(pady=10, padx=10, fill="x")
        
        # Variables y Campos de Entrada
        ttk.Label(frame_entrada, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entrada_fecha = ttk.Entry(frame_entrada, width=15)
        self.entrada_fecha.insert(0, datetime.now().strftime("%Y-%m-%d")) 
        self.entrada_fecha.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_entrada, text="Descripción:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entrada_desc = ttk.Entry(frame_entrada, width=30)
        self.entrada_desc.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(frame_entrada, text="Monto:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entrada_monto = ttk.Entry(frame_entrada, width=15)
        self.entrada_monto.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame_entrada, text="Tipo:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.tipo_var = tk.StringVar(value="GASTO")
        ttk.Radiobutton(frame_entrada, text="Gasto", variable=self.tipo_var, value="GASTO").grid(row=1, column=3, sticky="w")
        ttk.Radiobutton(frame_entrada, text="Ingreso", variable=self.tipo_var, value="INGRESO").grid(row=1, column=4, sticky="w")
        
        # Botón de Guardar
        ttk.Button(frame_entrada, text="Guardar Transacción", command=self.guardar_transaccion).grid(row=2, column=0, columnspan=5, pady=10, sticky="ew")

        # --- 3B. Frame de Resumen, Botones y Treeview ---
        
        frame_resumen = ttk.Frame(self)
        frame_resumen.pack(pady=5, padx=10, fill="x")
        
        # Etiqueta de Saldo
        self.saldo_label = ttk.Label(frame_resumen, text="SALDO TOTAL: $0.00 | INGRESOS: $0.00 | GASTOS: $0.00", font=("Arial", 12, "bold"))
        self.saldo_label.pack(side="left", padx=10)

        # 🔥 BOTÓN NUEVO: Llama al método para generar la gráfica
        ttk.Button(frame_resumen, text="📈 Generar Gráfica", command=self.generar_grafica).pack(side="right", padx=5)
        
        # Botón de Eliminar
        ttk.Button(frame_resumen, text="❌ Eliminar Seleccionado", command=self.eliminar_transaccion_seleccionada).pack(side="right", padx=5)
        
        # Historial (Treeview)
        frame_historial = ttk.LabelFrame(self, text="📋 Historial de Transacciones", padding="10 5 10 5")
        frame_historial.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.tree = self.crear_treeview(frame_historial)
        
    def crear_treeview(self, parent):
        """Crea el widget Treeview (tabla) y sus columnas."""
        
        columnas = ('ID', 'Fecha', 'Tipo', 'Monto', 'Descripción')
        tree = ttk.Treeview(parent, columns=columnas, show='headings')
        
        tree.heading('ID', text='ID', anchor='center')
        tree.heading('Fecha', text='Fecha', anchor='center')
        tree.heading('Tipo', text='Tipo', anchor='center')
        tree.heading('Monto', text='Monto', anchor='e')
        tree.heading('Descripción', text='Descripción', anchor='w')

        tree.column('ID', width=30, anchor='center')
        tree.column('Fecha', width=80, anchor='center')
        tree.column('Tipo', width=70, anchor='center')
        tree.column('Monto', width=70, anchor='e')
        tree.column('Descripción', width=200, anchor='w')
        
        tree.pack(fill="both", expand=True)
        return tree

    # 🔥 NUEVO MÉTODO: Generar la gráfica
    def generar_grafica(self):
        """Llama a las funciones del módulo de reportes para mostrar el gráfico."""
        try:
            # 1. Obtenemos el DataFrame de Pandas usando la función de finanza_reportes
            df_finanzas = generar_reporte_pandas()
            
            # 2. Verificamos si hay datos
            if not df_finanzas.empty:
                # 3. Visualizamos el resumen (esto abre la ventana de Matplotlib)
                visualizar_resumen(df_finanzas)
            else:
                messagebox.showwarning("Advertencia", "No hay transacciones registradas para generar el gráfico.")
        
        except Exception as e:
             messagebox.showerror("Error", f"Asegúrate de tener instalados Pandas y Matplotlib. Error: {e}")
        
    
    def actualizar_vista(self):
        """
        Llama a los métodos de la clase DB y actualiza la interfaz (saldo y tabla).
        """
        # 1. Limpiar la tabla Treeview antes de cargar nuevos datos
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 2. Cargar y actualizar el Saldo
        saldo, ingresos, gastos = self.db.obtener_saldo_total()
        self.saldo_label.config(text=f"SALDO TOTAL: ${saldo:,.2f} | INGRESOS: ${ingresos:,.2f} | GASTOS: ${gastos:,.2f}")
        
        # 3. Cargar y llenar la tabla Treeview
        transacciones = self.db.obtener_transacciones()
        for transaccion in transacciones:
            datos_formateados = (
                transaccion[0], # ID
                transaccion[1], # Fecha
                transaccion[4], # Tipo
                f"${transaccion[3]:,.2f}", # Monto formateado
                transaccion[2] # Descripción
            )
            self.tree.insert('', tk.END, values=datos_formateados)

    def guardar_transaccion(self):
        """
        Función llamada al presionar el botón de guardar.
        Valida datos y llama al método de inserción de la clase DB.
        """
        fecha = self.entrada_fecha.get()
        descripcion = self.entrada_desc.get()
        tipo = self.tipo_var.get()
        
        try:
            monto = float(self.entrada_monto.get())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número positivo.")
            return

        if not fecha or not descripcion:
             messagebox.showerror("Error", "Todos los campos son obligatorios.")
             return
             
        self.db.insertar_transaccion(fecha, descripcion, monto, tipo)
        
        self.entrada_desc.delete(0, tk.END)
        self.entrada_monto.delete(0, tk.END)
        
        self.actualizar_vista()

    def eliminar_transaccion_seleccionada(self):
        """Maneja la lógica para eliminar el elemento seleccionado en el Treeview."""
        item_seleccionado = self.tree.selection()
        
        if not item_seleccionado:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una transacción para eliminar.")
            return

        valores = self.tree.item(item_seleccionado, 'values')
        id_transaccion = valores[0]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar la transacción ID {id_transaccion} ({valores[4]})?"):
            
            if self.db.eliminar_transaccion(id_transaccion):
                messagebox.showinfo("Éxito", f"Transacción ID {id_transaccion} eliminada.")
                self.actualizar_vista()
            else:
                messagebox.showerror("Error", "No se pudo eliminar la transacción.")


# --- BLOQUE DE EJECUCIÓN (¡Fuera de la clase y sin indentación!) ---
if __name__ == "__main__":
    app = AppFinanzas()
    app.mainloop()