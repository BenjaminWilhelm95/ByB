import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports
import time
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
    enviar_comando('G91\nG0 X1 Z1 \nG90', 1, 0)

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
    enviar_comando('G91\nG0 Y1\nG90', 0, 0.25)

def y10_positivo():
    enviar_comando('G91\nG0 Y10\nG90', 0, 10)

def y100_positivo():
    enviar_comando('G91\nG0 Y100\nG90', 0, 100)

def y1_negativo():
    enviar_comando('G91\nG0 Y-1\nG90', 0, -1)

def y10_negativo():
    enviar_comando('G91\nG0 Y-10\nG90', 0, -10)

def y100_negativo():
    enviar_comando('G91\nG0 Y-100\nG90', 0, -100)

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
root.title("Control de dosímetro")

# Labels para mostrar la posición actual
label_x = tk.Label(root, text=f"Posición X: {x_pos}")
label_x.grid(row=0, column=3, columnspan=2)

label_y = tk.Label(root, text=f"Posición Y: {y_pos}")
label_y.grid(row=1, column=3, columnspan=2)

# Entradas para mover a una distancia específica
entry_distancia_x = tk.Entry(root)
entry_distancia_x.grid(row=0, column=1)
entry_distancia_x.insert(0, "0")

entry_distancia_y = tk.Entry(root)
entry_distancia_y.grid(row=1, column=1)
entry_distancia_y.insert(0, "0")

# Función para realizar el barrido en el eje XY
def realizar_barrido():
    try:
        distancia_escaneo_y = float(entry_distancia.get())  # Obtener la distancia total a recorrer
        intervalo = float(entry_intervalo.get())  # Obtener el intervalo de movimiento
        tiempo_espera = float(entry_tiempo.get())  # Obtener el tiempo de espera entre pasos
        distancia_escaneo_x = float(entry_distancia_x.get())  # Obtener la distancia en X
        repeticiones = int(entry_repeticiones.get())  # Obtener cuántas veces repetir el proceso


        pasos = int(distancia_escaneo_y // intervalo)  # Calcular cuántos pasos se deben hacer
        distancia_restante = distancia_escaneo_y % intervalo  # Por si queda una pequeña distancia final

        # Repetir el proceso de barrido las veces indicadas
        for repeticion in range(repeticiones):
            print(f"Iniciando barrido {repeticion + 1} de {repeticiones}...")
            
            # Si no es la primera repetición, primero mover en X
            if repeticion > 0:
                enviar_comando(f'G91\nG0 X{distancia_escaneo_x}\nG90')
                print(f"Movido {distancia_escaneo_x} unidades en X (subida en la repetición {repeticion + 1}).")

            # Mover en pasos regulares en Y
            for i in range(pasos):
                enviar_comando(f'G91\nG0 Y{intervalo}\nG90')  # Movimiento incremental en Y
                print(f"Movido {intervalo} unidades en Y. Paso {i + 1} de {pasos}.")
                time.sleep(tiempo_espera)  # Esperar el tiempo especificado

            # Mover la distancia restante en Y si es diferente de 0
            if distancia_restante > 0:
                enviar_comando(f'G91\nG0 Y{distancia_restante}\nG90')
                print(f"Movido la distancia restante de {distancia_restante} unidades en Y.")

            # Mover en X la distancia especificada
            enviar_comando(f'G91\nG0 X{distancia_escaneo_x}\nG90')
            print(f"Movido {distancia_escaneo_x} unidades en X.")

            # Regresar en Y la distancia total recorrida (en negativo)
            for i in range(pasos):
                enviar_comando(f'G91\nG0 Y-{intervalo}\nG90')  # Movimiento incremental en Y
                print(f"Regresado {-intervalo} unidades en Y. Paso {i + 1} de {pasos}.")
                time.sleep(tiempo_espera)  # Esperar el tiempo especificado

            # Regresar la distancia restante en Y si es diferente de 0
            if distancia_restante > 0:
                enviar_comando(f'G91\nG0 Y-{distancia_restante}\nG90')
                print(f"Regresado la distancia restante de {-distancia_restante} unidades en Y.")

        # Mostrar mensaje de que el proceso ha terminado
        messagebox.showinfo("Barrido completado", f"El barrido se repitió {repeticiones} veces y ha finalizado.")

    except ValueError:
        messagebox.showerror("Error", "Por favor, ingrese números válidos para la distancia, intervalo, tiempo y repeticiones.")
# Botones "+" y "-" para mover a la distancia especificada en X
def incrementar_x():
    mover_distancia_x(int(entry_distancia_x.get()))

def decrementar_x():
    mover_distancia_x(-int(entry_distancia_x.get()))

btn_x_mas = ttk.Button(root, text="+", command=incrementar_x)
btn_x_mas.grid(row=0, column=2)

btn_x_menos = ttk.Button(root, text="-", command=decrementar_x)
btn_x_menos.grid(row=0, column=0)

# Botones "+" y "-" para mover a la distancia especificada en Y
def incrementar_y():
    mover_distancia_y(int(entry_distancia_y.get()))

def decrementar_y():
    mover_distancia_y(-int(entry_distancia_y.get()))

btn_y_mas = ttk.Button(root, text="+", command=incrementar_y)
btn_y_mas.grid(row=1, column=2, padx=10, pady=10)

btn_y_menos = ttk.Button(root, text="-", command=decrementar_y)
btn_y_menos.grid(row=1, column=0, padx=10, pady=10)

btn_iniciar = ttk.Button(root, text="Detener", command=parada_emergencia,style='primary.TButton')
btn_iniciar.grid(row=8, column=0, padx=10, pady=10)

btn_calibrar = ttk.Button(root, text="Homing", command=homing)
btn_calibrar.grid(row=8, column=1, padx=10, pady=10)

# Función para mostrar la ventana de intervalos
def show_interval_window():
    interval_window = tk.Toplevel(root)
    interval_window.title("Mover por Intervalos")
    frame_calibrar = tk.Frame(interval_window)
    frame_calibrar.grid(row=4, column=3, columnspan=12, padx=10, pady=10)

#Boton calibrar
    ttk.Button(frame_calibrar, text="Calibrar", style='primary.Outline.TButton', command=calibrar).grid(row=0, column=0, padx=10,pady=10)

# Botones de Eje Y
    ttk.Button(interval_window, text="100Y+", style='primary.Outline.TButton', command=y100_positivo).grid(row=1, column=6, padx=10, pady=10)
    ttk.Button(interval_window, text="10Y+", style='primary.Outline.TButton', command=y10_positivo).grid(row=2, column=6, padx=10, pady=10)
    ttk.Button(interval_window, text="1Y+", style='primary.Outline.TButton', command=y1_positivo).grid(row=3, column=6, padx=10, pady=10)
    ttk.Button(interval_window, text="1Y-", style='primary.Outline.TButton', command=y1_negativo).grid(row=5, column=6, padx=10, pady=10)
    ttk.Button(interval_window, text="10Y-", style='primary.Outline.TButton', command=y10_negativo).grid(row=6, column=6, padx=10, pady=10)
    ttk.Button(interval_window, text="100Y-", style='primary.Outline.TButton', command=y100_negativo).grid(row=7, column=6, padx=10, pady=10)

    # Botones de Eje X
    ttk.Button(interval_window, text="100X+", style='primary.Outline.TButton', command=x100_positivo).grid(row=4, column=9, padx=10, pady=10)
    ttk.Button(interval_window, text="10X+", style='primary.Outline.TButton', command=x10_positivo).grid(row=4, column=8, padx=10, pady=10)
    ttk.Button(interval_window, text="1X+", style='primary.Outline.TButton', command=x1_positivo).grid(row=4, column=7, padx=10, pady=10)
    ttk.Button(interval_window, text="1X-", style='primary.Outline.TButton', command=x1_negativo).grid(row=4, column=5, padx=10, pady=10)
    ttk.Button(interval_window, text="10X-", style='primary.Outline.TButton', command=x10_negativo).grid(row=4, column=4, padx=10, pady=10)
    ttk.Button(interval_window, text="100X-", style='primary.Outline.TButton', command=x100_negativo).grid(row=4, column=3, padx=10, pady=10)


# Crear el botón "Mover por intervalos"
btn_intervalos = ttk.Button(root, text="Mover Manual", command=show_interval_window)
btn_intervalos.grid(row=8, column=3, padx=10, pady=10)

# Etiquetas y cuadros de texto
tk.Label(root, text="Distancia total a recorrer:").grid(row=0, column=8, padx=10, pady=5)
entry_distancia = tk.Entry(root)
entry_distancia.grid(row=0, column=9, padx=10, pady=5)

tk.Label(root, text="Intervalo de movimiento:").grid(row=1, column=8, padx=10, pady=5)
entry_intervalo = tk.Entry(root)
entry_intervalo.grid(row=1, column=9, padx=10, pady=5)

tk.Label(root, text="Tiempo de espera (segundos):").grid(row=2, column=8, padx=10, pady=5)
entry_tiempo = tk.Entry(root)
entry_tiempo.grid(row=2, column=9, padx=10, pady=5)

# Etiquetas y cuadros de texto para el eje X
tk.Label(root, text="Distancia a mover en X:").grid(row=3, column=8, padx=10, pady=5)
entry_distancia_x = tk.Entry(root)
entry_distancia_x.grid(row=3, column=9, padx=10, pady=5)

# Botón para iniciar el barrido
btn_barrido = tk.Button(root, text="Iniciar Barrido", command=realizar_barrido)
btn_barrido.grid(row=5, column=9, columnspan=2, padx=10, pady=10)

# Etiqueta y cuadro de texto para las repeticiones
tk.Label(root, text="Número de repeticiones:").grid(row=4, column=8, padx=10, pady=5)
entry_repeticiones = tk.Entry(root)
entry_repeticiones.grid(row=4, column=9, padx=10, pady=5)

root.mainloop()