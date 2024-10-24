#Barrido corregido y ahora se corregiran las posiciones
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

# Posiciones en milímetros
x_pos_mm = 0
y_pos_mm = 0

def pasos_a_mm_x(pasos):
    return pasos / 0.0805  # Conversión para el eje X

def pasos_a_mm_y(pasos):
    return pasos / 0.4  # Conversión para el eje Y

def mm_a_pasos_x(mm):
    return mm * 0.0805  # Conversión para el eje X

def mm_a_pasos_y(mm):
    return mm * 0.4  # Conversión para el eje Y



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

# Límites del área de movimiento en milímetros
X_MIN, X_MAX = 0, 170  # Limite en X
Y_MIN, Y_MAX = 0, 120  # Limite en Y


# Actualizar posición X
def actualizar_x(nueva_x_pasos):
    global x_pos, x_pos_mm
    x_pos = nueva_x_pasos
    x_pos_mm = round(pasos_a_mm_x(x_pos))  
    
# Actualizar posición Y
def actualizar_y(nueva_y_pasos):
    global y_pos, y_pos_mm
    y_pos = nueva_y_pasos
    y_pos_mm = round(pasos_a_mm_y(y_pos))  
    label_y.config(text=f"Posición Y: {y_pos_mm} mm")

# Verificación de límites para el área de trabajo
#También se intervino
def verificar_limites(x_nueva_pasos, y_nueva_pasos):
    # Ensure the new positions are within bounds
    return (X_MIN <= pasos_a_mm_x(x_nueva_pasos) <= X_MAX) and (Y_MIN <= pasos_a_mm_y(y_nueva_pasos) <= Y_MAX)

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
        label_x.config(text=f"Posición X: {x_pos} mm")
        label_y.config(text=f"Posición Y: {y_pos} mm")
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
        label_x.config(text="Posición X: 0 mm")
        label_y.config(text="Posición Y: 0 mm")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

def desbloquear():
    if ser and ser.is_open:
        ser.write(b'$X \n')  # Comando de desbloquear
        ser.flush()
        messagebox.showinfo("Dispositivo desbloqueado, motores listos para mover")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

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

"""Avance 18 de octubre se cambia esta función, se añade verificar limites"""

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

# Función para mostrar advertencias cuando se exceden los límites
def mostrar_advertencia(eje, nueva_pos):
    messagebox.showwarning("Límite excedido", f"No se puede mover el eje {eje} a {nueva_pos} mm, excede los límites.")

# Funciones para los botones de movimiento
#Se intervino y suma bien, hay que replicar en resto de ejes y probar limites
def x1_positivo():
    nueva_x_pasos = x_pos + mm_a_pasos_x(1)  
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y0.0805\nG90', x=1)  
        actualizar_x(nueva_x_pasos)  
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))  

def x10_positivo():
    nueva_x_pasos = x_pos + mm_a_pasos_x(5)  # Nueva posición en mm (moviendo 5 mm)
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y0.4025 \nG90', x=5)
        actualizar_x(nueva_x_pasos)
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))

def x100_positivo():
    nueva_x_pasos = x_pos + mm_a_pasos_x(10)   
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y0.805 \nG90', x=10)
        actualizar_x(nueva_x_pasos)
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))

def x1_negativo():
    nueva_x_pasos = x_pos - mm_a_pasos_x(1)  # Convert 1mm to steps
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y-0.0805\nG90', x=-1)
        actualizar_x(nueva_x_pasos)
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))

def x10_negativo():
    nueva_x_pasos = x_pos - mm_a_pasos_x(5)
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y-0.4025\nG90', x=-5)
        actualizar_x(nueva_x_pasos)
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))    

def x100_negativo():
    nueva_x_pasos = x_pos - mm_a_pasos_x(10)
    if verificar_limites(nueva_x_pasos, y_pos):
        enviar_comando('G91\nG0 Y-0.805\nG90', x=-10)
        actualizar_x(nueva_x_pasos)
    else:
        mostrar_advertencia("X", pasos_a_mm_x(nueva_x_pasos))    

def y1_positivo():
    nueva_y_pasos = y_pos + mm_a_pasos_y(1)
    if verificar_limites(x_pos, nueva_y_pasos):
        enviar_comando('G91\nG0 X0.4 Z0.4\nG90', y=1) # 1Y
        actualizar_y(nueva_y_pasos)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos))    

def y10_positivo():
    nueva_y_pasos = y_pos + mm_a_pasos_y(5)
    if verificar_limites(x_pos, nueva_y_pasos):
        enviar_comando('G91\nG0 X2 Z2\nG90',y=5)
        actualizar_y(nueva_y_pasos)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos))  

def y100_positivo():
    nueva_y_pasos = y_pos + mm_a_pasos_y(10)
    if verificar_limites(x_pos, nueva_y_pasos	):
        enviar_comando('G91\nG0 X4 Z4\nG90',y=10)
        actualizar_y(nueva_y_pasos)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos))     

def y1_negativo():
    nueva_y_pasos = y_pos - mm_a_pasos_y(1)
    if verificar_limites(x_pos, nueva_y_pasos):
        enviar_comando('G91\nG0 X-0.4 Z-0.4\nG90',y=-1) # -1Y
        actualizar_y(nueva_y_pasos)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos))  

def y10_negativo():
    nueva_y_pasos = y_pos - mm_a_pasos_y(5)
    if verificar_limites(x_pos, nueva_y_pasos):
        enviar_comando('G91\nG0 X-2 Z-2\nG90',y=-5)
        actualizar_y(nueva_y_pasos)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos)) 

def y100_negativo():
    nueva_y_pasos = y_pos - mm_a_pasos_y(10)
    if verificar_limites(x_pos, nueva_y_pasos):
        enviar_comando('G91\nG0 X-4 Z-4\nG90',y=-10)
        actualizar_y(nueva_y_pasos	)
    else:
        mostrar_advertencia("Y", pasos_a_mm_y(nueva_y_pasos)) 

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

ancho_ventana = 650 
alto_ventana = 245
centrar_ventana(root, ancho_ventana, alto_ventana)

# Labels para mostrar la posición actual
label_x = ttk.Label(root, bootstyle="dark", text=f"Posición X: {x_pos} mm")
label_x.grid(row=0, column=6)

label_y = ttk.Label(root, bootstyle="dark", text=f"Posición Y: {y_pos} mm")
label_y.grid(row=1, column=6)

# Función para realizar el barrido en el eje XY
import time  # Para usar la función de pausa

def realizar_barrido(distancia_escaneo_y, tiempo_espera, distancia_escaneo_x, repeticiones):

    for repeticion in range(repeticiones):
        print(f"\nIniciando repetición {repeticion + 1}")

        # Mover en eje X (Ascendente)
        for paso_x in range(int(distancia_escaneo_x)):
            enviar_comando(f'G91\nG0 Y0.0805\nG90', x=1)  # Mover 1 paso en X
            time.sleep(tiempo_espera)  # Pausar entre movimientos en X
            print(f"Moviendo +1 en X, paso {paso_x + 1}")

        # Mover en eje Y (Descendente)
        for paso_y in range(int(distancia_escaneo_y)):
            enviar_comando(f'G91\nG0 X0.4 Z0.4 \nG90', y=-1)  # Mover 1 paso en Y
            time.sleep(tiempo_espera)  # Pausar entre movimientos
            print(f"Moviendo +1 en Y, paso {paso_y + 1}")

       # Mover en eje X (Descendente), paso a paso
        for paso_x in range(int(distancia_escaneo_x)):
            enviar_comando(f'G91\nG0 Y-0.0805\nG90', x=-1)  # Mover 1 paso en X
            time.sleep(tiempo_espera)  # Pausar entre movimientos en X
            print(f"Moviendo +1 en X, paso {paso_x + 1}")

        # Mover en eje Y (descendente)
        for paso_y in range(int(distancia_escaneo_y)):
            enviar_comando(f'G91\nG0 X0.4 Z0.4 \nG90', y=-1)  # Mover -1 paso en Y
            time.sleep(tiempo_espera)  # Pausar entre movimientos
            print(f"Moviendo -1 en Y, paso {paso_y + 1}")

        # Pausa al final de cada repetición para respetar el tiempo antes de la siguiente repetición
        print(f"Esperando {tiempo_espera} segundos antes de iniciar la repetición {repeticion + 2}")
        time.sleep(tiempo_espera)  # Pausa antes de iniciar la nueva repetición
    print("Proceso de barrido completado.")

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
    ancho_ventana = 685
    alto_ventana = 285

    # Centrar la ventana secundaria
    centrar_ventana(interval_window, ancho_ventana, alto_ventana)
    #Se añade esto 18 de octubre

    # Hacer que la ventana de intervalos esté sobre la ventana principal
    interval_window.transient(root)  # Hace que la ventana secundaria esté siempre sobre la ventana principal
    interval_window.grab_set()  # Bloquea la interacción con la ventana principal hasta que se cierre la secundaria

    # Crear un frame dentro de la ventana secundaria
    frame_calibrar = ttk.Frame(interval_window)
    frame_calibrar.grid(row=4, column=3, columnspan=12, padx=10, pady=10)

    """Avance 18 de octubre, se cambia de Y a mm"""
    ttk.Labelframe(interval_window, text="").grid(row=5, column=4, padx=0, pady=0)

# Botones de Eje Y
    ttk.Label(interval_window, text=" Y ").grid(row=0, column=4)
    ttk.Button(interval_window, text="  10mm ", bootstyle="dark_outline", command=y100_positivo).grid(row=1, column=4, padx=0, pady=5)
    ttk.Button(interval_window, text="  5mm  ", bootstyle="dark_outline", command=y10_positivo).grid(row=2, column=4, padx=0, pady=5)
    ttk.Button(interval_window, text="  1mm  ", bootstyle="dark_outline", command=y1_positivo).grid(row=3, column=4, padx=0, pady=5)
    ttk.Button(interval_window, text=" -1mm  ", bootstyle="dark_outline", command=y1_negativo).grid(row=5, column=4, padx=0, pady=5)
    ttk.Button(interval_window, text=" -5mm  ", bootstyle="dark_outline", command=y10_negativo).grid(row=6, column=4, padx=0, pady=5)
    ttk.Button(interval_window, text=" -10mm ", bootstyle="dark_outline", command=y100_negativo).grid(row=7, column=4, padx=0, pady=5)

    # Botones de Eje X
    ttk.Label(interval_window, text=" X ").grid(row=4, column=0)
    ttk.Button(interval_window, text="  10mm ", bootstyle="dark_outline", command=x100_positivo).grid(row=4, column=7, padx=5, pady=0)
    ttk.Button(interval_window, text="  5mm  ", bootstyle="dark_outline", command=x10_positivo).grid(row=4, column=6, padx=5, pady=0)
    ttk.Button(interval_window, text="  1mm  ", bootstyle="dark_outline", command=x1_positivo).grid(row=4, column=5, padx=5, pady=0)
    ttk.Button(interval_window, text=" -1mm  ", bootstyle="dark_outline", command=x1_negativo).grid(row=4, column=3, padx=5, pady=0)
    ttk.Button(interval_window, text=" -5mm  ", bootstyle="dark_outline", command=x10_negativo).grid(row=4, column=2, padx=5, pady=0)
    ttk.Button(interval_window, text=" -10mm ", bootstyle="dark_outline", command=x100_negativo).grid(row=4, column=1, padx=5, pady=0)
    
    #Funciones de botón
    ttk.Button(interval_window, text="  Reanudar motores   ", bootstyle="success_outline", command=reanudar_motores).grid(row=6, column=8, padx=0, pady=5)
    ttk.Button(interval_window, text="  Detener motores    ", bootstyle="danger_outline", command=detener_motores).grid(row=7, column=8, padx=0, pady=5)
    ttk.Button(interval_window, text="Posicionar en origen ", bootstyle="warning_outline", command=homing).grid(row=5, column=8, padx=0, pady=5)




# Crear el botón "Mover por intervalos"
btn_intervalos = ttk.Button(root, bootstyle="info_outline", text="Movimiento manual", command=show_interval_window)
btn_intervalos.grid(row=0, column=0, padx=10, pady=10)

# Variable para saber en qué fase del ciclo estamos (avance o regreso)
ciclo_movimiento = {'X': 0, 'Y': 0}  # Ciclo en X y Y, 0 = no se ha movido, >0 = movimiento en progreso

def mover_manual():
    try:
        # Obtener los valores de las entradas
        delta_x = float(Delta_x.get()) * 0.0805  # Convertir Delta X a pasos
        delta_y = float(Delta_y.get()) * 0.4     # Convertir Delta Y a pasos

        x_positivo = int(X_positivo.get())  # Cuántas veces moverse en X+
        x_negativo = int(X_negativo.get())  # Cuántas veces moverse en X-
        y_positivo = int(Y_positivo.get())  # Cuántas veces moverse en Y+
        y_negativo = int(Y_negativo.get())  # Cuántas veces moverse en Y-

        # Movimiento en X+ (usando motor Y)
        if x_positivo > 0:
            # Mover manualmente uno por uno
            if ciclo_movimiento['X'] < x_positivo:  # Si no hemos completado X+ movimientos
                nueva_x = x_pos + delta_x
                if verificar_limites(nueva_x, y_pos):
                    enviar_comando(f'G91\nG0 Y{delta_x}\nG90', delta_x, 0)
                    ciclo_movimiento['X'] += 1  # Incrementar el ciclo de movimientos
                else:
                    mostrar_advertencia("X", nueva_x)
            else:  # Si ya hemos completado los X+ movimientos, retroceder
                enviar_comando(f'G91\nG0 Y{-delta_x * x_positivo}\nG90', -delta_x * x_positivo, 0)
                ciclo_movimiento['X'] = 0  # Resetear el ciclo de X+
                X_positivo.delete(0, tk.END)
                X_positivo.insert(0, "0")  # Resetear los pasos X+

        # Movimiento en X- (usando motor Y)
        elif x_negativo > 0:
            if ciclo_movimiento['X'] < x_negativo:
                nueva_x = x_pos - delta_x
                if verificar_limites(nueva_x, y_pos):
                    enviar_comando(f'G91\nG0 Y{-delta_x}\nG90', -delta_x, 0)
                    ciclo_movimiento['X'] += 1  # Incrementar el ciclo de movimientos
                else:
                    mostrar_advertencia("X", nueva_x)
            else:
                enviar_comando(f'G91\nG0 Y{delta_x * x_negativo}\nG90', delta_x * x_negativo, 0)
                actualizar_x(x_pos)  # Volver a la posición original
                ciclo_movimiento['X'] = 0  # Resetear el ciclo de X-
                X_negativo.delete(0, tk.END)
                X_negativo.insert(0, "0")  # Resetear los pasos X-

        # Movimiento en Y+ (usando motores X y Z)
        elif y_positivo > 0:
            if ciclo_movimiento['Y'] < y_positivo:
                nueva_y = y_pos + delta_y
                if verificar_limites(x_pos, nueva_y):
                    enviar_comando(f'G91\nG0 X{delta_y} Z{delta_y}\nG90', 0, delta_y)
                    ciclo_movimiento['Y'] += 1  # Incrementar el ciclo de movimientos
                else:
                    mostrar_advertencia("Y", nueva_y)
            else:
                enviar_comando(f'G91\nG0 X{-delta_y * y_positivo} Z{-delta_y * y_positivo}\nG90', 0, -delta_y * y_positivo)
                ciclo_movimiento['Y'] = 0  # Resetear el ciclo de Y+
                Y_positivo.delete(0, tk.END)
                Y_positivo.insert(0, "0")  # Resetear los pasos Y+

        # Movimiento en Y- (usando motores X y Z)
        elif y_negativo > 0:
            if ciclo_movimiento['Y'] < y_negativo:
                nueva_y = y_pos - delta_y
                if verificar_limites(x_pos, nueva_y):
                    enviar_comando(f'G91\nG0 X{-delta_y} Z{-delta_y}\nG90', 0, -delta_y)
                    ciclo_movimiento['Y'] += 1  # Incrementar el ciclo de movimientos
                else:
                    mostrar_advertencia("Y", nueva_y)
            else:
                enviar_comando(f'G91\nG0 X{delta_y * y_negativo} Z{delta_y * y_negativo}\nG90', 0, delta_y * y_negativo)
                ciclo_movimiento['Y'] = 0  # Resetear el ciclo de Y-
                Y_negativo.delete(0, tk.END)
                Y_negativo.insert(0, "0")  # Resetear los pasos Y-

        else:
            messagebox.showinfo("Movimiento Manual", "Todos los movimientos han sido completados.")

    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores válidos en las casillas de X e Y.")

import time

def iniciar_barrido():
    try:
        delta_x = float(Delta_x.get()) * 0.0805  # Convertir Delta X a pasos
        delta_y = float(Delta_y.get()) * 0.4     # Convertir Delta Y a pasos

        x_positivo = int(X_positivo.get())  # Cuántas veces moverse en X+
        x_negativo = int(X_negativo.get())  # Cuántas veces moverse en X-
        y_positivo = int(Y_positivo.get())  # Cuántas veces moverse en Y+
        y_negativo = int(Y_negativo.get())  # Cuántas veces moverse en Y-

        # Pausa para permitir la visualización del movimiento
        tiempo_pausa = 5  # Pausar 1.5 segundos entre cada movimiento

        # Movimiento en X+ (usando motor Y)
        if x_positivo > 0:
            for _ in range(x_positivo):
                nueva_x = x_pos + delta_x
                if verificar_limites(nueva_x, y_pos):
                    enviar_comando(f'G91\nG0 Y{delta_x}\nG90', delta_x, 0)
                    time.sleep(tiempo_pausa)  # Pausa entre movimientos
                else:
                    mostrar_advertencia("X", nueva_x)
                    break  # Si se exceden los límites, salimos del bucle

            # Regresar a la posición inicial después de moverse en X+
            enviar_comando(f'G91\nG0 Y{-delta_x * x_positivo}\nG90', -delta_x * x_positivo, 0)
            time.sleep(tiempo_pausa)  # Pausa para regresar

        # Movimiento en X- (usando motor Y)
        if x_negativo > 0:
            for _ in range(x_negativo):
                nueva_x = x_pos - delta_x
                if verificar_limites(nueva_x, y_pos):
                    enviar_comando(f'G91\nG0 Y{-delta_x}\nG90', -delta_x, 0)
                    time.sleep(tiempo_pausa)  # Pausa entre movimientos
                else:
                    mostrar_advertencia("X", nueva_x)
                    break  # Si se exceden los límites, salimos del bucle

            # Regresar a la posición inicial después de moverse en X-
            enviar_comando(f'G91\nG0 Y{delta_x * x_negativo}\nG90', delta_x * x_negativo, 0)
            time.sleep(tiempo_pausa)  # Pausa para regresar

        # Movimiento en Y+ (usando motores X y Z)
        if y_positivo > 0:
            for _ in range(y_positivo):
                nueva_y = y_pos + delta_y
                if verificar_limites(x_pos, nueva_y):
                    enviar_comando(f'G91\nG0 X{delta_y} Z{delta_y}\nG90', 0, delta_y)
                    time.sleep(tiempo_pausa)  # Pausa entre movimientos
                else:
                    mostrar_advertencia("Y", nueva_y)
                    break  # Si se exceden los límites, salimos del bucle

            # Regresar a la posición inicial después de moverse en Y+
            enviar_comando(f'G91\nG0 X{-delta_y * y_positivo} Z{-delta_y * y_positivo}\nG90', 0, -delta_y * y_positivo)
            time.sleep(tiempo_pausa)  # Pausa para regresar

        # Movimiento en Y- (usando motores X y Z)
        if y_negativo > 0:
            for _ in range(y_negativo):
                nueva_y = y_pos - delta_y
                if verificar_limites(x_pos, nueva_y):
                    enviar_comando(f'G91\nG0 X{-delta_y} Z{-delta_y}\nG90', 0, -delta_y)
                    time.sleep(tiempo_pausa)  # Pausa entre movimientos
                else:
                    mostrar_advertencia("Y", nueva_y)
                    break  # Si se exceden los límites, salimos del bucle

            # Regresar a la posición inicial después de moverse en Y-
            enviar_comando(f'G91\nG0 X{delta_y * y_negativo} Z{delta_y * y_negativo}\nG90', 0, delta_y * y_negativo)
            time.sleep(tiempo_pausa)  # Pausa para regresar

        messagebox.showinfo("Barrido completo", "El barrido automático ha finalizado correctamente.")

    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese valores válidos en las casillas de X e Y.")

label_x.update_idletasks()  # Forzar actualización de la interfaz
label_y.update_idletasks()  # Forzar actualización de la interfaz

#se intervino 23/10
def actualizar_x(nueva_x):
    global x_pos
    x_pos = nueva_x
    x_pos_mm = round(x_pos / 0.0805)
    label_x.config(text=f"Posición X: {x_pos_mm:} mm")

def actualizar_y(nueva_y):
    global y_pos
    y_pos = nueva_y
    y_pos_mm = round(y_pos / 0.4)
    label_y.config(text=f"Posición Y: {y_pos_mm:} mm")

def mostrar_advertencia(eje, nueva_pos):
    messagebox.showwarning("Límite excedido", f"No se puede mover el eje {eje} a {nueva_pos} mm, excede los límites.")

# Etiquetas y cuadros de texto para el eje X
ttk.Label(root, text="(ΔX):").grid(row=0, column=2, padx=10, pady=5)
Delta_x = tk.Entry(root)
Delta_x.grid(row=0, column=3, padx=10, pady=5)

ttk.Label(root, text="X+:").grid(row=1, column=2, padx=10, pady=5)
X_positivo = tk.Entry(root)
X_positivo.grid(row=1, column=3, padx=10, pady=5)

# Etiqueta y cuadro de texto para las repeticiones
tk.Label(root, text="X-:").grid(row=2, column=2, padx=10, pady=5)
X_negativo = tk.Entry(root)
X_negativo.grid(row=2, column=3, padx=10, pady=5)

ttk.Label(root, text="(ΔY):").grid(row=0, column=4, padx=10, pady=5)
Delta_y = tk.Entry(root)
Delta_y.grid(row=0, column=5, padx=10, pady=5)

ttk.Label(root, text="Y+:").grid(row=1, column=4, padx=10, pady=5)
Y_positivo = tk.Entry(root)
Y_positivo.grid(row=1, column=5, padx=10, pady=5)

# Etiqueta y cuadro de texto para las repeticiones
tk.Label(root, text="Y-:").grid(row=2, column=4, padx=10, pady=5)
Y_negativo = tk.Entry(root)
Y_negativo.grid(row=2, column=5, padx=10, pady=5)

# Código para agregar el botón en tu interfaz (Tkinter/ttkbootstrap)
btn_abrir_archivo = ttk.Button(root,bootstyle="secondary_outline", text=" Abrir Coordenadas ", command=abrir_archivo)
btn_abrir_archivo.grid(row=4, column=0, padx=10, pady=10)

# Botón para iniciar el barrido
btn_barrido = ttk.Button(root, bootstyle="primary_outline", text="Iniciar Barrido", command=iniciar_barrido)
btn_barrido.grid(row=3, column=3, padx=10, pady=10)

btn_barrido = ttk.Button(root, bootstyle="primary_outline", text="Mover manual", command=mover_manual)
btn_barrido.grid(row=3, column=5, padx=10, pady=10)

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

#12.py pero trabajando con los limites
#Final del dia 18 de octubre se limitaron los movimientos en los intervalos y los manuales
#Movimientos manuales dando problemas, se suman juntos a la vez y a veces no hace la suma ni resta correctamente
#Falta rehacer por completo el barrido
"""Prompt para barrido, quiero que el delta X y delta Y definan de cuantos serán los movimientos, este será un valor numerico 
que ira en mm y quiero que el valor que se ponga en X se multiplique por 0.0805 ya que ese paso debe dar en X para que se mueva 1 mm y para Y que se multiplique
por 0.4, luego quiero que se den movimientos para X+ X- Y+ Y- y que el programa mueva los motores Delta X y/0 Delta Y x+, x- y/o y+ y- veces., es decir
si x+ = 3 entonces se moverá delta X 3 veces hacia el positivo en X que es en como yo tengo los motores Y0.0805 para que se mueva 1 mm, pero acomodalo
y en Y seria X0.4 Z0.4.
Que termine el movimiento de X+ y luego regrese los pasos que avanzo y continue con X-, avance con X- y luego regrese
para luego subir Y+ y baje Y+ para que luego haga Y- y vuelva Y-, esto considerando la verificacion de valores para
que no se salga de los limites los cuales son X_MIN, X_MAX = 0, 170
Y_MIN, Y_MAX = 0, 120.
Adicionalmente te pedire dos cosas más, una que haya un boton el cual ya tengo creado que se llamará mover yo creo, hazle una función que cuando se aprete
se vaya moviendo la secuencia que te di de X+ x- y+y-, es decir que el movimiento sea completamente manual, botón por botón y que haya otro botón que se
llame iniciar barrido que haga el movimento automatico.
y por ultimo pero no menos importante que actualice los label de posición X e Y con los mm que ha avanzado o retrocedido y siempre dentro de los parametros
de seguridad.
    
"""