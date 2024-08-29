import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import serial.tools.list_ports

ser = None

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

def enviar_comando(comando, x, y):
    # Envía un comando G-code al Arduino.
    if ser and ser.is_open:
        comando_completo = comando + '\n'  # Añadir nueva línea al final del comando
        ser.write(comando_completo.encode())  # Enviar el comando como bytes
        respuesta = ser.readline().decode().strip()  # Leer la respuesta del Arduino
        print("Respuesta del Arduino: {}".format(respuesta))
        if respuesta:  # Check if there is a valid response
            save_reading(x, y, respuesta)  # Guardar la respuesta como PDD
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Funciones para los botones
def x1_positivo():
    enviar_comando('G91\nG0 X1 Y0\nG90', 1, 0)

def x10_positivo():
    enviar_comando('G91\nG0 X10 Y0\nG90', 10, 0)

def x100_positivo():
    enviar_comando('G91\nG0 X100 Y0\nG90', 100, 0)

def x1_negativo():
    enviar_comando('G91\nG0 X-1 Y0\nG90', -1, 0)

def x10_negativo():
    enviar_comando('G91\nG0 X-10 Y0\nG90', -10, 0)

def x100_negativo():
    enviar_comando('G91\nG0 X-100 Y0\nG90', -100, 0)

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
    # Devuelve el motor a la posición de origen (0,0).
 enviar_comando('G90')  # Asegurarse de que estamos en modo absoluto
 enviar_comando('G0 X0 Y0 Z0')

def resetear():
    if ser:
        ser.write(b'R')  # Enviar comando de reseteo al Arduino
        messagebox.showinfo("Reseteo", "Reseteo en proceso...")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Crear la ventana principal
root = tk.Tk()
root.title("Control de Dosímetro")
root.geometry("650x500")

# Botones
btn_calibrar = ttk.Button(root, text="Calibrar (Homing)",  command=calibrar)
btn_calibrar.grid(row=8, column=3, padx=10, pady=5)

btn_resetear = ttk.Button(root, text="Resetear",style='primary.TButton', command=resetear)
btn_resetear.grid(row=8, column=4, padx=10, pady=5)

btn_iniciar = ttk.Button(root, text="Iniciar Escaneo",style='primary.TButton')
btn_iniciar.grid(row=8, column=5, padx=10, pady=10)

# Eje Y
btn_iniciar = ttk.Button(root, text="100Y+", style='primary.Outline.TButton', command=y100_positivo)
btn_iniciar.grid(row=1, column=4,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="10Y+", style='primary.Outline.TButton', command=y10_positivo)
btn_iniciar.grid(row=2, column=4,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="1Y+", style='primary.Outline.TButton', command=y1_positivo)
btn_iniciar.grid(row=3, column=4,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="1Y-", style='primary.Outline.TButton', command=y1_negativo)
btn_iniciar.grid(row=5, column=4,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="10Y-", style='primary.Outline.TButton', command=y10_negativo)
btn_iniciar.grid(row=6, column=4,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="100Y-", style='primary.Outline.TButton', command=y100_negativo)
btn_iniciar.grid(row=7, column=4, padx=10, pady=10)

#Calibrar
btn_iniciar = ttk.Button(root, text="Calibrar", style='primary.Outline.TButton', command=calibrar)
btn_iniciar.grid(row=4, column=4, padx=10, pady=10,sticky="e")

# Eje X
btn_iniciar = ttk.Button(root, text="100X+", style='primary.Outline.TButton', command=x100_positivo)
btn_iniciar.grid(row=4, column=7, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="10X+", style='primary.Outline.TButton', command=x10_positivo)
btn_iniciar.grid(row=4, column=6, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="1X+", style='primary.Outline.TButton', command=x1_positivo)
btn_iniciar.grid(row=4, column=5, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="1X-", style='primary.Outline.TButton', command=x1_negativo)
btn_iniciar.grid(row=4, column=3, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="10X-", style='primary.Outline.TButton', command=x10_negativo)
btn_iniciar.grid(row=4, column=2, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="100X-", style='primary.Outline.TButton', command=x100_negativo)
btn_iniciar.grid(row=4, column=1, padx=0, pady=0, sticky="w")
root.mainloop()
