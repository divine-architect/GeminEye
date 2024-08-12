import google.generativeai as genai
from dotenv import load_dotenv
import os
import PIL.Image
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
import pygame
import requests
import time
from datetime import datetime

load_dotenv()

genai.configure(api_key=os.getenv('google_key'))
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

def get_location():
    try:
        response = requests.get('https://ipapi.co/json/')
        data = response.json()
        return f"{data['city']}, {data['region']}, {data['country_name']}"
    except:
        return "Location unavailable"

def gener(query, chat):
    current_location = get_location()
    current_date = time.strftime("%d/%m/%y")
    now = datetime.now()
    time_string = now.strftime("%I:%M %p")
    prompt = f"""
Please provide factual, concise responses to assist a visually impaired user named Sachit with daily tasks and queries. When an image is provided, describe it accurately without speculation. Offer relevant safety advice when appropriate, but avoid unnecessary warnings. Responses should be clear, simple to understand, and avoid providing speculative information, especially regarding navigation or directions without proper context. The current location is {current_location} and the date is {current_date} in d/m/y format, and time is {time_string}. Sachit's query is: {query}
    """
    response = chat.send_message([prompt])
    return response.text

def recognize_speech(timeout=15):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=timeout)
        except sr.WaitTimeoutError:
            speak("No speech detected within the timeout period.")
            return None
    
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand that.")
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")

def speak(text, lang='en-us', slow=False):
    tts = gTTS(text=text, lang=lang, slow=slow)
    tts.save("temp.mp3")
    
    pygame.mixer.init()
    pygame.mixer.music.load("temp.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.quit()
    os.remove("temp.mp3")

speak("Speak now:")
userinput = recognize_speech(timeout=15)
if userinput:
    response = gener(userinput, chat)
    speak(response, lang='en-us')
else:
    speak("No input detected. Try again.")
