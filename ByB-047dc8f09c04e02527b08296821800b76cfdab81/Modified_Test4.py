import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
from tkinter import ttk

ser = None
x_pos = 0
y_pos = 0

def find_arduino():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'USB' in port.description:
            try:
                ser = serial.Serial(port.device, 9600, timeout=1)
                ser.close()
                return port.device
            except serial.SerialException:
                pass
    return None

# Busca el puerto serie y establece la conexión
port = find_arduino()
if port:
    try:
        ser = serial.Serial(port, 9600, timeout=1)
        print(f"Conectado al puerto: {port}")
    except serial.SerialException:
        print("Error al conectar al puerto USB.")
else:
    print("No se encontró ningún dispositivo conectado.")

def save_reading(x, y, reading):
    with open('radiation_readings.txt', 'a') as file:
        file.write(f"X: {x}, Y: {y}, PDD: {reading}\n")

def actualizar_posiciones(x, y):
    global x_pos, y_pos
    x_pos += x
    y_pos += y
    label_x.config(text=f"X: {x_pos}")
    label_y.config(text=f"Y: {y_pos}")

def enviar_comando(comando, x, y):
    if ser and ser.is_open:
        comando_completo = comando + '\n'
        ser.write(comando_completo.encode())
        respuesta = ser.readline().decode().strip()
        print("Respuesta del Arduino: {}".format(respuesta))
        if respuesta:
            save_reading(x_pos, y_pos, respuesta)
        actualizar_posiciones(x, y)
        if not messagebox.askyesno("Continuar", "¿Quieres seguir con el siguiente barrido?"):
            root.quit()
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Funciones para los botones
def x1_positivo():
    enviar_comando('G91\nG0 X1 Z1\nG90', 1, 0)

def x10_positivo():
    enviar_comando('G91\nG0 X10 Z10\nG90', 10, 0)

def x100_positivo():
    enviar_comando('G91\nG0 X100 Z100\nG90', 100, 0)

def x1_negativo():
    enviar_comando('G91\nG0 X-1 Z-1\nG90', -1, 0)

def x10_negativo():
    enviar_comando('G91\nG0 X-10 Z-10\nG90', -10, 0)

def x100_negativo():
    enviar_comando('G91\nG0 X-100 Z-100\nG90', -100, 0)

def y1_positivo():
    enviar_comando('G91\nG0 X0 Y1\nG90', 0, 1)

def y10_positivo():
    enviar_comando('G91\nG0 X0 Y10\nG90', 0, 10)

def y100_positivo():
    enviar_comando('G91\nG0 X0 Y100\nG90', 0, 100)

def y1_negativo():
    enviar_comando('G91\nG0 X0 Y-1\nG90', 0, -1)

def y10_negativo():
    enviar_comando('G91\nG0 X0 Y-10\nG90', 0, -10)

def y100_negativo():
    enviar_comando('G91\nG0 X0 Y-100\nG90', 0, -100)

def calibrar():
    enviar_comando('G91\nG0 X0 Y0\nG90', -x_pos, -y_pos)

def resetear():
    if ser:
        ser.write(b'R')
        messagebox.showinfo("Reseteo", "Reseteo en proceso...")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Control de Máquina")

# Etiquetas para mostrar las posiciones
label_x = ttk.Label(root, text=f"X: {x_pos}")
label_x.grid(row=0, column=5, padx=10, pady=10)
label_y = ttk.Label(root, text=f"Y: {y_pos}")
label_y.grid(row=1, column=5, padx=10, pady=10)

# Botones
btn_calibrar = ttk.Button(root, text="Calibrar (Homing)", command=calibrar)
btn_calibrar.grid(row=8, column=3, padx=10, pady=5)

btn_resetear = ttk.Button(root, text="Resetear", style='primary.TButton', command=resetear)
btn_resetear.grid(row=8, column=4, padx=10, pady=5)

btn_iniciar = ttk.Button(root, text="Iniciar Escaneo", style='primary.TButton')
btn_iniciar.grid(row=8, column=5, padx=10, pady=10)

# Eje Y
btn_y100_pos = ttk.Button(root, text="100Y+", style='primary.Outline.TButton', command=y100_positivo)
btn_y100_pos.grid(row=1, column=4, padx=10, pady=10)

btn_y10_pos = ttk.Button(root, text="10Y+", style='primary.Outline.TButton', command=y10_positivo)
btn_y10_pos.grid(row=2, column=4, padx=10, pady=10)

btn_y1_pos = ttk.Button(root, text="1Y+", style='primary.Outline.TButton', command=y1_positivo)
btn_y1_pos.grid(row=3, column=4, padx=10, pady=10)

btn_y1_neg = ttk.Button(root, text="1Y-", style='primary.Outline.TButton', command=y1_negativo)
btn_y1_neg.grid(row=5, column=4, padx=10, pady=10)

btn_y10_neg = ttk.Button(root, text="10Y-", style='primary.Outline.TButton', command=y10_negativo)
btn_y10_neg.grid(row=6, column=4, padx=10, pady=10)

btn_y100_neg = ttk.Button(root, text="100Y-", style='primary.Outline.TButton', command=y100_negativo)
btn_y100_neg.grid(row=7, column=4, padx=10, pady=10)

# Calibrar
btn_calibrar = ttk.Button(root, text="Calibrar", style='primary.Outline.TButton', command=calibrar)
btn_calibrar.grid(row=4, column=4, padx=10, pady=10, sticky="e")

# Eje X
btn_x100_pos = ttk.Button(root, text="100X+", style='primary.Outline.TButton', command=x100_positivo)
btn_x100_pos.grid(row=4, column=7, padx=0, pady=0, sticky="w")

btn_x10_pos = ttk.Button(root, text="10X+", style='primary.Outline.TButton', command=x10_positivo)
btn_x10_pos.grid(row=4, column=6, padx=0, pady=0, sticky="w")

btn_x1_pos = ttk.Button(root, text="1X+", style='primary.Outline.TButton', command=x1_positivo)
btn_x1_pos.grid(row=4, column=5, padx=0, pady=0, sticky="w")

btn_x1_neg = ttk.Button(root, text="1X-", style='primary.Outline.TButton', command=x1_negativo)
btn_x1_neg.grid(row=4, column=3, padx=0, pady=0, sticky="w")

btn_x10_neg = ttk.Button(root, text="10X-", style='primary.Outline.TButton', command=x10_negativo)
btn_x10_neg.grid(row=4, column=2, padx=0, pady=0, sticky="w")

btn_x100_neg = ttk.Button(root, text="100X-", style='primary.Outline.TButton', command=x100_negativo)
btn_x100_neg.grid(row=4, column=1, padx=0, pady=0, sticky="w")

root.mainloop()
