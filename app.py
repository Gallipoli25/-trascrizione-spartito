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
    temp_path = tempfile.NamedTemporaryFile(suffix='.webm', delete=False).name
    file.save(temp_path)

    wav_path = temp_path.replace('.webm', '.wav')
    os.system(f"ffmpeg -i {temp_path} -ar 22050 -ac 1 {wav_path}")

    try:
        output = inference.predict([wav_path], save_midi=True)

        os.remove(temp_path)
        os.remove(wav_path)

        if output and isinstance(output, list) and 'note_sequence' in output[0]:
            midi_notes = output[0]['note_sequence']
            return jsonify({ "notes": midi_notes })
        else:
            return jsonify({ "error": "Analisi audio fallita." }), 500

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

@app.route('/download_midi', methods=['GET'])
def download_midi():
    return send_file("output.mid", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
