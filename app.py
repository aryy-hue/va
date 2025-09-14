import os
import subprocess
import uuid
from flask import Flask, render_template, request, jsonify, url_for, session
import ollama # Pastikan Anda mengimpor ollama di sini

app = Flask(__name__)
app.secret_key = 'supersecret'

# --- Konfigurasi Path ---
# Pastikan path ini sesuai dengan struktur folder Anda
PIPER_PATH = os.path.join("piper", "piper")
MODEL_PATH = os.path.join("piper", "models", "en_US-amy-low.onnx")
OUTPUT_DIR = "static"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_audio(text):
    """Fungsi untuk menghasilkan file audio dari teks menggunakan Piper TTS."""
    print(f"Generating audio for: '{text}'")
    unique_filename = f"response_{uuid.uuid4()}.wav"
    output_path = os.path.join(OUTPUT_DIR, unique_filename)
    
    command = [
        PIPER_PATH,
        '--model', MODEL_PATH,
        '--output_file', output_path
    ]
    
    try:
        # Menggunakan Popen untuk mengirim teks ke stdin
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=text.encode('utf-8'))
        print(f"✅ Audio generated: {unique_filename}")
        return unique_filename
    except FileNotFoundError:
        print(f"❌ ERROR: Piper executable not found at '{PIPER_PATH}'. Please check the path.")
        return None
    except Exception as e:
        print(f"❌ An error occurred with Piper: {e}")
        return None

def get_llm_response(conversation_history):
    """
    Mendapatkan respons dari model bahasa (Llama 3) berdasarkan riwayat percakapan.
    """
    print("Getting response from Llama 3... 🧠")
    try:
        response = ollama.chat(
            model='llama3:8b',
            messages=conversation_history  
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ An error occurred with Ollama: {e}")
        return "Maaf, saya sedang mengalami kesulitan terhubung dengan model bahasa."

@app.route('/')
def index():
    """Merender halaman utama dan mereset riwayat chat."""
    session.pop('chat_history', None)
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Menerima prompt dari pengguna, mendapatkan respons, dan mengembalikan teks serta URL audio."""
    data = request.get_json()
    user_prompt = data.get('prompt')
    
    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Mengambil atau membuat riwayat chat dari session
    chat_history = session.get('chat_history', [])

    # Menambahkan instruksi sistem jika ini adalah pesan pertama
    if not chat_history:
        chat_history.append({'role': 'system', 'content': 'You are a helpful assistant. Keep your answers concise and friendly.'})

    chat_history.append({'role': 'user', 'content': user_prompt})

    # Dapatkan respons dari LLM
    assistant_text = get_llm_response(chat_history)
    
    # Tambahkan respons asisten ke riwayat
    chat_history.append({'role': 'assistant', 'content': assistant_text})

    # Simpan kembali riwayat chat ke session
    session['chat_history'] = chat_history

    # Hasilkan audio dari teks respons
    audio_filename = generate_audio(assistant_text)
    audio_url = url_for('static', filename=audio_filename, _external=True) if audio_filename else None

    return jsonify({
        'response_text': assistant_text,
        'audio_url': audio_url
    })

if __name__ == '__main__':
    app.run(debug=True)

