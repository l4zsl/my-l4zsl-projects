#include <Servo.h>

#define buzzer_pin 8
#define TRIGGER_PIN  9
#define ECHO_PIN     10
#define SERVO_PIN    11
#define MAX_DISTANCE 20

Servo servo;

bool isOpen = false;

void setup() {
  Serial.begin(9600);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(buzzer_pin, OUTPUT);
  servo.attach(SERVO_PIN);
}

void soundOpen() {
  tone(buzzer_pin, 1000, 200);
  delay(250);
  tone(buzzer_pin, 1500, 200);
}

void soundClose() {
  tone(buzzer_pin, 800, 200);
  delay(250);
  tone(buzzer_pin, 600, 200);
}

void loop() {
  long duration, distance, noise;
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = (duration / 2) / 29.1;
  noise = (distance * 30);
  
  if (distance <= MAX_DISTANCE) {
    if(!isOpen){
      servo.write(90);
      soundOpen();
      isOpen = true;
    }
    tone(buzzer_pin, noise);
  } 
  else {
    if(isOpen){
      servo.write(0);
      soundClose();
      isOpen = false;
    }
   
  }
 
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  delay(100);
}
