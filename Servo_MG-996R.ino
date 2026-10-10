#include <Servo.h>

#define TRIGGER_PIN    9
#define ECHO_PIN       10
#define SERVO_PIN      11
#define POT_PIN        A0
#define MAX_DISTANCE   25

#define STOP_US        1500   // calibrate until the servo is still
#define SPEED_US       200    // how far from stop to drive (lower = slower)
#define DEADBAND       15     // tolerance in pot units

#define CLOSED_POS     200    // pot reading when lid is closed (measure this)
#define OPEN_POS       400    // pot reading when lid is open (measure this)
#define HOLD_TIME      3000

Servo servo;
bool objectPresent = false;

void setup() {
  Serial.begin(9600);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  servo.attach(SERVO_PIN);
  servo.writeMicroseconds(STOP_US);
}

long getDistance() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return 999;
  return (duration / 2) / 29.1;
}

void moveTo(int target) {
  unsigned long start = millis();
  while (millis() - start < 3000) {
    int pos = analogRead(POT_PIN);
    int error = target - pos;
    Serial.print("target: "); Serial.print(target);
    Serial.print("  pos: "); Serial.println(pos);
    if (abs(error) <= DEADBAND) {
      Serial.println("reached target");
      break;
    }
    servo.writeMicroseconds(error > 0 ? STOP_US + SPEED_US : STOP_US - SPEED_US);
    delay(10);
  }
  servo.writeMicroseconds(STOP_US);
  Serial.println("stopped");
}

void loop() {
  long distance = getDistance();

  if (distance > 0 && distance <= MAX_DISTANCE) {
    if (!objectPresent) {
      objectPresent = true;
      moveTo(OPEN_POS);
      delay(HOLD_TIME);
      moveTo(CLOSED_POS);                                                                                                                                                
    }
  } else {
    objectPresent = false;
  }
  delay(50);
}