import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import google.generativeai as genai
import os
import time
import tempfile
from pydub import AudioSegment
from pydub.playback import play


# Set the API key for Google Generative AI
os.environ["API_KEY"] = 'AIzaSyBGo6U2he1QpppItMKpSW2jzy5BI_mKRnE'

# Configure the Google Generative AI model
genai.configure(api_key=os.environ["API_KEY"])

# Initialize the recognizer
recognizer = sr.Recognizer()

def speech_to_text():
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

        try:
            text = recognizer.recognize_google(audio)
            st.write("You said:", text)
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.write("Sorry, my speech service is down.")
            return None

def process_text_with_llm(text):
    """Generate a response using Google Generative AI based on input text."""
    model = genai.GenerativeModel('gemini-1.0-pro')
    text += '. Answer it to the point within 150 words in appropriate manner in a conversational tone. Your answer will be read out as text to speech.'
    response = model.generate_content(text)
    
    reply = response.text
    st.write("LLM replied:", reply)
    return reply

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        tts.save(temp_audio_file.name)
        audio = AudioSegment.from_mp3(temp_audio_file.name)
        play(audio)
        return temp_audio_file.name

# Streamlit app layout
st.title("Continuous AI-Powered Speech Assistant")

# Continuous loop implementation
if st.button('Start'):
    st.write("Starting continuous listening...")
    while True:
        # Listen to the speech input
        input_text = speech_to_text()
        if input_text:
            # Process the text with LLM
            llm_reply = process_text_with_llm(input_text)
            # Convert LLM reply to speech
            audio_file = text_to_speech(llm_reply)
            st.audio(audio_file, format='audio/mp3')
        
        # A small delay to avoid too rapid looping
        time.sleep(1)
