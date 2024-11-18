import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('actividad_fisica.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS ejercicios (
    id INTEGER PRIMARY KEY,
    fecha TEXT,
    tipo_actividad TEXT,
    duracion INTEGER,
    intensidad TEXT
)
''')
conn.commit()

# Funciones
def registrar_ejercicio():
    """Registra un ejercicio en la base de datos."""
    fecha = datetime.now().strftime("%Y-%m-%d")
    tipo_actividad = tipo_entry.get()
    duracion = duracion_entry.get()
    intensidad = intensidad_var.get()
    
    if not tipo_actividad or not duracion or not intensidad:
        messagebox.showerror("Error", "Por favor, completa todos los campos")
        return
    
    try:
        duracion = int(duracion)
        if duracion <= 0:
            raise ValueError("La duración debe ser mayor a 0.")
    except ValueError as e:
        messagebox.showerror("Error", f"La duración debe ser un número válido: {e}")
        return
    
    c.execute('''
    INSERT INTO ejercicios (fecha, tipo_actividad, duracion, intensidad)
    VALUES (?, ?, ?, ?)
    ''', (fecha, tipo_actividad, duracion, intensidad))
    conn.commit()
    messagebox.showinfo("Éxito", "Ejercicio registrado correctamente")
    limpiar_campos()

def limpiar_campos():
    """Limpia los campos de entrada."""
    tipo_entry.delete(0, tk.END)
    duracion_entry.delete(0, tk.END)
    intensidad_var.set("")

def mostrar_progreso():
    """Muestra una gráfica del progreso diario."""
    c.execute('SELECT fecha, duracion FROM ejercicios')
    datos = c.fetchall()
    if not datos:
        messagebox.showinfo("Sin datos", "No hay registros de ejercicios para mostrar.")
        return
    
    df = pd.DataFrame(datos, columns=["Fecha", "Duración"])
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df = df.groupby("Fecha").sum()
    
    plt.figure(figsize=(10, 5))
    plt.plot(df.index, df["Duración"], marker='o', linestyle='-', color='b')
    plt.title("Progreso de Actividad Física")
    plt.xlabel("Fecha")
    plt.ylabel("Duración (minutos)")
    plt.grid()
    plt.show()

def mostrar_por_tipo():
    """Muestra una gráfica de las actividades por tipo."""
    c.execute('SELECT tipo_actividad, SUM(duracion) FROM ejercicios GROUP BY tipo_actividad')
    datos = c.fetchall()
    if not datos:
        messagebox.showinfo("Sin datos", "No hay registros de ejercicios para mostrar.")
        return
    
    df = pd.DataFrame(datos, columns=["Tipo de Actividad", "Duración"])
    
    plt.figure(figsize=(8, 5))
    plt.bar(df["Tipo de Actividad"], df["Duración"], color='skyblue')
    plt.title("Duración por Tipo de Actividad")
    plt.xlabel("Tipo de Actividad")
    plt.ylabel("Duración (minutos)")
    plt.xticks(rotation=45)
    plt.show()

def exportar_datos():
    """Exporta los datos a un archivo CSV."""
    c.execute('SELECT * FROM ejercicios')
    datos = c.fetchall()
    if not datos:
        messagebox.showinfo("Sin datos", "No hay registros para exportar.")
        return
    
    archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if archivo:
        df = pd.DataFrame(datos, columns=["ID", "Fecha", "Tipo de Actividad", "Duración", "Intensidad"])
        df.to_csv(archivo, index=False)
        messagebox.showinfo("Éxito", "Datos exportados correctamente.")

def limpiar_registros():
    """Elimina todos los registros de la base de datos."""
    if messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar todos los registros?"):
        c.execute('DELETE FROM ejercicios')
        conn.commit()
        messagebox.showinfo("Éxito", "Todos los registros han sido eliminados.")

# Interfaz de la gráfica
root = tk.Tk()
root.title("Seguimiento de Actividad Física")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

tk.Label(frame, text="Tipo de actividad:").grid(row=0, column=0, padx=5, pady=5)
tipo_entry = tk.Entry(frame)
tipo_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Duración (min):").grid(row=1, column=0, padx=5, pady=5)
duracion_entry = tk.Entry(frame)
duracion_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Intensidad:").grid(row=2, column=0, padx=5, pady=5)
intensidad_var = tk.StringVar()
intensidad_menu = ttk.Combobox(frame, textvariable=intensidad_var, values=["Baja", "Media", "Alta"])
intensidad_menu.grid(row=2, column=1, padx=5, pady=5)

# Botones
registrar_button = tk.Button(frame, text="Registrar Ejercicio", command=registrar_ejercicio)
registrar_button.grid(row=3, column=0, columnspan=2, pady=10)

progreso_button = tk.Button(frame, text="Mostrar Progreso Diario", command=mostrar_progreso)
progreso_button.grid(row=4, column=0, columnspan=2, pady=10)

tipo_button = tk.Button(frame, text="Mostrar por Tipo de Actividad", command=mostrar_por_tipo)
tipo_button.grid(row=5, column=0, columnspan=2, pady=10)

exportar_button = tk.Button(frame, text="Exportar Datos a CSV", command=exportar_datos)
exportar_button.grid(row=6, column=0, columnspan=2, pady=10)

limpiar_button = tk.Button(frame, text="Limpiar Todos los Registros", command=limpiar_registros)
limpiar_button.grid(row=7, column=0, columnspan=2, pady=10)

root.mainloop()
