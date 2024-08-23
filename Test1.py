import tkinter as tk
from tkinter import messagebox
import serial
import serial.tools.list_ports

ser = None
pos_x = 0
pos_y = 0

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

# Función de calibración
def calibrar():
    global ser, pos_x, pos_y
    if ser:
        ser.write(b'G28')  # Enviar comando de homing al Arduino
        pos_x = 0
        pos_y = 0
        actualizar_posicion()
        messagebox.showinfo("Calibración", "Calibración en proceso. Los ejes se están moviendo al punto (0,0)...")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Funciones para los botones de movimiento
def mover_eje(eje, direccion):
    global ser, pos_x, pos_y
    if ser:
        comando = f'{eje}{direccion}\n'
        ser.write(comando.encode())
        if eje == 'X':
            pos_x += 1 if direccion == '+' else -1
        elif eje == 'Y':
            pos_y += 1 if direccion == '+' else -1
        actualizar_posicion()
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

def actualizar_posicion():
    label_pos_x.config(text=f"Posición X: {pos_x}")
    label_pos_y.config(text=f"Posición Y: {pos_y}")

# Funciones para los botones de control de escaneo
def resetear():
    if ser:
        ser.write(b'R')  # Enviar comando de reseteo al Arduino
        messagebox.showinfo("Reseteo", "Reseteo en proceso...")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

def iniciar_escaneo():
    area_x = entry_area_x.get()
    area_y = entry_area_y.get()
    intervalo_cm = entry_intervalo_cm.get()
    intervalo_tiempo = entry_intervalo_tiempo.get()

    try:
        area_x = float(area_x)
        area_y = float(area_y)
        intervalo_cm = float(intervalo_cm)
        intervalo_tiempo = float(intervalo_tiempo)

        if area_x <= 0 or area_y <= 0 or intervalo_cm <= 0 or intervalo_tiempo <= 0:
            messagebox.showwarning("Advertencia", "Por favor, ingresa valores positivos.")
            return

        if ser:
            # Enviar los valores al Arduino
            command = f'S:{area_x}:{area_y}:{intervalo_cm}:{intervalo_tiempo}\n'
            ser.write(command.encode())
            messagebox.showinfo("Escaneo", f"Escaneo iniciado con área X: {area_x} cm², área Y: {area_y} cm², intervalo de {intervalo_cm} cm y tiempo de {intervalo_tiempo} ms.")
            preguntar_siguiente_barrido()
        else:
            messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")
    except ValueError:
        messagebox.showwarning("Advertencia", "Por favor, ingresa valores numéricos válidos.")

def preguntar_siguiente_barrido():
    continuar = messagebox.askyesno("Escaneo", "¿Deseas continuar con el siguiente barrido?")
    if continuar:
        ser.write(b'C')  # Enviar comando para continuar al Arduino
        preguntar_siguiente_barrido()
    else:
        guardar_resultados()

def guardar_resultados():
    if ser:
        ser.write(b'G')  # Enviar comando para obtener resultados al Arduino
        resultado = ser.readline().decode().strip()
        with open("resultados.txt", "w") as file:
            file.write(resultado)
        messagebox.showinfo("Resultados", "Los resultados se han guardado en resultados.txt")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Crear la ventana principal
root = tk.Tk()
root.title("Control de Dosímetro")

# Etiquetas y cuadros de texto
tk.Label(root, text="Área X a escanear (cm²):").grid(row=0, column=0, padx=10, pady=5)
entry_area_x = tk.Entry(root)
entry_area_x.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Área Y a escanear (cm²):").grid(row=1, column=0, padx=10, pady=5)
entry_area_y = tk.Entry(root)
entry_area_y.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Intervalo de movimiento (cm):").grid(row=2, column=0, padx=10, pady=5)
entry_intervalo_cm = tk.Entry(root)
entry_intervalo_cm.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Tiempo entre movimientos (ms):").grid(row=3, column=0, padx=10, pady=5)
entry_intervalo_tiempo = tk.Entry(root)
entry_intervalo_tiempo.grid(row=3, column=1, padx=10, pady=5)

# Etiquetas para mostrar la posición actual
label_pos_x = tk.Label(root, text="Posición X: 0")
label_pos_x.grid(row=4, column=0, padx=10, pady=5, sticky='w')
label_pos_y = tk.Label(root, text="Posición Y: 0")
label_pos_y.grid(row=5, column=0, padx=10, pady=5, sticky='w')

# Botones de movimiento organizados en un plano cartesiano en el lado derecho
frame_movimiento = tk.Frame(root)
frame_movimiento.grid(row=4, column=2, rowspan=2, padx=10, pady=5)

tk.Button(frame_movimiento, text="Y+", command=lambda: mover_eje('Y', '+')).grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_movimiento, text="X-", command=lambda: mover_eje('X', '-')).grid(row=1, column=0, padx=5, pady=5)
tk.Button(frame_movimiento, text="X+", command=lambda: mover_eje('X', '+')).grid(row=1, column=2, padx=5, pady=5)
tk.Button(frame_movimiento, text="Y-", command=lambda: mover_eje('Y', '-')).grid(row=2, column=1, padx=5, pady=5)

# Botones de control
btn_calibrar = tk.Button(root, text="Calibrar (Homing)", command=calibrar)
btn_calibrar.grid(row=6, column=0, padx=10, pady=5)

btn_resetear = tk.Button(root, text="Resetear", command=resetear)
btn_resetear.grid(row=6, column=1, padx=10, pady=5)

btn_iniciar = tk.Button(root, text="Iniciar Escaneo", command=iniciar_escaneo)
btn_iniciar.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

# Ejecutar la interfaz
root.mainloop()
