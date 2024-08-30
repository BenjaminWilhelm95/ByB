import tkinter as tk
from tkinter import messagebox
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

# Función de calibración
def calibrar():
    global ser  # Asegúrate de declarar 'ser' como global aquí también
    if ser:
        ser.write(b'H')  # Enviar comando de homing al Arduino
        messagebox.showinfo("Calibración", "Calibración en proceso. Los ejes se están moviendo al punto (0,0)...")
    else:
        messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")

# Funciones para los botones
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
        else:
            messagebox.showwarning("Advertencia", "No hay conexión con el puerto serial.")
    except ValueError:
        messagebox.showwarning("Advertencia", "Por favor, ingresa valores numéricos válidos.")

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

# Botones
btn_calibrar = tk.Button(root, text="Calibrar (Homing)", command=calibrar)
btn_calibrar.grid(row=4, column=0, padx=10, pady=5)

btn_resetear = tk.Button(root, text="Resetear", command=resetear)
btn_resetear.grid(row=4, column=1, padx=10, pady=5)

btn_iniciar = tk.Button(root, text="Iniciar Escaneo", command=iniciar_escaneo)
btn_iniciar.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Ejecutar la interfaz
root.mainloop()
