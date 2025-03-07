import os
import time
import wave
from flask import Flask, render_template, request, send_file, jsonify

# Configuración Flask
app = Flask(__name__)
UPLOAD_FOLDER = 'grabaciones'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ruta para la página principal
@app.route('/')
def index():
    archivos = os.listdir(UPLOAD_FOLDER)
    archivos.sort(reverse=True)
    return render_template('index.html', archivos=archivos)

# Ruta para descargar archivos
@app.route('/descargar/<nombre>')
def descargar(nombre):
    ruta = os.path.join(UPLOAD_FOLDER, nombre)
    return send_file(ruta, as_attachment=True)

# Ruta para eliminar archivos
@app.route('/eliminar/<nombre>', methods=['POST'])
def eliminar(nombre):
    ruta = os.path.join(UPLOAD_FOLDER, nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        return jsonify({'mensaje': 'Archivo eliminado correctamente'})
    else:
        return jsonify({'error': 'Archivo no encontrado'}), 404

# Ruta para actualizar lista de archivos
@app.route('/actualizar')
def actualizar():
    archivos = os.listdir(UPLOAD_FOLDER)
    archivos.sort(reverse=True)
    return jsonify(archivos)

# Ruta para recibir el archivo de audio del cliente
@app.route('/subir_audio', methods=['POST'])
def subir_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Guardar el archivo recibido en la carpeta 'grabaciones'
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Confirmar la recepción y almacenamiento del archivo
    return jsonify({'mensaje': 'Archivo recibido correctamente', 'nombre': file.filename})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
