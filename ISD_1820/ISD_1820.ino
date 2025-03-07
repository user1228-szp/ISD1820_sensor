#define REC_PIN 7
#define PLAYE_PIN 8
#define PLAYL_PIN 9

void setup() {
    pinMode(REC_PIN, OUTPUT);
    pinMode(PLAYE_PIN, OUTPUT);
    pinMode(PLAYL_PIN, OUTPUT);
}

void loop() {
    // Record for 5 seconds
    digitalWrite(REC_PIN, HIGH);
    delay(5000); // Recording duration
    digitalWrite(REC_PIN, LOW);

    delay(2000); // Wait before playback

    // Play the recorded message (edge-triggered)
    digitalWrite(PLAYE_PIN, HIGH);
    delay(500);
    digitalWrite(PLAYE_PIN, LOW);
    
    delay(3000); // Delay before the next loop
}
