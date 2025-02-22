import serial
import wave
import os
import struct
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Configurar puerto serie (ajustar el puerto según tu sistema)
SERIAL_PORT = "COM3"  # Cambia esto a tu puerto
BAUD_RATE = 115200

# Configurar carpeta de almacenamiento
UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ruta del archivo donde se guardará el audio capturado desde Arduino
AUDIO_FILE_PATH = os.path.join(UPLOAD_FOLDER, "recorded_audio.wav")

# Página principal con la interfaz web
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Aplicación Flask</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                flex-direction: column;
            }
            h1 {
                color: #333;
            }
            .container {
                text-align: center;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .button {
                padding: 10px 15px;
                font-size: 16px;
                color: white;
                background-color: #007BFF;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            .button:hover {
                background-color: #0056b3;
            }
            #image-container, #audio-container {
                margin-top: 20px;
                display: none;
                text-align: center;
            }
            #image-container img {
                max-width: 100%;
                height: auto;
            }
            input[type="file"] {
                margin-top: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Audio</h1>
            
            <h2>Subir Archivo de Voz</h2>
            <input type="file" id="fileInput" accept="audio/*">
            <button class="button" onclick="uploadVoice()">Subir Voz</button>
            <p id="status"></p>

            <h2>Reproducir Audio Recibido</h2>
            <button class="button" onclick="playAudio()">Escuchar Grabación</button>
            <audio id="audioPlayer" controls style="display:none;">
                <source src="/static/recorded_audio.wav" type="audio/wav">
            </audio>
        </div>

        <script>
            function toggleImage() {
                const imageContainer = document.getElementById('image-container');
                imageContainer.style.display = imageContainer.style.display === 'none' ? 'block' : 'none';
            }

            function uploadVoice() {
                const fileInput = document.getElementById('fileInput');
                const status = document.getElementById('status');

                if (fileInput.files.length === 0) {
                    status.innerText = "Selecciona un archivo primero.";
                    return;
                }

                const formData = new FormData();
                formData.append("file", fileInput.files[0]);

                fetch("/upload", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    status.innerText = data.message;
                })
                .catch(error => {
                    status.innerText = "Error al subir el archivo.";
                });
            }

            function playAudio() {
                const audio = document.getElementById("audioPlayer");
                audio.style.display = "block";
                audio.play();
            }
        </script>
    </body>
    </html>
    """)

# Ruta para subir archivos de voz manualmente
@app.route('/upload', methods=['POST'])
def upload_voice():
    if 'file' not in request.files:
        return jsonify({"message": "No se encontró ningún archivo."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No se seleccionó ningún archivo."}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return jsonify({"message": "Archivo subido exitosamente.", "file_path": file_path})

# Función para recibir audio en tiempo real desde Arduino y guardarlo como WAV
def record_audio_from_arduino():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    with wave.open(AUDIO_FILE_PATH, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(8000)  # 8kHz de muestreo

        print("Grabando desde Arduino...")

        try:
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode("utf-8").strip()
                    if line.isdigit():
                        sample = int(line)
                        audio_bytes = struct.pack('<h', sample)  # Convertir a 16-bit PCM
                        wf.writeframes(audio_bytes)
        except KeyboardInterrupt:
            print("Grabación detenida.")
            ser.close()

# **Ejecución principal**
if __name__ == '__main__':
    from threading import Thread
    # Hilo para grabar audio en segundo plano
    arduino_thread = Thread(target=record_audio_from_arduino, daemon=True)
    arduino_thread.start()

    # Iniciar Flask
    app.run(debug=True)
