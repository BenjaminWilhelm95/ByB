import tkinter as tk
from tkinter import messagebox
from ttkbootstrap import Style
from ttkbootstrap.dialogs import Messagebox
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

"""def save_reading(x, y, reading):
    with open('Coordenadas_usadas.txt', 'a') as file:
        file.write(f"X: {x}, Y: {y}, PDD: {reading}\n")"""
import datetime
def save_reading(x, y, reading):
    # Obtener la fecha y hora actual en formato dd/mm/aa hh:mm:ss
    fecha_hora = datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")
    
    # Formatear el texto de salida para que sea más legible
    registro = f"Fecha/Hora: {fecha_hora}\nCoordenadas -> X: {x}, Y: {y}\nEstado PDD: {reading}\n{'-'*30}\n"
    
    # Guardar el registro en un archivo de texto
    with open('Coordenadas_usadas.txt', 'a') as file:
        file.write(registro)

import os 

def abrir_archivo():
    try:
        # Verificar si el archivo existe antes de intentar abrirlo
        if os.path.exists('Coordenadas_usadas.txt'):
            os.startfile('Coordenadas_usadas.txt')  # Solo en Windows
        else:
            messagebox.showwarning("Advertencia", "El archivo no existe aún.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

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
        x_pos += -x
        y_pos += -y
        label_x.config(text=f"Posición X: {x_pos}")
        label_y.config(text=f"Posición Y: {y_pos}")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Simulación de función que guardaría las lecturas (para mantener tu código funcional)
def save_reading(x, y, respuesta):
    pass  # Puedes implementar esta función como sea necesario

# Función para realizar el homing
def homing():
    if ser and ser.is_open:
        ser.write(b'$H \n')  # Comando de homing
        ser.flush()
        # Restablecer la posición a 0,0
        global x_pos, y_pos
        x_pos = 0
        y_pos = 0
        # Actualizar los labels
        label_x.config(text="Posición X: 0")
        label_y.config(text="Posición Y: 0")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

"""def recalibrar_origen():
    global x_pos, y_pos
    x_pos, y_pos = 0, 0
    label_x.config(text=f"Posición X: {x_pos}")
    label_y.config(text=f"Posición Y: {y_pos}")
    messagebox.showinfo("Calibración", "La posición (0,0) ha sido establecida en los fines de carrera.")"""


def desbloquear():
    if ser and ser.is_open:
        ser.write(b'$X \n')  # Comando de desbloquear
        ser.flush()
        messagebox.showinfo("Dispositivo desbloqueado, motores listos para mover")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

"""def calibrar():
    global x_pos, y_pos
    enviar_comando('G91\nG0 X{} Y{}\nG90'.format(-x_pos, -y_pos), -x_pos, -y_pos)
    x_pos, y_pos = 0, 0
    label_x.config(text=f"Posición X: {x_pos}")
    label_y.config(text=f"Posición Y: {y_pos}")"""

def detener_motores():
    if ser and ser.is_open:
        ser.write(b'! \n')  # Comando de pausa de emergencia en GRBL
        ser.flush()
        ser.write(b'\x18')  # Enviar el comando de reset (Ctrl+X) para cancelar el movimiento pendiente
        ser.flush()
        messagebox.showinfo("Motores detenidos", "Pulse reanudar para seguir moviéndolos")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

def reanudar_motores():
    if ser and ser.is_open:
        ser.write(b'$X \n')  
        ser.flush()
        ser.write(b'~\n')  # Comando de reanudar el movimiento en GRBL
        ser.flush()
        messagebox.showinfo("Motores reanudados", "Puedes seguir moviéndolos.")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")


def mover_distancia_x(distancia):
    enviar_comando(f'G91\nG0 X{distancia} Z{distancia}\nG90', distancia, 0)

def mover_distancia_y(distancia):
    enviar_comando(f'G91\nG0 X0 Y{distancia}\nG90', 0, distancia)

# Función para mostrar el messagebox con las opciones "Hacer Homing" o "Posición Actual"
def mostrar_messagebox():
    # Crear una ventana de diálogo personalizada
    messagebox_window = tk.Toplevel(root)
    messagebox_window.title("Configuración de Posición")

    # Etiqueta con la pregunta
    label = ttk.Label(messagebox_window, text="¿Desea hacer homing o usar la posición actual?", padding=10)
    label.pack(padx=20, pady=10)

    # Botones
    btn_homing = ttk.Button(messagebox_window, bootstyle="info", text="    Volver al origen    ", command=lambda: seleccionar_opcion(messagebox_window, "Homing"))
    btn_homing.pack(side="left", padx=10, pady=10)

    btn_posicion_actual = ttk.Button(messagebox_window,bootstyle="info", text="Usar Posición Actual", command=lambda: seleccionar_opcion(messagebox_window, "Posición Actual"))
    btn_posicion_actual.pack(side="right", padx=10, pady=10)

    # Hacer que la ventana sea modal
    messagebox_window.grab_set()  # Bloquea la interacción con la ventana principal
    messagebox_window.transient(root)  # Hace que la ventana esté sobre la principal

    ancho_ventana = 350
    alto_ventana = 109
    screen_width = messagebox_window.winfo_screenwidth()
    screen_height = messagebox_window.winfo_screenheight()
    x_centrado = (screen_width // 2) - (ancho_ventana // 2)
    y_centrado = (screen_height // 2) - (alto_ventana // 2)
    messagebox_window.geometry(f"{ancho_ventana}x{alto_ventana}+{x_centrado}+{y_centrado}")

# Función para manejar la opción seleccionada
def seleccionar_opcion(window, opcion):
    window.destroy()  # Cerrar el messagebox
    if opcion == "Homing":
        print("Iniciar Homing...")
        if ser and ser.is_open:
            ser.write(b'$H \n')  # Comando de pausa de emergencia en GRBL
            ser.flush()
        else:
            messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")
    elif opcion == "Posición Actual":
        print("Usar Posición Actual...")
        if ser and ser.is_open:
            ser.write(b'$X \n')  # Comando de pausa de emergencia en GRBL
            ser.flush()
        else:
            messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")
        # Aquí puedes continuar con la posición actual


# Funciones para los botones de movimiento
def x1_positivo():
    enviar_comando('G91\nG0 X-1 Z-1 \nG90', x=-1)

def x10_positivo():
    enviar_comando('G91\nG0 X-5 Z-5\nG90', x=-10)

def x100_positivo():
    enviar_comando('G91\nG0 X-10 Z-10\nG90', x=-50)

def x1_negativo():
    enviar_comando('G91\nG0 X1 Z1\nG90', x=1)

def x10_negativo():
    enviar_comando('G91\nG0 X5 Z5\nG90', x=10)

def x100_negativo():
    enviar_comando('G91\nG0 X10 Z10\nG90', x=50)

def y1_positivo():
    enviar_comando('G91\nG0 Y-1\nG90', y=-1)

def y10_positivo():
    enviar_comando('G91\nG0 Y-5\nG90',y=-5)

def y100_positivo():
    enviar_comando('G91\nG0 Y-10\nG90',y=-10)

def y1_negativo():
    enviar_comando('G91\nG0 Y1\nG90',y=1)

def y10_negativo():
    enviar_comando('G91\nG0 Y5\nG90',y=5)

def y100_negativo():
    enviar_comando('G91\nG0 Y10\nG90',y=10)

def centrar_ventana(root, ancho_ventana, alto_ventana):
    # Obtener dimensiones de la pantalla
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcular posición centrada
    x_centrado = (screen_width // 2) - (ancho_ventana // 2)
    y_centrado = (screen_height // 2) - (alto_ventana // 2)

    # Establecer geometría de la ventana
    root.geometry(f"{ancho_ventana}x{alto_ventana}+{x_centrado}+{y_centrado}")
# Crear la interfaz gráfica
root = tk.Tk()
root.title("Control de dosímetro")
root.after(100, mostrar_messagebox)  # Muestra el messagebox después de 100 ms

ancho_ventana = 780  
alto_ventana = 250
centrar_ventana(root, ancho_ventana, alto_ventana)

# Labels para mostrar la posición actual
label_x = ttk.Label(root, bootstyle="dark", text=f"Posición X: {x_pos}")
label_x.grid(row=0, column=5)

label_y = ttk.Label(root, bootstyle="dark", text=f"Posición Y: {y_pos}")
label_y.grid(row=1, column=5)

# Entradas para mover a una distancia específica
entry_manual_x = tk.Entry(root)
entry_manual_x.grid(row=0, column=2)
entry_manual_x.insert(0, "0")

entry_manual_y = tk.Entry(root)
entry_manual_y.grid(row=1, column=2)
entry_manual_y.insert(0, "0")

# Función para realizar el barrido en el eje XY
import time  # Para usar la función de pausa

def realizar_barrido(distancia_escaneo_y, tiempo_espera, distancia_escaneo_x, repeticiones):

    for repeticion in range(repeticiones):
        print(f"\nIniciando repetición {repeticion + 1}")

        # Mover en eje Y (ascendente)
        for paso_y in range(int(distancia_escaneo_y)):
            enviar_comando(f'G91\nG0 Y1\nG90', y=1)  # Mover 1 paso en Y
            time.sleep(tiempo_espera)  # Pausar entre movimientos
            print(f"Moviendo +1 en Y, paso {paso_y + 1}")

        # Mover en eje X después de terminar los movimientos en Y
        for paso_x in range(int(distancia_escaneo_x)):
            enviar_comando(f'G91\nG0 X1\nG90', x=1)  # Mover 1 paso en X
            time.sleep(tiempo_espera)  # Pausar entre movimientos en X
            print(f"Moviendo +1 en X, paso {paso_x + 1}")

        # Mover en eje Y (descendente, regresando)
        for paso_y in range(int(distancia_escaneo_y)):
            enviar_comando(f'G91\nG0 Y-1\nG90', y=-1)  # Mover -1 paso en Y
            time.sleep(tiempo_espera)  # Pausar entre movimientos
            print(f"Moviendo -1 en Y, paso {paso_y + 1}")

       # Mover en eje X (ascendente), paso a paso
        for paso_x in range(int(distancia_escaneo_x)):
            enviar_comando(f'G91\nG0 X1\nG90', x=1)  # Mover 1 paso en X
            time.sleep(tiempo_espera)  # Pausar entre movimientos en X
            print(f"Moviendo +1 en X, paso {paso_x + 1}")

        # Pausa al final de cada repetición para respetar el tiempo antes de la siguiente repetición
        print(f"Esperando {tiempo_espera} segundos antes de iniciar la repetición {repeticion + 2}")
        time.sleep(tiempo_espera)  # Pausa antes de iniciar la nueva repetición
    print("Proceso de barrido completado.")


# Botones "+" y "-" para mover a la distancia especificada en X
def incrementar_x():
    mover_distancia_x(-int(entry_manual_x.get()))
    
def decrementar_x():
    mover_distancia_x(int(entry_manual_x.get()))

btn_x_mas = ttk.Button(root, bootstyle="black_link", text="+", command=incrementar_x)
btn_x_mas.grid(row=0, column=3)

btn_x_menos = ttk.Button(root, bootstyle="black_link", text="-", command=decrementar_x)
btn_x_menos.grid(row=0, column=1)

# Botones "+" y "-" para mover a la distancia especificada en Y
def incrementar_y():
    mover_distancia_y(-int(entry_manual_y.get()))

def decrementar_y():
    mover_distancia_y(int(entry_manual_y.get()))

btn_y_mas = ttk.Button(root, bootstyle="dark_link", text="+", command=incrementar_y)
btn_y_mas.grid(row=1, column=3, padx=10, pady=10)

btn_y_menos = ttk.Button(root,bootstyle="dark_link", text="-", command=decrementar_y)
btn_y_menos.grid(row=1, column=1, padx=10, pady=10)

btn_iniciar = ttk.Button(root, bootstyle="danger_outline", text="  Detener motores   ", command=detener_motores)
btn_iniciar.grid(row=3, column=0, padx=10, pady=10)

btn_iniciar = ttk.Button(root, bootstyle="success_outline", text="  Reanudar motores  ", command=reanudar_motores)
btn_iniciar.grid(row=2, column=0, padx=10, pady=10)

btn_calibrar = ttk.Button(root,bootstyle="warning_outline", text="Posicionar en origen", command=homing)
btn_calibrar.grid(row=1, column=0, padx=10, pady=10)

# Función para mostrar la ventana de intervalos
def show_interval_window():
    interval_window = tk.Toplevel(root)
    interval_window.title("Mover manualmente")

    # Definir el tamaño de la ventana
    ancho_ventana = 570
    alto_ventana = 270

    # Centrar la ventana secundaria
    centrar_ventana(interval_window, ancho_ventana, alto_ventana)

    # Crear un frame dentro de la ventana secundaria
    frame_calibrar = ttk.Frame(interval_window)
    frame_calibrar.grid(row=4, column=3, columnspan=12, padx=10, pady=10)

    # Labels para mostrar la posición actual
    label_x = ttk.Label(interval_window, text=f"Posición X: {x_pos}")
    label_x.grid(row=0, column=7, columnspan=2)

    label_y = ttk.Label(interval_window, text=f"Posición Y: {y_pos}")
    label_y.grid(row=1, column=7, columnspan=2)

#Boton calibrar
    ttk.Labelframe(interval_window, text="").grid(row=0, column=0, padx=0, pady=0)
# Botones de Eje Y
    ttk.Button(interval_window, text="  10Y ", bootstyle="dark_outline", command=y100_positivo).grid(row=0, column=3, padx=0, pady=5)
    ttk.Button(interval_window, text="  5Y  ", bootstyle="dark_outline", command=y10_positivo).grid(row=1, column=3, padx=0, pady=5)
    ttk.Button(interval_window, text="  1Y  ", bootstyle="dark_outline", command=y1_positivo).grid(row=4, column=3, padx=0, pady=5)
    ttk.Button(interval_window, text=" -1Y  ", bootstyle="dark_outline", command=y1_negativo).grid(row=6, column=3, padx=0, pady=5)
    ttk.Button(interval_window, text=" -5Y  ", bootstyle="dark_outline", command=y10_negativo).grid(row=7, column=3, padx=0, pady=5)
    ttk.Button(interval_window, text=" -10Y ", bootstyle="dark_outline", command=y100_negativo).grid(row=8, column=3, padx=0, pady=5)

    # Botones de Eje X
    ttk.Button(interval_window, text="  50X ", bootstyle="dark_outline", command=x100_positivo).grid(row=5, column=6, padx=5, pady=0)
    ttk.Button(interval_window, text="  10X ", bootstyle="dark_outline", command=x10_positivo).grid(row=5, column=5, padx=5, pady=0)
    ttk.Button(interval_window, text="  1X  ", bootstyle="dark_outline", command=x1_positivo).grid(row=5, column=4, padx=5, pady=0)
    ttk.Button(interval_window, text=" -1X  ", bootstyle="dark_outline", command=x1_negativo).grid(row=5, column=2, padx=5, pady=0)
    ttk.Button(interval_window, text=" -10X ", bootstyle="dark_outline", command=x10_negativo).grid(row=5, column=1, padx=5, pady=0)
    ttk.Button(interval_window, text=" -50X ", bootstyle="dark_outline", command=x100_negativo).grid(row=5, column=0, padx=5, pady=0)
    
    #Funciones de botón
    ttk.Button(interval_window, text="  Reanudar motores  ", bootstyle="success_outline", command=reanudar_motores).grid(row=7, column=7, padx=0, pady=5)
    ttk.Button(interval_window, text="  Detener motores    ", bootstyle="danger_outline", command=detener_motores).grid(row=8, column=7, padx=0, pady=5)
    ttk.Button(interval_window, text="Posicionar en origen", bootstyle="warning_outline", command=homing).grid(row=4, column=7, padx=0, pady=5)




# Crear el botón "Mover por intervalos"
btn_intervalos = ttk.Button(root, bootstyle="info_outline", text="Movimiento manual", command=show_interval_window)
btn_intervalos.grid(row=0, column=0, padx=10, pady=10)

# Etiquetas y cuadros de texto
ttk.Label(root, text="Distancia a mover en Y:").grid(row=0, column=6, padx=10, pady=5)
entry_distancia_y = tk.Entry(root)
entry_distancia_y.grid(row=0, column=7, padx=10, pady=5)

# Etiquetas y cuadros de texto para el eje X
ttk.Label(root, text="Distancia a mover en X:").grid(row=1, column=6, padx=10, pady=5)
entry_distancia_x = tk.Entry(root)
entry_distancia_x.grid(row=1, column=7, padx=10, pady=5)

ttk.Label(root, text="Tiempo de espera (segundos):").grid(row=2, column=6, padx=10, pady=5)
entry_tiempo = tk.Entry(root)
entry_tiempo.grid(row=2, column=7, padx=10, pady=5)

# Etiqueta y cuadro de texto para las repeticiones
tk.Label(root, text="Número de repeticiones:").grid(row=3, column=6, padx=10, pady=5)
entry_repeticiones = tk.Entry(root)
entry_repeticiones.grid(row=3, column=7, padx=10, pady=5)

def iniciar_barrido():
    try:
        # Obtener los valores de las entradas
        distancia_escaneo_y = float(entry_distancia_y.get())  # Obtener la distancia total a recorrer en Y
        tiempo_espera = float(entry_tiempo.get())  # Obtener el tiempo de espera entre movimientos 
        distancia_escaneo_x = float(entry_distancia_x.get())  # Obtener la distancia en X
        repeticiones = int(entry_repeticiones.get())  # Obtener cuántas veces repetir el proceso

        # Llamar a la función de barrido con los valores obtenidos
        realizar_barrido(distancia_escaneo_y, tiempo_espera, distancia_escaneo_x, repeticiones)
    
    except ValueError:
        # Manejar el caso en que las entradas no son válidas
        messagebox.showerror("Error", "Por favor, ingrese valores numéricos válidos para todos los campos.")

# Código para agregar el botón en tu interfaz (Tkinter/ttkbootstrap)
btn_abrir_archivo = ttk.Button(root,bootstyle="secondary_outline", text=" Abrir Coordenadas ", command=abrir_archivo)
btn_abrir_archivo.grid(row=4, column=0, padx=10, pady=10)

# Botón para iniciar el barrido
btn_barrido = ttk.Button(root, bootstyle="primary_outline", text="Iniciar Barrido", command=iniciar_barrido)
btn_barrido.grid(row=4, column=7, padx=10, pady=10)

root.mainloop()

"""
Fecha/Hora: 01/10/24 14:32:45
Coordenadas -> X: 10, Y: 5
Estado PDD: ok
------------------------------
Fecha/Hora: 01/10/24 14:33:10
Coordenadas -> X: 11, Y: 6
Estado PDD: ok
------------------------------
Fecha/Hora: 01/10/24 14:34:00
Coordenadas -> X: 12, Y: 7
Estado PDD: ok
------------------------------
"""