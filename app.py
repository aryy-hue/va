import os
import subprocess
import uuid
from flask import Flask, render_template, request, jsonify, url_for, session


app = Flask(__name__)
app.secret_key = 'kunci-rahasia-super-acak-untuk-proyek-va'

PIPER_PATH = os.path.join("piper", "piper")
MODEL_PATH = os.path.join("piper", "models", "en_US-amy-low.onnx")
OUTPUT_DIR = "static"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_audio(text):
    print(f"Generating audio for: '{text}'")
    unique_filename = f"response_{uuid.uuid4()}.wav"
    output_path = os.path.join(OUTPUT_DIR, unique_filename)
    command = [
        PIPER_PATH,
        '--model', MODEL_PATH,
        '--output_file', output_path
    ]
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=text.encode('utf-8'))
        return unique_filename
    except Exception as e:
        print(f"❌ An error occurred with Piper: {e}")
        return None

def get_llm_response(conversation_history):
    """
    PERUBAHAN DI SINI:
    Fungsi ini sekarang menerima seluruh riwayat percakapan.
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
        return "Sorry, I'm having trouble connecting to the language model."


@app.route('/')
def index():
    session.pop('chat_history', None)
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_prompt = data.get('prompt')
    
    if not user_prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    chat_history = session.get('chat_history', [])

    if not chat_history:
        chat_history.append({'role': 'system', 'content': 'You are a helpful assistant. Keep your answers concise.'})

    chat_history.append({'role': 'user', 'content': user_prompt})

    assistant_text = get_llm_response(chat_history)
    
    chat_history.append({'role': 'assistant', 'content': assistant_text})

    session['chat_history'] = chat_history

    audio_filename = generate_audio(assistant_text)
    audio_url = url_for('static', filename=audio_filename, _external=True) if audio_filename else None

    return jsonify({
        'response_text': assistant_text,
        'audio_url': audio_url
    })

if __name__ == '__main__':
    import ollama
    app.run(debug=True)
