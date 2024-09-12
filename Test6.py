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
    with open('Coordenadas_usadas.txt', 'a') as file:
        file.write(f"X: {x}, Y: {y}, PDD: {reading}\n")

# Función para enviar comandos G-code
def enviar_comando(comando, x=0, y=0):
    global x_pos, y_pos
    if ser and ser.is_open:
        comando_completo = comando + '\n'
        ser.write(comando_completo.encode())
        respuesta = ser.readline().decode().strip()
        print("Respuesta del Arduino: {}".format(respuesta))
        if respuesta:
            save_reading(x, y, respuesta)
        x_pos += x
        y_pos += y
        label_x.config(text=f"Posición X: {x_pos}")
        label_y.config(text=f"Posición Y: {y_pos}")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Simulación de función que guardaría las lecturas (para mantener tu código funcional)
def save_reading(x, y, respuesta):
    pass  # Puedes implementar esta función como sea necesario

# Función para realizar el homing
def homing():
    global x_pos, y_pos
    enviar_comando('G0\nG91 X-200 Y-200\nG90', -200, -200)  # Movemos en negativo hacia los fines de carrera
    recalibrar_origen()

def recalibrar_origen():
    global x_pos, y_pos
    x_pos, y_pos = 0, 0
    label_x.config(text=f"Posición X: {x_pos}")
    label_y.config(text=f"Posición Y: {y_pos}")
    messagebox.showinfo("Calibración", "La posición (0,0) ha sido establecida en los fines de carrera.")

# Funciones para los botones de movimiento
def x1_positivo():
    enviar_comando('G91\nG0 X1 Y1 \nG90', 1, 0)

def x10_positivo():
    enviar_comando('G91\nG0 X10 Y10\nG90', 10, 0)

def x100_positivo():
    enviar_comando('G91\nG0 X100 Y100\nG90', 100, 0)

def x1_negativo():
    enviar_comando('G91\nG0 X-1 Y-1\nG90', -1, 0)

def x10_negativo():
    enviar_comando('G91\nG0 X-10 Y-10\nG90', -10, 0)

def x100_negativo():
    enviar_comando('G91\nG0 X-100 Y-100\nG90', -100, 0)

def y1_positivo():
    enviar_comando('G91\nG0 Z0.25\nG90', 0, 0.25)

def y10_positivo():
    enviar_comando('G91\nG0 Z10\nG90', 0, 10)

def y100_positivo():
    enviar_comando('G91\nG0 Z100\nG90', 0, 100)

def y1_negativo():
    enviar_comando('G91\nG0 Z-1\nG90', 0, -1)

def y10_negativo():
    enviar_comando('G91\nG0 Z-10\nG90', 0, -10)

def y100_negativo():
    enviar_comando('G91\nG0 Z-100\nG90', 0, -100)

def calibrar():
    global x_pos, y_pos
    enviar_comando('G91\nG0 X{} Y{}\nG90'.format(-x_pos, -y_pos), -x_pos, -y_pos)
    x_pos, y_pos = 0, 0
    label_x.config(text=f"Posición X: {x_pos}")
    label_y.config(text=f"Posición Y: {y_pos}")
#$21=1
def parada_emergencia():
    if ser and ser.is_open:
        ser.write(b'!')  # Comando de pausa de emergencia en GRBL
        ser.flush()
        messagebox.showinfo("Parada de Emergencia", "Los motores han sido detenidos")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

def mover_distancia_x(distancia):
    enviar_comando(f'G91\nG0 X{distancia} Z{distancia}\nG90', distancia, 0)

def mover_distancia_y(distancia):
    enviar_comando(f'G91\nG0 X0 Y{distancia}\nG90', 0, distancia)

# Crear la interfaz gráfica
root = tk.Tk()
root.title("Control de Máquina")

# Labels para mostrar la posición actual
label_x = tk.Label(root, text=f"Posición X: {x_pos}")
label_x.grid(row=0, column=1, columnspan=2)

label_y = tk.Label(root, text=f"Posición Y: {y_pos}")
label_y.grid(row=1, column=1, columnspan=2)

# Entradas para mover a una distancia específica
entry_distancia_x = tk.Entry(root)
entry_distancia_x.grid(row=2, column=1)
entry_distancia_x.insert(0, "0")

entry_distancia_y = tk.Entry(root)
entry_distancia_y.grid(row=3, column=1)
entry_distancia_y.insert(0, "0")

# Botones "+" y "-" para mover a la distancia especificada en X
def incrementar_x():
    mover_distancia_x(int(entry_distancia_x.get()))

def decrementar_x():
    mover_distancia_x(-int(entry_distancia_x.get()))

btn_x_mas = ttk.Button(root, text="+", command=incrementar_x)
btn_x_mas.grid(row=2, column=2)

btn_x_menos = ttk.Button(root, text="-", command=decrementar_x)
btn_x_menos.grid(row=2, column=0)

# Botones "+" y "-" para mover a la distancia especificada en Y
def incrementar_y():
    mover_distancia_y(int(entry_distancia_y.get()))

def decrementar_y():
    mover_distancia_y(-int(entry_distancia_y.get()))

btn_y_mas = ttk.Button(root, text="+", command=incrementar_y)
btn_y_mas.grid(row=3, column=2)

btn_y_menos = ttk.Button(root, text="-", command=decrementar_y)
btn_y_menos.grid(row=3, column=0)

# Botones de control de movimientos estándar
btn_calibrar = ttk.Button(root, text="Calibrar", command=calibrar)
btn_calibrar.grid(row=4, column=4, padx=10, pady=5)

btn_iniciar = ttk.Button(root, text="Parada de Emergencia", command=parada_emergencia,style='primary.TButton')
btn_iniciar.grid(row=8, column=0, padx=10, pady=10)

btn_calibrar = ttk.Button(root, text="Homing", command=homing)
btn_calibrar.grid(row=8, column=1, padx=10, pady=10)


# Eje Y
btn_y100_positivo = ttk.Button(root, text="100Y+", style='primary.Outline.TButton', command=y100_positivo)
btn_y100_positivo.grid(row=1, column=4, padx=10, pady=10)

btn_y10_positivo = ttk.Button(root, text="10Y+", style='primary.Outline.TButton', command=y10_positivo)
btn_y10_positivo.grid(row=2, column=4, padx=10, pady=10)

btn_y1_positivo = ttk.Button(root, text="1Y+", style='primary.Outline.TButton', command=y1_positivo)
btn_y1_positivo.grid(row=3, column=4, padx=10, pady=10)

btn_y1_negativo = ttk.Button(root, text="1Y-", style='primary.Outline.TButton', command=y1_negativo)
btn_y1_negativo.grid(row=5, column=4, padx=10, pady=10)

btn_y10_negativo = ttk.Button(root, text="10Y-", style='primary.Outline.TButton', command=y10_negativo)
btn_y10_negativo.grid(row=6, column=4, padx=10, pady=10)

btn_y100_negativo = ttk.Button(root, text="100Y-", style='primary.Outline.TButton', command=y100_negativo)
btn_y100_negativo.grid(row=7, column=4, padx=10, pady=10)

# Eje X
btn_x100_positivo = ttk.Button(root, text="100X+", style='primary.Outline.TButton', command=x100_positivo)
btn_x100_positivo.grid(row=4, column=7, padx=0, pady=0, sticky="w")

btn_x10_positivo = ttk.Button(root, text="10X+", style='primary.Outline.TButton', command=x10_positivo)
btn_x10_positivo.grid(row=4, column=6, padx=0, pady=0, sticky="w")

btn_x1_positivo = ttk.Button(root, text="1X+", style='primary.Outline.TButton', command=x1_positivo)
btn_x1_positivo.grid(row=4, column=5, padx=0, pady=0, sticky="w")

btn_x1_negativo = ttk.Button(root, text="1X-", style='primary.Outline.TButton', command=x1_negativo)
btn_x1_negativo.grid(row=4, column=3, padx=0, pady=0, sticky="e")

btn_x10_negativo = ttk.Button(root, text="10X-", style='primary.Outline.TButton', command=x10_negativo)
btn_x10_negativo.grid(row=4, column=2, padx=0, pady=0, sticky="e")

btn_x100_negativo = ttk.Button(root, text="100X-", style='primary.Outline.TButton', command=x100_negativo)
btn_x100_negativo.grid(row=4, column=1, padx=0, pady=0, sticky="e")

root.mainloop()