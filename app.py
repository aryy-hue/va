import os
import subprocess
import tempfile
import ollama


PIPER_PATH = os.path.join("piper", "piper")
MODEL_PATH = os.path.join("piper", "models", "en_US-amy-low.onnx")

def speak(text):
    """Mengubah teks menjadi suara menggunakan Piper dan memainkannya."""
    print(f"Assistant 🗣️: {text}")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
        output_path = output_file.name
    
    command = [
        PIPER_PATH,
        '--model', MODEL_PATH,
        '--output_file', output_path
    ]
    
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=text.encode('utf-8'))
        
        if os.name == 'nt':
            os.system(f'start /min "" "{output_path}"')
        elif os.uname().sysname == 'Darwin':
            os.system(f"afplay '{output_path}'")
        else:
            os.system(f"aplay -q '{output_path}'")

    except FileNotFoundError:
        print(f"❌ ERROR: Piper executable not found at '{PIPER_PATH}'.")
    except Exception as e:
        print(f"❌ An error occurred with Piper: {e}")

def get_llm_response(prompt):
    """Mengirim prompt ke Ollama (Llama 3) dan mendapatkan respons teks."""
    print("Assistant is thinking... 🧠")
    try:
       
        response = ollama.chat(
            model='llama3:8b',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant. Keep your answers concise and to the point.'},
                {'role': 'user', 'content': prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ An error occurred with Ollama: {e}")
        return "Sorry, I'm having trouble connecting to the language model."

# --- PROGRAM UTAMA ---
if __name__ == "__main__":
    speak("Hello, I am ready. What can I help you with?")
    
    while True:
        try:
            user_input = input("You 👤: ")
            if user_input.lower() in ['exit', 'quit', 'keluar']:
                speak("Goodbye!")
                break
            
            if user_input:
                assistant_response = get_llm_response(user_input)
                
                speak(assistant_response)

        except KeyboardInterrupt:
            print("\nProgram stopped.")
            break
