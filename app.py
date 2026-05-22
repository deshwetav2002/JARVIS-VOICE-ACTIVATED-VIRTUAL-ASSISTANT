import streamlit as st
import base64
from datetime import datetime
import speech_recognition as sr
import time
import threading

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── MODULE-LEVEL THREAD BUFFER ────────────────────────────────────────────────
_pending = []

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "listening" not in st.session_state: st.session_state.listening = False
if "stop_fn"   not in st.session_state: st.session_state.stop_fn   = None

# ── BACKGROUND IMAGE ──────────────────────────────────────────────────────────
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64("background.jpg")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{
    background-image:
    linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
    url("data:image/jpg;base64,{img}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
header {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
.main-title {{
    text-align: center;
    font-size: 75px;
    font-weight: bold;
    color: #00F5FF;
    text-shadow: 0px 0px 20px cyan;
}}
.sub-text {{
    text-align: center;
    color: white;
    font-size: 22px;
    margin-bottom: 30px;
}}
.orb {{
    width: 230px; height: 230px;
    border-radius: 50%;
    margin: auto;
    background: radial-gradient(circle, #00f5ff 0%, #0077ff 40%, transparent 75%);
    box-shadow: 0 0 30px #00f5ff, 0 0 70px #00f5ff, 0 0 140px #0077ff;
    animation: pulse 2.5s infinite;
}}
@keyframes pulse {{
    0%   {{ transform: scale(1);    }}
    50%  {{ transform: scale(1.08); }}
    100% {{ transform: scale(1);    }}
}}
.chat-box {{
    background: rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 15px;
    margin-top: 15px;
    color: white;
    border: 1px solid rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
}}
.stButton>button {{
    width: 100%;
    height: 60px;
    border-radius: 15px;
    background: linear-gradient(90deg,#00F5FF,#0077FF);
    color: white;
    font-size: 20px;
    font-weight: bold;
    border: none;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 JARVIS")
    st.success("System Online")
    st.write("✔ Voice Assistant")
    st.write("✔ AI Integrated")
    st.write("✔ Music System")
    st.write("✔ News System")

# ── MAIN UI ───────────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>JARVIS</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>AI Powered Virtual Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='orb'></div>", unsafe_allow_html=True)
current_time = datetime.now().strftime("%I:%M:%S %p")
st.markdown(f"<h2 style='text-align:center;color:white;'>🕒 {current_time}</h2>", unsafe_allow_html=True)
st.write("")
st.write("")

# ── RECOGNIZER ────────────────────────────────────────────────────────────────
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold         = 3500
recognizer.pause_threshold          = 0.8
recognizer.phrase_threshold         = 0.3

# ── SPEAK IN BACKGROUND THREAD ────────────────────────────────────────────────
def speak_async(text):
    def _run():
        try:
            import pyttsx3
            e = pyttsx3.init()
            e.setProperty('rate', 175)
            e.say(text)
            e.runAndWait()
            e.stop()
        except Exception as ex:
            print(f"[SPEAK] Error: {ex}")
    threading.Thread(target=_run, daemon=True).start()

# ── CALLBACK ──────────────────────────────────────────────────────────────────
# NO wake word — every phrase heard while listening is treated as a command.
# The user presses "Start Listening", speaks a command, Jarvis executes it.
# This is simpler, faster, and actually works with listen_in_background.
def callback(recognizer_instance, audio):
    try:
        text = recognizer_instance.recognize_google(audio)
        text = text.lower().strip()
        print(f"[MIC] Heard: '{text}'")

        if not text:
            return

        _pending.append(("You", text))

        try:
            processCommand = get_process_command()
            response = processCommand(text)
            if response:
                _pending.append(("Jarvis", response))
                speak_async(response)
        except Exception as e:
            print(f"[JARVIS] Command error: {e}")
            _pending.append(("Jarvis", f"Error: {e}"))

    except sr.UnknownValueError:
        pass
    except Exception as e:
        print(f"[JARVIS] Voice error: {e}")

# ── DRAIN BUFFER → SESSION STATE ──────────────────────────────────────────────
if _pending:
    st.session_state.messages.extend(_pending)
    _pending.clear()

# ── TOGGLE BUTTON ─────────────────────────────────────────────────────────────
if st.button("🛑 Stop Listening" if st.session_state.listening else "🎤 Start Listening"):
    if not st.session_state.listening:
        mic = sr.Microphone()
        st.session_state.stop_fn = recognizer.listen_in_background(
            mic, callback, phrase_time_limit=8
        )
        st.session_state.listening = True
        print("[JARVIS] Started listening")
        _pending.append(("Jarvis", "Jarvis online. Speak your command."))
        speak_async("Jarvis online. Speak your command.")
    else:
        if st.session_state.stop_fn:
            st.session_state.stop_fn(wait_for_stop=False)
            st.session_state.stop_fn = None
        st.session_state.listening = False
        print("[JARVIS] Stopped listening")

# ── STATUS ────────────────────────────────────────────────────────────────────
if st.session_state.listening:
    st.success("🟢 Jarvis Active — speak your command")
else:
    st.warning("🔴 Jarvis is Offline")

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
st.write("")
for sender, msg in st.session_state.messages:
    msg_html = str(msg).replace("\n", "<br>")
    st.markdown(f"""
    <div class='chat-box'>
    <b>{sender}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)

# ── POLLING LOOP ──────────────────────────────────────────────────────────────
if st.session_state.listening:
    time.sleep(1)
    st.rerun()