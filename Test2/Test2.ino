#include <Module_GRBL_13.2.h>
#include <AccelStepper.h>

// Definir pines para el primer motor (Motor 1) - Eje X
#define DIR_PIN1 5
#define STEP_PIN1 2

// Definir pines para el segundo motor (Motor 2) - Eje X
#define DIR_PIN2 6
#define STEP_PIN2 3

// Definir pines para el tercer motor (Motor 3) - Eje Y
#define DIR_PIN3 7
#define STEP_PIN3 4

#define ENABLE_PIN 8  // Compartido por todos los motores
#define LIMIT_SWITCH_PIN1 9  // Para motores 1 y 2 (Eje X)
#define LIMIT_SWITCH_PIN2 10 // Para motor 3 (Eje Y)

// Crear instancias de AccelStepper para los tres motores
AccelStepper stepper1(AccelStepper::DRIVER, STEP_PIN1, DIR_PIN1);
AccelStepper stepper2(AccelStepper::DRIVER, STEP_PIN2, DIR_PIN2);
AccelStepper stepper3(AccelStepper::DRIVER, STEP_PIN3, DIR_PIN3);

void setup() {
  Serial.begin(9600);

  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(LIMIT_SWITCH_PIN1, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_PIN2, INPUT_PULLUP);

  digitalWrite(ENABLE_PIN, LOW);  // Habilitar los motores

  stepper1.setMaxSpeed(500);
  stepper1.setAcceleration(1000);
  stepper2.setMaxSpeed(500);
  stepper2.setAcceleration(1000);
  stepper3.setMaxSpeed(500);
  stepper3.setAcceleration(1000);

  Serial.println("Listo para recibir comandos.");
  // Variables para almacenar los datos
float currentX = 0;
float currentY = 0;
bool isMoving = false;
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');

    if (input.startsWith("S:")) {
      input.remove(0, 2);
      float area_x = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float area_y = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float intervalo_cm = input.substring(0, input.indexOf(':')).toFloat();
      float intervalo_tiempo = input.substring(input.indexOf(':') + 1).toFloat();

      long steps_x = area_x / intervalo_cm;
      long steps_y = area_y / intervalo_cm;

      stepper1.moveTo(steps_x);
      stepper2.moveTo(steps_x);
      stepper3.moveTo(steps_y);

      while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0 || stepper3.distanceToGo() != 0) {
        if (stepper1.distanceToGo() != 0) stepper1.run();
        if (stepper2.distanceToGo() != 0) stepper2.run();
        if (stepper3.distanceToGo() != 0) stepper3.run();
      }
      Serial.println("Movimiento completado.");
    } else if (input == "GET_DATA") { // Comando para obtener datos
      enviarDatos();
    }
  }
}
void enviarDatos() {
  // Obtener las posiciones actuales de los motores
  long posicion_x1 = stepper1.currentPosition();
  long posicion_x2 = stepper2.currentPosition();
  long posicion_y = stepper3.currentPosition();

  // Obtener el estado de los switches de límite
  bool estado_limit_x = digitalRead(LIMIT_SWITCH_PIN1) == LOW;
  bool estado_limit_y = digitalRead(LIMIT_SWITCH_PIN2) == LOW;

  // Enviar los datos por el puerto serial
  Serial.print("PX1:"); Serial.print(posicion_x1);
  Serial.print(",PX2:"); Serial.print(posicion_x2);
  Serial.print(",PY:"); Serial.print(posicion_y);
  Serial.print(",LX:"); Serial.print(estado_limit_x);
  Serial.print(",LY:"); Serial.println(estado_limit_y);
}
//