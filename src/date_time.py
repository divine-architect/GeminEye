import google.generativeai as genai
from dotenv import load_dotenv
import os
from duckduckgo_search import DDGS
from newspaper import Article, Config
import speech_recognition as sr
from gtts import gTTS
import pygame
from datetime import datetime
from twilio.rest import Client
import cv2
import requests
import geocoder
import time
import praw
import subprocess

load_dotenv()


account_sid = os.getenv('acc_sid_twi')
auth_token = os.getenv('auth_toke_twi')
twilio_phone_number = os.getenv('twiphone')
emergency_contact_number = os.getenv('emerno')
imgur_client_id = os.getenv('imgurid')
client = Client(account_sid, auth_token)


genai.configure(api_key=os.getenv('google_key'))
model = genai.GenerativeModel("gemini-pro")


reddit = praw.Reddit(
    client_id=os.getenv('reddit_client_id'),
    client_secret=os.getenv('reddit_client_secret'),
    user_agent='gemineye'
)


safe = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
]


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
        return None
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")
        return None


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


def search_and_summarize(query):
    try:
        results = DDGS().text(query, max_results=3)
        summarized_results = []

        for i in results:
            try:
                url = i.get("href")
                url = url.strip()
                if url:
                    user_agent = 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                    config = Config()
                    config.browser_user_agent = user_agent
                    article = Article(url, config=config)
                    article.download()
                    article.parse()
                    summarized_results.append(article.text)
                else:
                    summarized_results.append("No valid URL found.")
            except Exception as e:
                summarized_results.append(f"Error in fetching article from URL {url}: {e}")
                print(e)
        
        return summarized_results

    except Exception as e:
        print(f"Error in searching and summarizing: {e}")
        speak("There was an error performing the search.")
        return ["Error performing search"]


def summarize_top_articles_from_worldnews():
    try:
        subreddit = reddit.subreddit('worldnews')
        top_articles = subreddit.rising(limit=10)
        
        summarized_results = []
        user_agent = 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        config = Config()
        config.browser_user_agent = user_agent

        for submission in top_articles:
            url = submission.url
            url = url.strip()
            try:
                article = Article(url, config=config)
                article.download()
                article.parse()
                summarized_results.append(article.text)
            except Exception as e:
                print(f"Error in fetching article from URL {url}: {e}")
                summarized_results.append(f"Error: {e}")

        combined_results = "\n\n".join(summarized_results)
        summary = summarize_with_gemini("Top 5 news articles from r/worldnews", combined_results)
        speak(summary)

    except Exception as e:
        print(f"Error in summarizing top articles from r/worldnews: {e}")
        speak("There was an error retrieving news articles.")


def summarize_with_gemini(user_query, results):
    prompt = f"""
    Take the role of Gemineye, the AI processing unit of a handheld device used to aid visually impaired users. Do not use punctuations (such as *) since your output will be narrated.
    Summarize the given text in a concise form so that the user can understand what is happening. It's a web search. If you're ines, do not repeat about a topic more than 2 times.
    Do not use '-' or '*' in your output, simply recite them with numbers.
    User query: {user_query}
    Results: {results}
    """
    
    response = model.generate_content([prompt], stream=False, safety_settings=safe)
    return response.text

def listen_for_command():
    speak("Listening for command...")
    recognizer = sr.Recognizer()
   
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    try:
        command = recognizer.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        speak("Sorry, there was an error with the speech recognition service.")
        return None


def get_current_datetime():
    now = datetime.now()
    date_string = now.strftime("%B %d, 2024")
    time_string = now.strftime("%I:%M %p")
    return f"The current date is {date_string}, and the time is {time_string}."

#img cap
def capture_and_upload_image():
    try:
        command = ['libcamera-still', '-o', 'emergency.jpg']
        subprocess.run(command)
        url = "https://api.imgur.com/3/image"
        payload = {
            'type': 'image',
            'title': 'Emergency Situation',
            'description': 'Image captured during an emergency alert'
        }
        files = [
            ('image', ('emergency.jpg', open('emergency.jpg', 'rb'), 'image/jpeg'))
        ]
        headers = {
            'Authorization': f'Client-ID {imgur_client_id}'
        }
        
        response = requests.post(url, headers=headers, data=payload, files=files)
        os.remove('emergency.jpg')
        
        if response.status_code == 200:
            return response.json()['data']['link']
        else:
            return "Failed to upload image"
    except Exception as e:
        print(f"Error in capturing and uploading image: {e}")
        return "Failed to capture image"


def get_location_and_ip():
    g = geocoder.ip('me')
    ip = requests.get('https://api.ipify.org').text
    return f"Location: {g.latlng}, IP: {ip}"

#twilio interface NEEDS WORK!!
def send_emergency_text():
    try:
        image_url = capture_and_upload_image()
        location_info = get_location_and_ip()
        
        message_body = f"""
        Emergency alert! The user has requested assistance.
        Image: {image_url}
        {location_info}
        """
        
        message = client.messages.create(
            body=message_body,
            from_=twilio_phone_number,
            to=emergency_contact_number
        )
        speak("Emergency alert sent successfully with image and location information.")
    except Exception as e:
        speak("There was an error sending the emergency alert.")
        print(f"Error: {e}")


def main():
    command = listen_for_command()
    if command:
        if "time" in command or "date" in command:
            datetime_info = get_current_datetime()
            speak(datetime_info)
        elif "emergency" in command:
            speak("Sending emergency alert with image and location information.")
            send_emergency_text()
        elif "search" in command:
            speak("Please enter your search query:")
            user_query = recognize_speech(timeout=15)
            if user_query:
                search_results = search_and_summarize(user_query)
                combined_results = "\n\n".join(search_results)
                summary = summarize_with_gemini(user_query, combined_results)
                speak(summary)
            else:
                speak("No input detected. Try again.")
        elif "news" in command:
            summarize_top_articles_from_worldnews()
        else:
            speak("Command not recognized.")
    else:
        speak("No command detected.")


if __name__ == "__main__":
    main()
