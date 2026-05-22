import webbrowser
import difflib
import requests
import pyttsx3
import threading
from openai import OpenAI
from apikeys import openrouter_api, news_API
import MusicLibrary

openrouter_api = st.secrets["OPENROUTER_API"]
news_API = st.secrets["NEWS_API"]

# speak() runs in its own thread so it NEVER blocks the callback
def speak(text):
    def _run():
        try:
            eng = pyttsx3.init()
            eng.setProperty('rate', 175)
            eng.say(text)
            eng.runAndWait()
            eng.stop()
        except Exception as e:
            print("Speech Error:", e)
    threading.Thread(target=_run, daemon=True).start()


def aiProcess(command):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api
        )
        completion = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=[
                {"role": "system", "content": "You are Jarvis, a futuristic AI assistant. Give short helpful responses."},
                {"role": "user",   "content": command}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"


def processCommand(command):
    command = command.lower().strip()
    response = ""
    try:
        if "open google" in command:
            webbrowser.open("https://google.com")
            response = "Opening Google, sir."

        elif "open youtube" in command:
            webbrowser.open("https://youtube.com")
            response = "Opening YouTube, sir."

        elif "open facebook" in command:
            webbrowser.open("https://facebook.com")
            response = "Opening Facebook, sir."

        elif "open linkedin" in command:
            webbrowser.open("https://linkedin.com")
            response = "Opening LinkedIn, sir."

        elif command.startswith("play"):
            song = command.replace("play", "").strip()
            matches = difflib.get_close_matches(song, MusicLibrary.music.keys(), n=1, cutoff=0.5)
            if matches:
                best_match = matches[0]
                response = f"Playing {best_match}, sir."
                webbrowser.open(MusicLibrary.music[best_match])
            else:
                response = f"Playing {song} on YouTube, sir."
                # Direct YouTube search — faster than pywhatkit
                query = song.replace(" ", "+")
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")

        elif "news" in command:
            r = requests.get(
                f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_API}",
                timeout=6
            )
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                headlines = [a['title'] for a in articles if a.get('title')][:5]
                response = "Top Headlines:\n\n" + "\n\n".join(f"• {h}" for h in headlines)
            else:
                response = "Unable to fetch news right now."

        else:
            response = aiProcess(command)

        speak(response)
        return response

    except Exception as e:
        err = f"Command Error: {e}"
        speak(err)
        return err
