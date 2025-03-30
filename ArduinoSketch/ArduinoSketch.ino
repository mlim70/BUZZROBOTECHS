void setup() {
  Serial.begin(115200); // Start serial communication at 115200 baud
}

void loop() {
  if (Serial.available()) {
    // Read incoming data until newline character
    String data = Serial.readStringUntil('\n');
    
    // Parse the comma-separated values
    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);
    
    if (comma1 > 0 && comma2 > comma1) {
      float x = data.substring(0, comma1).toFloat();
      float y = data.substring(comma1 + 1, comma2).toFloat();
      float z = data.substring(comma2 + 1).toFloat();
      
      // Now you have x, y, z in meters.
      // You can use them as needed (e.g., controlling servos, logging data, etc.)
    }
  }
}
