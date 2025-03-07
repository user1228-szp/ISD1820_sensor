#define REC_PIN 22  // Pin de grabación
#define PLAY_PIN 23 // Pin de reproducción

void setup() {
  Serial.begin(115200);  // Configura la velocidad del puerto serial

  pinMode(REC_PIN, OUTPUT);
  pinMode(PLAY_PIN, OUTPUT);

  // Comienza la grabación
  digitalWrite(REC_PIN, HIGH);  // Inicia la grabación
  delay(10000);  // Graba durante 10 segundos

  // Detiene la grabación
  digitalWrite(REC_PIN, LOW);
  Serial.println("Grabación detenida.");
  
  // Enviar los datos grabados al puerto serial
  Serial.println("Enviando datos de grabación...");
  // Aquí deberías agregar el código para enviar los datos del ISD1820 (ver más abajo)

  // Reproduce el audio
  digitalWrite(PLAY_PIN, HIGH); // Comienza la reproducción
  delay(10000);  // Reproduce durante 10 segundos
  digitalWrite(PLAY_PIN, LOW);  // Detiene la reproducción
}

void loop() {
  // El bucle principal está vacío porque solo grabamos una vez
}
