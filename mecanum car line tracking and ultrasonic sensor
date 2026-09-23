#include "MecanumCar_v2.h"
#include "Servo.h"

mecanumCar mecanumCar(3, 2);
Servo myservo;

// line sensors
#define SensorLeft    A0
#define SensorMiddle  A1
#define SensorRight   A2

// ultrasonics
#define EchoPin 13
#define TrigPin 12

int distance_M, distance_L, distance_R;

void setup() {

  pinMode(SensorLeft, INPUT);
  pinMode(SensorMiddle, INPUT);
  pinMode(SensorRight, INPUT);

  pinMode(EchoPin, INPUT);
  pinMode(TrigPin, OUTPUT);

  myservo.attach(9);
  myservo.write(90);
  delay(500);

  mecanumCar.Init();
}

void loop() {

  // ultrasonic movements (the servo write angle is made for that one specific robot i used, change if you need to)
  distance_M = get_distance();

  if (distance_M > 0 && distance_M < 20) {

    mecanumCar.Stop();
    delay(200);

    // scan left
    myservo.write(160);
    delay(300);
    distance_L = get_distance();

    // scan right
    myservo.write(20);
    delay(300);
    distance_R = get_distance();

    // center
    myservo.write(90);
    delay(150);

    // decide direction
    if (distance_L > distance_R) {
      mecanumCar.Turn_Left();
      delay(200);
    } else {
      mecanumCar.Turn_Right();
      delay(200);
    }

    return;
  }

  // line tracking
  int SL = digitalRead(SensorLeft);
  int SM = digitalRead(SensorMiddle);
  int SR = digitalRead(SensorRight);

  if (SM == HIGH) {
    mecanumCar.Advance();
  }

  else if (SL == HIGH && SR == LOW) {
    mecanumCar.Turn_Left();
  }

  else if (SR == HIGH && SL == LOW) {
    mecanumCar.Turn_Right();
  }

  else {
    mecanumCar.Stop();
  }
}


// ultrasonic distance calculating
int get_distance() {
  long duration;

  digitalWrite(TrigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);

  duration = pulseIn(EchoPin, HIGH, 30000);

  if (duration == 0) return 0;

  return duration * 0.034 / 2;
}
