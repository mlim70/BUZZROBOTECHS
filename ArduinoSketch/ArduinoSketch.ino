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
    int comma3 = data.indexOf(',', comma2 + 1);
    int comma4 = data.indexOf(',', comma3 + 1);
    int comma5 = data.indexOf(',', comma4 + 1);
    
    if (comma1 > 0 && comma2 > comma1 && comma3 > comma2 && 
        comma4 > comma3 && comma5 > comma4) {
      // Parse position data (x, y, z)
      float x = data.substring(0, comma1).toFloat();
      float y = data.substring(comma1 + 1, comma2).toFloat();
      float z = data.substring(comma2 + 1, comma3).toFloat();
      
      // Parse orientation data (rx, ry, rz)
      float rx = data.substring(comma3 + 1, comma4).toFloat();
      float ry = data.substring(comma4 + 1, comma5).toFloat();
      float rz = data.substring(comma5 + 1).toFloat();
      
      // Now you have:
      // x, y, z: Position in meters
      // rx, ry, rz: Rotation vector components (in radians)
      
      // You can use these values to:
      // 1. Control servos based on position
      // 2. Calculate angles for arm movement
      // 3. Log the data for debugging
      
      // Example: Print the received data
      Serial.print("Position (m): ");
      Serial.print(x); Serial.print(", ");
      Serial.print(y); Serial.print(", ");
      Serial.println(z);
      
      Serial.print("Rotation (rad): ");
      Serial.print(rx); Serial.print(", ");
      Serial.print(ry); Serial.print(", ");
      Serial.println(rz);
    }
  }
}

