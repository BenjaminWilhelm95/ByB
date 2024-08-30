import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import serial.tools.list_ports

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

def enviar_comando(comando, x=0, y=0):
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
    enviar_comando('G91\nG0 X10 Z10\nG90',10,0)

def x100_positivo():
    enviar_comando('G91\nG0 X100 Z100\nG90',100,0)

def x1_negativo():
    enviar_comando('G91\nG0 X-1 Z-1\nG90',-1,0)

def x10_negativo():
    enviar_comando('G91\nG0 X-10 Z-10 \nG90',-10,0)

def x100_negativo():
    enviar_comando('G91\nG0 X-100 Z-100\nG90',-100,0)

def y1_positivo():
    enviar_comando('G91\nG0 Y1\nG90',0,1)

def y10_positivo():
    enviar_comando('G91\nG0 Y10\nG90',0,10)

def y100_positivo():
    enviar_comando('G91\nG0 Y100\nG90',0,100)

def y1_negativo():
    enviar_comando('G91\nG0 Y-1\nG90',0,-1)

def y10_negativo():
    enviar_comando('G91\nG0 Y-10\nG90',0,-10)

def y100_negativo():
    enviar_comando('G91\nG0 Y-100\nG90',0,-100)

def calibrar():
    #Devuelve el motor a la posición de origen (0,0,0).
    enviar_comando('G90', 0, 0)  # Asegurarse de que estamos en modo absoluto y enviar x, y = 0, 0
    enviar_comando('G0 X0 Y0 Z0', 0, 0)  # Mover a la posición absoluta de origen

def mover_manual():
    #Mueve los motores X e Y a la distancia especificada en los campos de entrada."""
    try:
        distancia_x = float(entry_area_x.get())  # Obtener el valor de X
        distancia_y = float(entry_area_y.get())  # Obtener el valor de Y

        enviar_comando('G91')  # Cambiar a modo relativo
        enviar_comando(f'G0 X{distancia_x} Y{distancia_y} Z{distancia_x}',distancia_x,distancia_y)  # Mover X e Y a la distancia especificada
        enviar_comando('G90')  # Volver a modo absoluto (opcional si no necesitas estar en modo relativo)

    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese un número válido para las distancias.")



# Crear la ventana principal
root = tk.Tk()
root.title("Control de Dosímetro")
root.geometry("1000x390")

# Etiquetas y cuadros de texto
tk.Label(root, text="Distancia X a recorrer:").grid(row=1, column=1, padx=10, pady=5)
entry_area_x = tk.Entry(root)
entry_area_x.grid(row=1, column=2, padx=10, pady=5)

tk.Label(root, text="Distancia Y a recorrer:").grid(row=2, column=1, padx=10, pady=5)
entry_area_y = tk.Entry(root)
entry_area_y.grid(row=2, column=2, padx=10, pady=5)

# Etiquetas para mostrar las posiciones
label_x = ttk.Label(root, text=f"X: {x_pos}")
label_x.grid(row=1, column=5, padx=10, pady=10)
label_y = ttk.Label(root, text=f"Y: {y_pos}")
label_y.grid(row=2, column=5, padx=10, pady=10)

# Botones
btn_calibrar = ttk.Button(root, text="Calibrar (Homing)",  command=calibrar)
btn_calibrar.grid(row=8, column=1, padx=10, pady=5)

btn_resetear = ttk.Button(root, text="Mover manual",style='primary.TButton', command=mover_manual)
btn_resetear.grid(row=8, column=2, padx=10, pady=5)

btn_iniciar = ttk.Button(root, text="Iniciar Escaneo",style='primary.TButton')
btn_iniciar.grid(row=8, column=0, padx=10, pady=10)

# Eje Y
btn_iniciar = ttk.Button(root, text="100Y+", style='primary.Outline.TButton', command=y100_positivo)
btn_iniciar.grid(row=1, column=6,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="10Y+", style='primary.Outline.TButton', command=y10_positivo)
btn_iniciar.grid(row=2, column=6,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="1Y+", style='primary.Outline.TButton', command=y1_positivo)
btn_iniciar.grid(row=3, column=6,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="1Y-", style='primary.Outline.TButton', command=y1_negativo)
btn_iniciar.grid(row=5, column=6,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="10Y-", style='primary.Outline.TButton', command=y10_negativo)
btn_iniciar.grid(row=6, column=6,padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="100Y-", style='primary.Outline.TButton', command=y100_negativo)
btn_iniciar.grid(row=7, column=6, padx=10, pady=10)

#Calibrar
btn_iniciar = ttk.Button(root, text="Calibrar", style='primary.Outline.TButton', command=calibrar)
btn_iniciar.grid(row=4, column=6, padx=10, pady=10,sticky="e")

# Eje X
btn_iniciar = ttk.Button(root, text="100X+", style='primary.Outline.TButton', command=x100_positivo)
btn_iniciar.grid(row=4, column=9, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="10X+", style='primary.Outline.TButton', command=x10_positivo)
btn_iniciar.grid(row=4, column=8, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="1X+", style='primary.Outline.TButton', command=x1_positivo)
btn_iniciar.grid(row=4, column=7, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="1X-", style='primary.Outline.TButton', command=x1_negativo)
btn_iniciar.grid(row=4, column=5, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="10X-", style='primary.Outline.TButton', command=x10_negativo)
btn_iniciar.grid(row=4, column=4, padx=0, pady=0, sticky="w")

btn_iniciar = ttk.Button(root, text="100X-", style='primary.Outline.TButton', command=x100_negativo)
btn_iniciar.grid(row=4, column=3, padx=0, pady=0, sticky="w")
root.mainloop()