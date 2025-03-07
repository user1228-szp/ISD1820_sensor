import serial
import wave
import numpy as np

# Configura el puerto serial donde está conectado el ESP32 (ajusta según sea necesario)
ser = serial.Serial('COM6', 115200)  # 'COM3' es un ejemplo, usa el puerto correcto
output_filename = 'grabacion.wav'

# Parámetros de la grabación
sampling_rate = 8000  # Frecuencia de muestreo, ajusta si es necesario
num_samples = 80000  # Número de muestras (ajusta según la duración de la grabación)

# Crear archivo WAV
output_file = wave.open(output_filename, 'wb')
output_file.setnchannels(1)  # Mono
output_file.setsampwidth(2)  # 2 bytes (16 bits por muestra)
output_file.setframerate(sampling_rate)

print("Esperando datos del ESP32...")

# Lee los datos desde el puerto serial y guárdalos en el archivo WAV
audio_data = []

for _ in range(num_samples):
    if ser.in_waiting > 0:
        byte = ser.read()  # Lee un byte del puerto serial
        audio_data.append(ord(byte))  # Almacena el valor del byte

# Convertir la lista de datos a un arreglo numpy para procesamiento
audio_data = np.array(audio_data, dtype=np.int16)

# Escribir los datos de audio en el archivo WAV
output_file.writeframes(audio_data.tobytes())

# Cerrar el archivo y el puerto serial
output_file.close()
ser.close()

print(f"Grabación guardada como {output_filename}")
