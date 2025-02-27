import os
import time
import wave
import struct
from threading import Thread
from flask import Flask, request, jsonify, render_template_string
import serial

app = Flask(__name__)

# Configuración del puerto serie y otros parámetros
SERIAL_PORT = "COM3"  # Cambia este valor al puerto donde está conectado tu Arduino
BAUD_RATE = 115200

# Carpeta donde se guardarán las grabaciones
UPLOAD_FOLDER = "static"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Ruta del archivo de audio grabado
AUDIO_FILE_PATH = os.path.join(UPLOAD_FOLDER, "recorded_audio.wav")

# Variables globales para controlar la grabación
is_recording = False
wave_file = None

def record_audio_from_arduino():
    """Función que lee datos del Arduino y los escribe en un archivo WAV cuando se activa la grabación."""
    global is_recording, wave_file
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"Error al abrir el puerto serie: {e}")
        return

    while True:
        if is_recording:
            # Si se inicia la grabación y el archivo no está abierto, se abre
            if wave_file is None:
                wave_file = wave.open(AUDIO_FILE_PATH, 'wb')
                wave_file.setnchannels(1)     # Mono
                wave_file.setsampwidth(2)       # 16 bits (2 bytes)
                wave_file.setframerate(8000)    # Frecuencia de muestreo de 8 kHz
                print("Grabación iniciada...")

            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode("utf-8").strip()
                    if line.isdigit():
                        sample = int(line)
                        # Empaquetar la muestra en formato PCM 16-bit little endian
                        audio_bytes = struct.pack('<h', sample)
                        wave_file.writeframes(audio_bytes)
                except Exception as e:
                    print(f"Error al leer/escribir: {e}")
        else:
            # Si no se está grabando y el archivo está abierto, se cierra
            if wave_file is not None:
                wave_file.close()
                wave_file = None
                print("Grabación detenida.")
            time.sleep(0.1)  # Evitar busy waiting

# Página principal con botones para controlar la grabación
@app.route('/')
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Control de Grabación</title>
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
            audio {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Control de Grabación</h1>
            <button class="button" onclick="startRecording()">Iniciar Grabación</button>
            <button class="button" onclick="stopRecording()">Detener Grabación</button>
            <p id="status"></p>
            <h2>Reproducir Grabación</h2>
            <audio id="audioPlayer" controls>
                <source src="/static/recorded_audio.wav" type="audio/wav">
            </audio>
        </div>

        <script>
            function startRecording() {
                fetch("/start_recording", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("status").innerText = data.message;
                })
                .catch(error => {
                    document.getElementById("status").innerText = "Error al iniciar grabación.";
                });
            }

            function stopRecording() {
                fetch("/stop_recording", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("status").innerText = data.message;
                })
                .catch(error => {
                    document.getElementById("status").innerText = "Error al detener grabación.";
                });
            }
        </script>
    </body>
    </html>
    """)

# Endpoint para iniciar la grabación
@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording
    is_recording = True
    return jsonify({"message": "Grabación iniciada."})

# Endpoint para detener la grabación
@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording
    is_recording = False
    return jsonify({"message": "Grabación detenida."})

if __name__ == '__main__':
    # Iniciar en un hilo separado la función que lee del Arduino
    t = Thread(target=record_audio_from_arduino, daemon=True)
    t.start()
    app.run(debug=True)
