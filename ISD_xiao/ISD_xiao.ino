#include <WiFi.h>
#include <HTTPClient.h>
#include <SPIFFS.h>

const char* ssid = "tu_red_wifi";  // Este valor será sustituido por el SSID elegido
const char* password = "tu_contraseña_wifi";  // Este valor será introducido por el usuario

#define REC_PIN 22  // Pin de grabación
#define PLAY_PIN 23 // Pin de reproducción

unsigned long lastDebounceTime = 0;  // Última vez que se cambió el estado del botón
unsigned long debounceDelay = 50;     // Retardo de debounce en milisegundos

String serverUrl = "http://192.168.1.100:5000/subir_audio"; // URL del servidor para subir los datos grabados

void setup() {
  // Iniciar la comunicación serial
  Serial.begin(115200);
  delay(10);

  // Iniciar la conexión Wi-Fi
  initWiFi();

  // Iniciar SPIFFS para almacenar archivos temporales
  if (!SPIFFS.begin(true)) {
    Serial.println("Error al montar SPIFFS.");
    return;
  }
}

void loop() {
  // Verificar el estado del botón de grabación
  startRecording();
}

// Función para iniciar el escaneo y permitir la elección de la red Wi-Fi
void initWiFi() {
  Serial.println("Iniciando escaneo de redes Wi-Fi...");

  int n = WiFi.scanNetworks();  // Escanear redes Wi-Fi disponibles
  Serial.println("Escaneo completado");

  if (n == 0) {
    Serial.println("No se encontraron redes.");
  } else {
    Serial.print(n);
    Serial.println(" redes encontradas:");

    for (int i = 0; i < n; ++i) {
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(" dBm)");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN) ? " Abierta" : " Segura");
      delay(10);
    }

    // Solicitar al usuario seleccionar una red
    Serial.println("\nIngresa el número de la red a la que deseas conectarte (1 - " + String(n) + "):");
    while (!Serial.available());

    int choice = Serial.parseInt();
    if (choice > 0 && choice <= n) {
      String selectedSSID = WiFi.SSID(choice - 1);
      Serial.print("Seleccionaste: ");
      Serial.println(selectedSSID);

      // Solicitar la contraseña de la red seleccionada
      requestPassword(selectedSSID);
    } else {
      Serial.println("Selección inválida.");
    }
  }
}

// Función para solicitar la contraseña
void requestPassword(String ssid) {
  Serial.println("La red seleccionada requiere una contraseña.");
  Serial.println("Ingresa la contraseña para la red '" + ssid + "':");

  String enteredPassword = readPassword();  // Función para leer la contraseña

  connectToNetwork(ssid, enteredPassword);  // Conectar a la red
}

// Función para leer la contraseña
String readPassword() {
  String password = "";
  while (true) {
    if (Serial.available()) {
      password = Serial.readStringUntil('\n');
      password.trim();  // Eliminar espacios o saltos de línea
      if (password.length() > 0) break; // Salir si la contraseña no está vacía
    }
  }
  return password;
}

// Función para conectar a la red Wi-Fi con la contraseña proporcionada
void connectToNetwork(String ssid, String password) {
  WiFi.begin(ssid.c_str(), password.c_str());

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConexión exitosa.");
    Serial.print("Dirección IP: ");
    Serial.println(WiFi.localIP());

    // Solicitar URL del servidor después de la conexión Wi-Fi
    serverUrl = readServerUrl();  // Obtener la URL del servidor desde el monitor serial
    Serial.println("URL del servidor configurada: " + serverUrl);
  } else {
    Serial.println("Error al conectar.");
  }
}

// Función para leer la URL del servidor
String readServerUrl() {
  String url = "";
  Serial.println("Ingresa la URL del servidor:");

  while (true) {
    if (Serial.available()) {
      url = Serial.readStringUntil('\n');
      url.trim();  // Eliminar espacios o saltos de línea
      if (url.length() > 0) break; // Salir si la URL no está vacía
    }
  }
  return url;
}

// Función para iniciar la grabación
void startRecording() {
  Serial.println("Esperando para iniciar la grabación...");
  pinMode(REC_PIN, INPUT_PULLUP);  // Configurar botón de grabación

  while (true) {
    int buttonStateRec = digitalRead(REC_PIN);  // Leer el estado del botón de grabación

    // Detectar si se presionó el botón de grabación
    if (buttonStateRec == LOW && (millis() - lastDebounceTime) > debounceDelay) {
      lastDebounceTime = millis();  // Actualizar el tiempo de debounce
      Serial.println("Iniciando grabación...");
      
      // Simulación de grabación (reemplazar con código ISD1820 real)
      delay(3000);  // Simulación de 3 segundos de grabación

      // Guardar audio simulado en SPIFFS (en una ruta temporal)
      File audioFile = SPIFFS.open("/audio_grabado.wav", FILE_WRITE);
      byte audioData[] = { 0x00, 0x01, 0x02, 0x03, 0x04 };  // Datos de audio simulados
      audioFile.write(audioData, sizeof(audioData));
      audioFile.close();

      Serial.println("Grabación finalizada. Enviando datos al servidor...");
      sendAudioToServer("/audio_grabado.wav");
      break;  // Terminar el ciclo de grabación
    }
  }
}

// Función para enviar el audio grabado al servidor
void sendAudioToServer(String filePath) {
  if (serverUrl.length() > 0) {
    File file = SPIFFS.open(filePath, FILE_READ);
    if (!file) {
      Serial.println("No se pudo abrir el archivo de audio.");
      return;
    }

    HTTPClient http;
    http.begin(serverUrl); // Iniciar conexión HTTP con la URL del servidor

    http.addHeader("Content-Type", "application/octet-stream"); // Tipo de contenido binario
    http.addHeader("Content-Disposition", "attachment; filename=\"audio_grabado.wav\""); // Nombre del archivo

    int httpResponseCode = http.sendRequest("POST", &file, file.size()); // Enviar los datos

    if (httpResponseCode > 0) {
      Serial.print("Respuesta del servidor: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error al enviar datos al servidor: ");
      Serial.println(httpResponseCode);
    }

    file.close();  // Cerrar el archivo
    http.end();  // Finalizar la conexión HTTP
  } else {
    Serial.println("URL del servidor no configurada.");
  }
}


