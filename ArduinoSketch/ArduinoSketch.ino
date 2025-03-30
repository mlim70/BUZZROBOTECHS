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
// PID Control Variables
// -----------------------------
float Kp = 100.0;
float Ki = 0.0;
float Kd = 20.0;
float prevError = 0.0;
float integral = 0.0;
unsigned long lastTime = 0;

// -----------------------------
// Navigation thresholds (in meters)
// -----------------------------
float approachThreshold = 0.3; // Stop if tag is closer than 30cm

// -----------------------------
// Function Prototypes
// -----------------------------
void driveForwardPID(int leftSpeed, int rightSpeed);
void haltMotors();
float computePID(float error);

void setup() {
  Serial.begin(115200);
  
  // Initialize all motor control pins as OUTPUT
  int motorPins[] = {IN1, IN2, IN3, IN4, ENA, ENB, IN5, IN6, IN7, IN8, ENA2, ENB2};
  for (int i = 0; i < 12; i++) {
    pinMode(motorPins[i], OUTPUT);
  }
  
  lastTime = millis();
}

// -----------------------------
// Motor Control Functions
// -----------------------------
// driveForwardPID: drives forward with separate left/right speeds
void driveForwardPID(int leftSpeed, int rightSpeed) {
  // Front Wheels
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  analogWrite(ENA, leftSpeed);
  analogWrite(ENB, rightSpeed);
  
  // Back Wheels
  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
  analogWrite(ENA2, leftSpeed);
  analogWrite(ENB2, rightSpeed);
}

// haltMotors: stops all motors
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

// computePID: calculates the PID output for the given error
float computePID(float error) {
  unsigned long now = millis();
  float dt = (now - lastTime) / 1000.0; // convert to seconds
  if (dt <= 0.0) dt = 0.001; // prevent division by zero
  
  integral += error * dt;
  float derivative = (error - prevError) / dt;
  float output = Kp * error + Ki * integral + Kd * derivative;
  prevError = error;
  lastTime = now;
  
  return output;
}

// -----------------------------
// Main Loop: Read Serial Data & Navigate
// -----------------------------
void loop() {
  if (Serial.available()) {
    // Read incoming data until newline character
    String data = Serial.readStringUntil('\n');
    
    // Parse the comma-separated values
    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);
    int comma3 = data.indexOf(',', comma2 + 1);
    int comma4 = data.indexOf(',', comma3 + 1);
    int comma5 = data.indexOf(',', comma4 + 1);
    
    // Check if commas are in correct order
    if (comma1 > 0 && comma2 > comma1 && comma3 > comma2 && 
        comma4 > comma3 && comma5 > comma4) {
        
        // Convert directly to floats (will be 0.0 if conversion fails)
        float x = data.substring(0, comma1).toFloat();
        float y = data.substring(comma1 + 1, comma2).toFloat();
        float z = data.substring(comma2 + 1, comma3).toFloat();
        float rx = data.substring(comma3 + 1, comma4).toFloat();
        float ry = data.substring(comma4 + 1, comma5).toFloat();
        float rz = data.substring(comma5 + 1).toFloat();
        
        // Check if any value is 0 (indicating conversion failure)
        if (x != 0.0 || y != 0.0 || z != 0.0 || 
            rx != 0.0 || ry != 0.0 || rz != 0.0) {
            
            // Print received data for debugging
            Serial.print("DEBUG: Position (m): ");
            Serial.print(x); Serial.print(", ");
            Serial.print(y); Serial.print(", ");
            Serial.println(z);
            
            // Use PID control for smooth movement
            float error = x;  // Use x position as error
            float pidOutput = computePID(error);
            
            // Base speed for forward motion
            int baseSpeed = 150;
            
            // Calculate motor speeds using PID output
            int leftSpeed = baseSpeed + pidOutput;
            int rightSpeed = baseSpeed - pidOutput;
            
            // Ensure speeds are within valid PWM range
            leftSpeed = constrain(leftSpeed, 0, 255);
            rightSpeed = constrain(rightSpeed, 0, 255);
            
            // Drive the motors using the PID-calculated speeds
            driveForwardPID(leftSpeed, rightSpeed);
            
            // Print debug information
            Serial.print("DEBUG: PID output: ");
            Serial.println(pidOutput);
            Serial.print("DEBUG: Left speed: ");
            Serial.print(leftSpeed);
            Serial.print(" | Right speed: ");
            Serial.println(rightSpeed);
            
        } else {
            Serial.println("DEBUG: Error: Invalid number format");
            haltMotors();
        }
    } else {
        Serial.println("DEBUG: Error: Invalid comma positions");
        haltMotors();
    }
  }
}