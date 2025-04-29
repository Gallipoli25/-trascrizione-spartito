
from flask import Flask, request, jsonify, send_file
import tempfile
import basic_pitch.inference as inference
import os

app = Flask(__name__)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    file = request.files['audio']
    temp_path = tempfile.NamedTemporaryFile(suffix='.webm', delete=False).name
    file.save(temp_path)

    wav_path = temp_path.replace('.webm', '.wav')
    os.system(f"ffmpeg -i {temp_path} -ar 22050 -ac 1 {wav_path}")

    output_path = "output.mid"
    output = inference.predict([wav_path], output_directory=".", save_midi=True)

    os.remove(temp_path)
    os.remove(wav_path)

    midi_notes = output['note_sequence']
    return jsonify(midi_notes)

@app.route('/download_midi', methods=['GET'])
def download_midi():
    midi_path = 'output.mid'
    return send_file(midi_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
