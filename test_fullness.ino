// --- Sensor 2: Bin Fullness Test ---
#define FULLNESS_TRIG_PIN 6
#define FULLNESS_ECHO_PIN 5

// Adjust this to the actual distance from the sensor to the bottom of the empty bin in cm
const float BIN_HEIGHT_CM = 16.0; 

void setup() {
  Serial.begin(9600);
  pinMode(FULLNESS_TRIG_PIN, OUTPUT);
  pinMode(FULLNESS_ECHO_PIN, INPUT);
  
  Serial.println("--- Fullness Sensor Test Started! ---");
  Serial.println("Ensure TRIG is on Pin 7, ECHO is on Pin 8.");
}

long getDistance(int trigPin, int echoPin) {
  // Send 10us HIGH pulse to trigger
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Read echo duration (timeout after 30ms)
  long duration = pulseIn(echoPin, HIGH, 30000); 
  
  if (duration == 0) {
    return 999; // 999 indicates timeout / out of range
  }
  
  // Convert duration to cm
  return (duration / 2) / 29.1; 
}

void loop() {
  long fullnessDistance = getDistance(FULLNESS_TRIG_PIN, FULLNESS_ECHO_PIN);
  
  // Calculate percentage (0% if empty, 100% if full)
  float fullnessPct = 0.0;
  if (fullnessDistance >= 0 && fullnessDistance < 999) {
    fullnessPct = ((BIN_HEIGHT_CM - (float)fullnessDistance) / BIN_HEIGHT_CM) * 100.0;
    
    // Clamp values between 0% and 100%
    if (fullnessPct < 0.0) fullnessPct = 0.0;
    if (fullnessPct > 100.0) fullnessPct = 100.0;
  }
  
  Serial.print("Raw Distance: ");
  if (fullnessDistance == 999) {
    Serial.print("OUT OF RANGE");
  } else {
    Serial.print(fullnessDistance);
    Serial.print(" cm");
  }
  Serial.print("   |   ");
  
  if (fullnessDistance == 999) {
    Serial.println("Error: No reading (check wiring!)");
  } else {
    Serial.print("Bin Fullness: ");
    Serial.print(fullnessPct, 1);
    Serial.println("%");
  }

  delay(1000); // Wait 1 second before the next reading
}
