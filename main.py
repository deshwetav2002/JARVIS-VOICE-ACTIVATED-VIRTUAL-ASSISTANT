import speech_recognition as sr
import webbrowser
import pyttsx3 
import pyaudio
import MusicLibrary
import difflib
import requests
import os
from openai import OpenAI 
from apikeys import openrouter_api
from apikeys import news_API
from gtts import gTTS
import pygame

recognizer = sr.Recognizer()
# engine = pyttsx3.init('sapi5')
newsAPI = news_API

''' 'sapi5' explicitly tells Python: "Use Windows Speech API version 5" 
Creating a fresh connection to SAPI5, Speaking immediately
Destroying it after use'''

def speak_old(text):
    engine = pyttsx3.init('sapi5')
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load('temp.mp3')

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3") 

def aiProcess(command):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key = openrouter_api
  )

    completion = client.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free",
    messages=[
        {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud. Give short responses please"},
        {"role": "user", "content": command}
    ]
    )

    return (completion.choices[0].message.content)

def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        song = c.lower().replace("play", "").strip()
        song = song.replace(".", "").strip()

        print("Recognized song:", song)

        matches = difflib.get_close_matches(song, MusicLibrary.music.keys(), n=1, cutoff=0.5)

        if matches:
            best_match = matches[0]
            speak(f"Playing {best_match}")
            webbrowser.open(MusicLibrary.music[best_match])
        else:
            speak("Song not found")

    elif "news" in c.lower():
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsAPI}")
        if r.status_code == 200:
            # Parse the JSON response
            data = r.json()
            
            # Extract the articles
            articles = data.get('articles', [])
            
            # Print the headlines
            for article in articles:
                speak(article['title'])

    else:
        #let openAI handle the request
        output = aiProcess(c)
        speak(output)


if __name__ == "__main__":
    speak("Initializing Jarvis")
    while True:
        # listen for the wake word "Jarvis"
        # obtain audio from the microphone
        r = sr.Recognizer()
            
        # print("Recognizing...")
        # recognize speech using google
        
        
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5)
            word = r.recognize_google(audio)
            # command = r.recognize_google(audio)
            if (word.lower()=="jarvis"):
                speak("Yaa")
                #listen for command
                print("Jarvis Active...")
                with sr.Microphone() as source:
                    audio = r.listen(source, timeout=5)
                    command = r.recognize_google(audio)
                # print("Heard:", command)

                    processCommand(command)

        except Exception as e:
            print(f"Error: {e}")
