import streamlit as st
import base64
from datetime import datetime
import speech_recognition as sr
from gtts import gTTS
import io
import os

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []

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

# ── gTTS SPEAK — plays audio in browser, Indian English accent ────────────────
# FIX 1 — double speak: main.py speak() is now a no-op. Only this function
#          speaks. Previously both main.py speak() AND app.py speak_async()
#          were firing for every response — that caused the double speech.
# FIX 2 — Indian accent: gTTS tld="co.in" uses Google India TTS server
#          which has a natural Indian English accent and correctly pronounces
#          Hindi song names like "chupke se" instead of mangling them.
def speak_browser(text):
    try:
        # tld="co.in" = Indian English accent, handles Hindi words naturally
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        audio_b64 = base64.b64encode(buf.read()).decode()
        # Autoplay audio tag injected into the page
        st.markdown(
            f'<audio autoplay style="display:none">'
            f'<source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">'
            f'</audio>',
            unsafe_allow_html=True
        )
    except Exception as e:
        print(f"[SPEAK] Error: {e}")

# ── HANDLE COMMAND ────────────────────────────────────────────────────────────
def handle_command(text):
    text = text.lower().strip()
    if not text:
        return
    st.session_state.messages.append(("You", text))
    try:
        processCommand = get_process_command()
        response = processCommand(text)
        if response:
            st.session_state.messages.append(("Jarvis", response))
            speak_browser(response)
    except Exception as e:
        err = f"Error: {e}"
        st.session_state.messages.append(("Jarvis", err))
        speak_browser(err)

# ── INPUT: MIC RECORDER (browser-based, works on Streamlit Cloud) ─────────────
# streamlit-mic-recorder records audio in the browser and returns wav bytes.
# No pyaudio, no system mic access needed on the server side.
try:
    from streamlit_mic_recorder import mic_recorder

    col1, col2 = st.columns([1, 1])

    with col1:
        audio = mic_recorder(
            start_prompt="🎤 Start Listening",
            stop_prompt="🛑 Stop Listening",
            just_once=True,         # returns audio once after each recording
            use_container_width=True,
            key="mic"
        )

    with col2:
        text_input = st.text_input("", placeholder="Or type a command...",
                                   label_visibility="collapsed")
        if st.button("⚡ Send", use_container_width=True):
            if text_input.strip():
                handle_command(text_input.strip())
                st.rerun()

    # Process mic audio
    if audio and audio.get("bytes"):
        with st.spinner("Processing..."):
            try:
                recognizer = sr.Recognizer()
                wav_bytes = audio["bytes"]
                audio_data = sr.AudioData(wav_bytes, audio["sample_rate"], 2)
                # Indian English recognition
                text = recognizer.recognize_google(audio_data, language="en-IN")
                handle_command(text)
                st.rerun()
            except sr.UnknownValueError:
                st.warning("Couldn't understand. Please try again.")
            except Exception as e:
                st.error(f"Recognition error: {e}")

except ImportError:
    # Fallback: text input only (if mic recorder not installed)
    st.warning("Install `streamlit-mic-recorder` for voice input.")
    text_input = st.text_input("", placeholder="Type a command...",
                               label_visibility="collapsed")
    if st.button("⚡ Send", use_container_width=True):
        if text_input.strip():
            handle_command(text_input.strip())
            st.rerun()

# ── STATUS ────────────────────────────────────────────────────────────────────
st.success("🟢 Jarvis Active — press mic to speak")

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
for sender, msg in st.session_state.messages:
    msg_html = str(msg).replace("\n", "<br>")
    st.markdown(f"""
    <div class='chat-box'>
    <b>{sender}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)
