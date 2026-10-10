#include <Servo.h>

#define TRIGGER_PIN    9 
#define ECHO_PIN       10 
#define SERVO_PIN      11 
#define MAX_DISTANCE   25 

// Adjust this value to control how long it spins per detection
#define MOVE_TIME      400 

Servo servo;
bool objectPresent = false; // Tracks if your hand is currently over the sensor

void setup() {
  Serial.begin(9600);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  servo.attach(SERVO_PIN);
  servo.write(90); // 90 tells a 360-degree servo to STOP spinning
}

long getDistance() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000); 
  
  if (duration == 0) {
    return 999; 
  }
  
  return (duration / 2) / 29.1; 
}

void loop() {
  long distance = getDistance();

  // If a hand is detected in range
  if (distance > 0 && distance <= MAX_DISTANCE) {
    
    // Only spin if we haven't already reacted to this hand wave
    if (!objectPresent) {
      servo.write(180); // Spin forward
      delay(MOVE_TIME); // Wait while it travels
     
      servo.write(90);  // STOP spinning
      
      
      objectPresent = true; // Lock it so it doesn't keep spinning while your hand is there
    }
    
  } else {
    // If no hand is detected, unlock it for the next wave
    objectPresent = false;
  }

  delay(50); 
}