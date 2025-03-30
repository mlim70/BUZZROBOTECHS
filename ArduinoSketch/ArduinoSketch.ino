void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

void loop() {
  // print out a message every second:
  Serial.println("Hello, Arduino!");
  delay(1000);
}
