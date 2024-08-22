#include <AccelStepper.h>

// Definir pines para el primer motor (Motor 1)
#define DIR_PIN1 5
#define STEP_PIN1 2

// Definir pines para el segundo motor (Motor 2)
#define DIR_PIN2 6
#define STEP_PIN2 3

// Definir pines para el tercer motor (Motor 3)
#define DIR_PIN3 7
#define STEP_PIN3 4

#define ENABLE_PIN 8  // Compartido por todos los motores
#define LIMIT_SWITCH_PIN1 9  // Para motores 1 y 2
#define LIMIT_SWITCH_PIN2 10 // Para motor 3

// Crear instancias de AccelStepper para los tres motores
AccelStepper stepper1(AccelStepper::DRIVER, STEP_PIN1, DIR_PIN1);
AccelStepper stepper2(AccelStepper::DRIVER, STEP_PIN2, DIR_PIN2);
AccelStepper stepper3(AccelStepper::DRIVER, STEP_PIN3, DIR_PIN3);

void setup() {
  // Iniciar comunicación serial
  Serial.begin(9600);
  
  // Configurar los pines
  pinMode(ENABLE_PIN, OUTPUT);
  pinMode(LIMIT_SWITCH_PIN1, INPUT_PULLUP);
  pinMode(LIMIT_SWITCH_PIN2, INPUT_PULLUP);

  // Habilitar el driver
  digitalWrite(ENABLE_PIN, LOW);  // LOW para habilitar, HIGH para deshabilitar

  // Configurar la velocidad y aceleración del motor 1
  stepper1.setMaxSpeed(500); // Máxima velocidad en pasos por segundo
  stepper1.setAcceleration(1000); // Aceleración en pasos por segundo al cuadrado

  // Configurar la velocidad y aceleración del motor 2
  stepper2.setMaxSpeed(500); // Máxima velocidad en pasos por segundo
  stepper2.setAcceleration(1000); // Aceleración en pasos por segundo al cuadrado

  // Configurar la velocidad y aceleración del motor 3
  stepper3.setMaxSpeed(500); // Máxima velocidad en pasos por segundo
  stepper3.setAcceleration(1000); // Aceleración en pasos por segundo al cuadrado

  // Mensaje de bienvenida
  Serial.println("Ingrese 'calibrar' para iniciar la calibración:");
}

void loop() {
  // Verificar si hay datos disponibles en el monitor serial
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n'); // Leer la entrada del usuario

    if (input.equalsIgnoreCase("calibrar")) {
      // Iniciar la calibración
      Serial.println("Iniciando calibración...");

      // Mover los motores 1 y 2 hacia el límite
      stepper1.setSpeed(350); // Velocidad de calibración
      stepper2.setSpeed(350); // Velocidad de calibración
      while (digitalRead(LIMIT_SWITCH_PIN1) == LOW) {
        stepper1.runSpeed();
        stepper2.runSpeed();
      }

      // Detener los motores 1 y 2 al alcanzar el límite
      stepper1.stop();
      stepper2.stop();
      stepper1.setCurrentPosition(0); // Establecer la posición actual como cero
      stepper2.setCurrentPosition(0); // Establecer la posición actual como cero

      // Mover el motor 3 hacia el límite
      stepper3.setSpeed(250); // Velocidad de calibración
      while (digitalRead(LIMIT_SWITCH_PIN2) == LOW) {
        stepper3.runSpeed();
      }

      // Detener el motor 3 al alcanzar el límite
      stepper3.stop();
      stepper3.setCurrentPosition(0); // Establecer la posición actual como cero
      Serial.println("Calibración completada.");
    }
  }
}