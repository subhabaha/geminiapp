
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import os
import tempfile
from pydub import AudioSegment

# Set the API key for Google Generative AI
os.environ["API_KEY"] = 'YOUR_GOOGLE_API_KEY'

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
    """Generate a response using Google Generative AI based on input text."""
    model = genai.GenerativeModel('gemini-1.0-pro')
    text += '. Answer it to the point within 150 words in a conversational tone.'
    response = model.generate_content(text)
    return response.text

st.title("Real-Time Audio Processing with Streamlit")

# Serving the HTML file within Streamlit
with open("continuous_audio_capture.html", "r") as html_file:
    html_content = html_file.read()

st.components.v1.html(html_content, height=600)

# Handle incoming POST request from JavaScript
if st.request.method == 'POST':
    audio_file = st.request.files.get('audio')
    if audio_file:
        with tempfile.NamedTemporaryFile(delete=False) as temp_audio:
            temp_audio.write(audio_file.read())
            temp_audio.flush()

            # Process the audio to get the text
            recognized_text = process_audio(temp_audio.name)

            # Process the text with LLM
            response_text = process_text_with_llm(recognized_text)

            st.json({"response": response_text})


