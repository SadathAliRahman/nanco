from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from groq import Groq
from dotenv import load_dotenv
import tempfile

load_dotenv()

app = Flask(__name__)
# Enable CORS so our frontend can communicate with the backend
CORS(app)

# Initialize Groq client safely.
api_key = os.environ.get("GROQ_API_KEY")
client = None
if api_key:
    try:
        client = Groq(key=api_key) if hasattr(Groq, 'key') else Groq(api_key=api_key)
    except Exception as init_err:
        print(f"Failed to initialize Groq client: {init_err}")

@app.route('/')
@app.route('/api')
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Nanco AI Chatbot Backend is running on Vercel!"
    })

@app.route('/api/chat', methods=['POST'])
@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({
            'error': 'Groq client not initialized. Please ensure the GROQ_API_KEY environment variable is configured in Vercel project settings.'
        }), 500

    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message is required'}), 400

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are Nanco AI, a highly intelligent and helpful assistant for Nanco Paints. Keep your answers concise, professional, and friendly."
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            model="llama-3.1-8b-instant",
        )
        response_text = chat_completion.choices[0].message.content
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/voice', methods=['POST'])
@app.route('/voice', methods=['POST'])
def voice():
    if not client:
        return jsonify({
            'error': 'Groq client not initialized. Please ensure the GROQ_API_KEY environment variable is configured in Vercel project settings.'
        }), 500

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    
    try:
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            audio_file.save(temp_audio.name)
            temp_audio_path = temp_audio.name

        # Transcribe using Groq Whisper API
        with open(temp_audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(temp_audio_path, file.read()),
                model="whisper-large-v3",
                response_format="json",
                language="en"
			)
            
        # Clean up temp file
        os.remove(temp_audio_path)
        
        user_text = transcription.text
        
        # Forward the transcribed text to the LLM
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are Nanco AI, a highly intelligent and helpful assistant for Nanco Paints. Keep your answers concise, professional, and friendly."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            model="llama-3.1-8b-instant",
        )
        response_text = chat_completion.choices[0].message.content
        
        return jsonify({
            'transcription': user_text,
            'response': response_text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
