import streamlit as st
import os
import tempfile
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment

# Set the API key for Google Generative AI
os.environ["API_KEY"] = 'AIzaSyBGo6U2he1QpppItMKpSW2jzy5BI_mKRnE'

# Configure the Google Generative AI model
genai.configure(api_key=os.environ["API_KEY"])

def process_audio(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return "Sorry, I could not understand the audio."
        except sr.RequestError:
            return "Sorry, my speech service is down."

def process_text_with_llm(text):
    model = genai.GenerativeModel('gemini-1.0-pro')
    text += '. Answer it to the point within 150 words in a conversational tone.'
    response = model.generate_content(text)
    return response.text

st.title("Real-Time Audio Processing with Streamlit")

# Serve the HTML page within the Streamlit app
st.components.v1.html(
    """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Continuous Real-Time Audio Capture</title>
    </head>
    <body>
        <h1>Continuous Real-Time Audio Capture and Streamlit Integration</h1>
        <button onclick="startListening()">Start Conversation</button>
        <button onclick="stopListening()">Stop Conversation</button>
        <div id="response"></div>

        <script>
            let mediaRecorder;
            let audioChunks = [];
            let isListening = false;

            async function startListening() {
                isListening = true;
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                    if (mediaRecorder.state === 'inactive') {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        sendAudioToStreamlit(audioBlob);
                        audioChunks = [];
                    }
                };

                mediaRecorder.start();
                setInterval(() => {
                    if (mediaRecorder.state === 'recording') {
                        mediaRecorder.stop();
                        if (isListening) {
                            mediaRecorder.start();
                        }
                    }
                }, 5000); // Adjust interval as needed
            }

            function stopListening() {
                isListening = false;
                mediaRecorder.stop();
            }

            function sendAudioToStreamlit(audioBlob) {
                const formData = new FormData();
                formData.append('audio', audioBlob, 'audio.wav');

                fetch('/process-audio', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerText = 'Response: ' + data.response;
                    if (isListening) {
                        startListening();
                    }
                })
                .catch(error => console.error('Error sending audio:', error));
            }
        </script>
    </body>
    </html>
    """,
    height=600,
    scrolling=True
)

# Handle incoming POST request from JavaScript
if st.experimental_get_query_params().get('method') == ['POST']:
    audio_file = st.file_uploader("Upload an audio file", type=["wav", "mp3"])
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            temp_audio.write(audio_file.read())
            temp_audio.flush()

            recognized_text = process_audio(temp_audio.name)
            response_text = process_text_with_llm(recognized_text)

            st.json({"response": response_text})
