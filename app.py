from flask import Flask, request, jsonify, send_file
import tempfile
import basic_pitch.inference as inference
import os

app = Flask(__name__)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    file = request.files['audio']
    if not file:
        return jsonify({"error": "Nessun file ricevuto"}), 400

    # Salva il file temporaneamente con estensione originale
    temp_input_path = tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[-1], delete=False).name
    file.save(temp_input_path)

    # Converte il file in WAV con ffmpeg
    temp_output_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    conversion_result = os.system(f"ffmpeg -y -i \"{temp_input_path}\" -ar 22050 -ac 1 \"{temp_output_path}\"")

    if conversion_result != 0:
        os.remove(temp_input_path)
        return jsonify({"error": "Errore durante la conversione audio"}), 500

    try:
        output = inference.predict([temp_output_path], save_midi=True)
        if output and isinstance(output, list) and 'note_sequence' in output[0]:
            midi_notes = output[0]['note_sequence']
            return jsonify({ "notes": midi_notes })
        else:
            return jsonify({ "error": "Analisi audio fallita." }), 500
    except Exception as e:
        return jsonify({"error": f"Errore nella trascrizione: {str(e)}"}), 500
    finally:
        os.remove(temp_input_path)
        os.remove(temp_output_path)

@app.route('/download_midi', methods=['GET'])
def download_midi():
    return send_file("output.mid", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
