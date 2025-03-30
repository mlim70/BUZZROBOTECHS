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
float approachThreshold = 0.3;  // Stop if tag is closer than 30 cm

// -----------------------------
// Function Prototypes
// -----------------------------
void forward();
void turnLeft();
void turnRight();
void haltMotors();

// -----------------------------
// State tracking
// -----------------------------
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT = 1000; // 1 second timeout
bool lastCommandValid = false;

void setup() {
  Serial.begin(115200);
  
  // Initialize all motor control pins as OUTPUT
  int motorPins[] = {IN1, IN2, IN3, IN4, ENA, ENB, IN5, IN6, IN7, IN8, ENA2, ENB2};
  for (int i = 0; i < 12; i++) {
    pinMode(motorPins[i], OUTPUT);
  }
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
  
  lastCommandTime = millis();
  lastCommandValid = true;
}

void turnLeft() {
  // Left Wheels (backward)
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN5, LOW);
  digitalWrite(IN6, HIGH);
  
  // Right Wheels (forward)
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
  digitalWrite(IN7, HIGH);
  digitalWrite(IN8, LOW);
  
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  analogWrite(ENA2, 200);
  analogWrite(ENB2, 200);
  
  lastCommandTime = millis();
  lastCommandValid = true;
}

void turnRight() {
  // Left Wheels (forward)
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  
  // Right Wheels (backward)
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
  
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  analogWrite(ENA2, 200);
  analogWrite(ENB2, 200);
  
  lastCommandTime = millis();
  lastCommandValid = true;
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
  
  lastCommandValid = false;
}

// -----------------------------
// Main Loop: Read Serial Data & Navigate Without PID
// -----------------------------
void loop() {
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
      String rx_str = data.substring(comma3 + 1, comma4);
      String ry_str = data.substring(comma4 + 1, comma5);
      String rz_str = data.substring(comma5 + 1);
      
      if (x_str.length() > 0 && y_str.length() > 0 && z_str.length() > 0 &&
          rx_str.length() > 0 && ry_str.length() > 0 && rz_str.length() > 0) {
        
        // Convert strings to float values
        float x = x_str.toFloat();
        float y = y_str.toFloat();
        float z = z_str.toFloat();
        float rx = rx_str.toFloat();
        float ry = ry_str.toFloat();
        float rz = rz_str.toFloat();
        
        // Navigation Decision:
        // If the tag is far (z > approachThreshold), adjust motion based on x.
        if (z > approachThreshold) {
          if (x > centerThreshold) {
            Serial.println("RIGHT");
            turnRight();
          } else if (x < -centerThreshold) {
            Serial.println("LEFT");
            turnLeft();
          } else {
            Serial.println("FORWARD");
            forward();
          }
        } else {
          // Tag is close enough, so stop.
          Serial.println("STOP");
          haltMotors();
        }
      } else {
        Serial.println("ERR: Missing values");
      }
    } else {
      Serial.println("ERR: Invalid format");
    }
  }
  
  // Check if we've exceeded the command timeout
  if (lastCommandValid && (millis() - lastCommandTime > COMMAND_TIMEOUT)) {
    Serial.println("TIMEOUT");
    haltMotors();
  }
}