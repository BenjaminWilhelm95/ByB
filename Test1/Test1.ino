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

  stepper1.setMaxSpeed(1000);
  stepper1.setAcceleration(500);
  stepper2.setMaxSpeed(1000);
  stepper2.setAcceleration(500);
  stepper3.setMaxSpeed(1000);
  stepper3.setAcceleration(500);

  Serial.println("Listo para recibir comandos.");
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');

    if (input.startsWith("S:")) {
      // Parsear el comando recibido
      input.remove(0, 2);
      float area_x = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float area_y = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float intervalo_cm = input.substring(0, input.indexOf(':')).toFloat();
      float intervalo_tiempo = input.substring(input.indexOf(':') + 1).toFloat();

      // Calcular los pasos necesarios
      long steps_x = area_x / intervalo_cm;
      long steps_y = area_y / intervalo_cm;

      // Configurar la velocidad máxima de los motores de acuerdo con el intervalo de tiempo
      float speed = intervalo_cm * 1000 / intervalo_tiempo;
      stepper1.setMaxSpeed(speed);
      stepper2.setMaxSpeed(speed);
      stepper3.setMaxSpeed(speed);

      for (long i = 0; i < steps_x; i++) {
        // Mover los motores de X en sincronia
        stepper1.moveTo((i + 1) * intervalo_cm);
        stepper2.moveTo((i + 1) * intervalo_cm);

        while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0) {
          stepper1.runToPosition();
          stepper2.runToPosition();
        }

        // Mover el motor de Y
        stepper3.moveTo((i + 1) * intervalo_cm);
        stepper3.runToPosition();
      }

      Serial.println("Movimiento completado.");
    }
  }
}
