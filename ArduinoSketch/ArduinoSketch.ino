// -----------------------------
// Motor pin definitions
// -----------------------------
// Front Wheels
int IN1 = 2;   // Front-Left Motor IN1
int IN2 = 3;   // Front-Left Motor IN2
int IN3 = 4;   // Front-Right Motor IN1
int IN4 = 7;   // Front-Right Motor IN2
int ENA = 10;  // Front-Left PWM speed
int ENB = 5;   // Front-Right PWM speed

// Back Wheels
int IN5 = 8;   // Back-Left Motor IN1
int IN6 = 9;   // Back-Left Motor IN2
int IN7 = 12;  // Back-Right Motor IN1
int IN8 = 13;  // Back-Right Motor IN2
int ENA2 = 11; // Back-Left PWM speed
int ENB2 = 6;  // Back-Right PWM speed

// -----------------------------
// Navigation thresholds (in meters)
// -----------------------------
float centerThreshold = 0.05;   // ±5 cm off-center
float approachThreshold = 0.07;  // Stop if tag is closer than 30 cm
float maxSpeed = 150;           // Maximum PWM speed
float minSpeed = 50;            // Minimum PWM speed for movement

// -----------------------------
// Movement Control Variables
// -----------------------------
float lastX = 0;
float lastZ = 0;
unsigned long lastUpdateTime = 0;
const unsigned long MOVEMENT_TIMEOUT = 100; // 100ms timeout for movement updates

// -----------------------------
// Function Prototypes
// -----------------------------
void moveProportional(float x, float z);
void haltMotors();
void updateMotors(float leftSpeed, float rightSpeed);

void setup() {
  Serial.begin(115200);
  
  // Initialize all motor control pins as OUTPUT
  int motorPins[] = {IN1, IN2, IN3, IN4, ENA, ENB, IN5, IN6, IN7, IN8, ENA2, ENB2};
  for (int i = 0; i < 12; i++) {
    pinMode(motorPins[i], OUTPUT);
  }
  
  // Initialize motors to stopped state
  haltMotors();
}

// -----------------------------
// Motor Control Functions
// -----------------------------
void forward() {
  // Front Wheels
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, 150);
  analogWrite(ENB, 150);
  
  // Back Wheels
  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
  analogWrite(ENA2, 150);
  analogWrite(ENB2, 150);
}

void turnLeft() {
  // Left Wheels (backward)
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  
  // Right Wheels (forward)
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  digitalWrite(IN7, HIGH);
  digitalWrite(IN8, LOW);
  
  analogWrite(ENA, 150);
  analogWrite(ENB, 150);
  analogWrite(ENA2, 150);
  analogWrite(ENB2, 150);
}

void turnRight() {
  // Left Wheels (forward)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, HIGH);
  
  // Right Wheels (backward)
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
  
  analogWrite(ENA, 150);
  analogWrite(ENB, 150);
  analogWrite(ENA2, 150);
  analogWrite(ENB2, 150);
}

void haltMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
  
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, LOW);
  analogWrite(ENA2, 0);
  analogWrite(ENB2, 0);
}

// -----------------------------
// Main Loop: Read Serial Data & Navigate With Proportional Control
// -----------------------------
void loop() {
  unsigned long currentTime = millis();
  
  // Check if we need to maintain last movement command
  if (currentTime - lastUpdateTime > MOVEMENT_TIMEOUT) {
    // If no new data received, maintain last movement
    if (lastZ > approachThreshold) {
      moveProportional(lastX, lastZ);
    }
  }
  
  // Check if Serial data is available
  if (Serial.available()) {
    // Read the incoming data until newline character
    String data = Serial.readStringUntil('\n');
    
    // Parse the comma-separated values
    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);
    int comma3 = data.indexOf(',', comma2 + 1);
    int comma4 = data.indexOf(',', comma3 + 1);
    int comma5 = data.indexOf(',', comma4 + 1);
    
    if (comma1 > 0 && comma2 > comma1 && comma3 > comma2 &&
        comma4 > comma3 && comma5 > comma4) {
      
      String x_str  = data.substring(0, comma1);
      String y_str  = data.substring(comma1 + 1, comma2);
      String z_str  = data.substring(comma2 + 1, comma3);
      
      if (x_str.length() > 0 && y_str.length() > 0 && z_str.length() > 0) {
        // Convert strings to float values
        float x = x_str.toFloat();
        float y = y_str.toFloat();
        float z = z_str.toFloat();
        
        // Update last known position
        lastX = x;
        lastZ = z;
        lastUpdateTime = currentTime;
        
        // Navigation Decision:
        if (z > approachThreshold) {
          moveProportional(x, z);
        } else {
          // Tag is close enough, so stop.
          Serial.println("Tag reached. Halting...");
          haltMotors();
        }
      }
    }
  }
}

void moveProportional(float x, float z) {
  // Calculate base speed based on distance (closer = slower)
  float baseSpeed = map(z, approachThreshold, 1.0, minSpeed, maxSpeed);
  baseSpeed = constrain(baseSpeed, minSpeed, maxSpeed);
  
  // Calculate turn factor based on x offset
  float turnFactor = map(x, -centerThreshold, centerThreshold, -1.0, 1.0);
  turnFactor = constrain(turnFactor, -1.0, 1.0);
  
  // Calculate left and right speeds
  float leftSpeed = baseSpeed * (1.0 + turnFactor);
  float rightSpeed = baseSpeed * (1.0 - turnFactor);
  
  // Constrain speeds
  leftSpeed = constrain(leftSpeed, 0, maxSpeed);
  rightSpeed = constrain(rightSpeed, 0, maxSpeed);
  
  // Update motors with new speeds
  updateMotors(leftSpeed, rightSpeed);
  
  // Debug output
  Serial.print("Speeds - Left: ");
  Serial.print(leftSpeed);
  Serial.print(" Right: ");
  Serial.println(rightSpeed);
}

void updateMotors(float leftSpeed, float rightSpeed) {
  // Front Left
  digitalWrite(IN1, leftSpeed > 0 ? HIGH : LOW);
  digitalWrite(IN2, leftSpeed > 0 ? LOW : HIGH);
  analogWrite(ENA, abs(leftSpeed));
  
  // Front Right
  digitalWrite(IN3, rightSpeed > 0 ? HIGH : LOW);
  digitalWrite(IN4, rightSpeed > 0 ? LOW : HIGH);
  analogWrite(ENB, abs(rightSpeed));
  
  // Back Left
  digitalWrite(IN5, leftSpeed > 0 ? HIGH : LOW);
  digitalWrite(IN6, leftSpeed > 0 ? LOW : HIGH);
  analogWrite(ENA2, abs(leftSpeed));
  
  // Back Right
  digitalWrite(IN7, rightSpeed > 0 ? HIGH : LOW);
  digitalWrite(IN8, rightSpeed > 0 ? LOW : HIGH);
  analogWrite(ENB2, abs(rightSpeed));
}