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
}

void loop() {
  if (Serial.available() > 0) { //Verifica si hay datos disponibles en el puerto serial
    String input = Serial.readStringUntil('\n');//Lee la cadena de caracteres enviada, se almacena en input

    if (input.startsWith("S:")) {//Input empieza con S?
      // Parsear el comando recibido
      input.remove(0, 2);// Elimina los 2 primeros caracteres
      float area_x = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float area_y = input.substring(0, input.indexOf(':')).toFloat();
      input = input.substring(input.indexOf(':') + 1);
      float intervalo_cm = input.substring(0, input.indexOf(':')).toFloat(); //Distancia que se mueve el motor paso a paso
      float intervalo_tiempo = input.substring(input.indexOf(':') + 1).toFloat();  //Tiempo entre movimientos en milisegundos

      // Calcular los pasos necesarios
      long steps_x = area_x / intervalo_cm; //Si area X = 10cm e intervalo de mov = 1cm, entonces se requieren 10 pasos
      long steps_y = area_y / intervalo_cm;

           // Configurar los motores para moverse al mismo tiempo
      stepper1.moveTo(steps_x);
      stepper2.moveTo(steps_x);
      stepper3.moveTo(steps_y);

      // Mover los motores simultáneamente
      while (stepper1.distanceToGo() != 0 || stepper2.distanceToGo() != 0 || stepper3.distanceToGo() != 0) {
        // Ejecutar los motores de X juntos
        if (stepper1.distanceToGo() != 0) stepper1.run();
        if (stepper2.distanceToGo() != 0) stepper2.run();

        // Mover el motor de Y
        if (stepper3.distanceToGo() != 0) stepper3.run();
      }
      Serial.println("Movimiento completado.");
    }
  }
}
