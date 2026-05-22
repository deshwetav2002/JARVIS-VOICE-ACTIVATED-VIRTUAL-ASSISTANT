import streamlit as st
import base64
from datetime import datetime
import speech_recognition as sr
import io

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "last_command"  not in st.session_state: st.session_state.last_command  = ""
if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None

# ── BACKGROUND IMAGE ──────────────────────────────────────────────────────────
def get_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

img = get_base64("background.jpg")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&display=swap');
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
    font-family: 'Orbitron', sans-serif;
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
.chat-box-user {{
    background: rgba(0,119,255,0.15);
    padding: 12px 16px;
    border-radius: 15px;
    margin-top: 10px;
    color: white;
    border: 1px solid rgba(0,150,255,0.3);
    backdrop-filter: blur(10px);
}}
.chat-box-jarvis {{
    background: rgba(0,245,255,0.08);
    padding: 12px 16px;
    border-radius: 15px;
    margin-top: 10px;
    color: #00F5FF;
    border: 1px solid rgba(0,245,255,0.2);
    backdrop-filter: blur(10px);
}}
.stButton>button {{
    width: 100%;
    height: 56px;
    border-radius: 14px;
    background: linear-gradient(90deg,#00F5FF,#0077FF);
    color: #000;
    font-size: 17px;
    font-weight: bold;
    border: none;
}}
.stTextInput > div > div > input {{
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(0,245,255,0.4) !important;
    color: white !important;
    border-radius: 10px !important;
}}
/* Style the native audio_input widget */
[data-testid="stAudioInput"] {{
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(0,245,255,0.3);
    border-radius: 14px;
    padding: 8px;
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
st.markdown(f"<h2 style='text-align:center;color:white;'>🕒 {current_time}</h2>",
            unsafe_allow_html=True)
st.write("")

# ── SPEAK via browser SpeechSynthesis ─────────────────────────────────────────
def speak_browser(text):
    safe = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
    st.markdown(f"""
    <script>
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang = 'en-IN';
        u.rate = 1.0;
        (function trySpeak() {{
            var voices = speechSynthesis.getVoices();
            var v = voices.find(x => x.lang === 'en-IN') ||
                    voices.find(x => x.lang.startsWith('en'));
            if (v) u.voice = v;
            speechSynthesis.cancel();
            speechSynthesis.speak(u);
        }})();
    </script>
    """, unsafe_allow_html=True)

# ── HANDLE COMMAND ────────────────────────────────────────────────────────────
def handle_command(text):
    text = text.strip()
    if not text or text == st.session_state.last_command:
        return
    st.session_state.last_command = text
    print(f"[CMD] {text}")
    st.session_state.messages.append(("You", text))
    try:
        response = get_process_command()(text)
        response = response or "Done, sir."
    except Exception as e:
        response = f"Error: {e}"
    st.session_state.messages.append(("Jarvis", response))
    speak_browser(response)

# ── VOICE INPUT via st.audio_input (native Streamlit, works on Cloud) ─────────
# st.audio_input is a native Streamlit widget added in v1.31.
# It records audio directly in the browser and returns raw WAV bytes.
# SpeechRecognition then transcribes the bytes server-side via Google API.
# No iframe sandbox, no component, no pyaudio needed.
st.markdown("<p style='color:rgba(255,255,255,0.6); text-align:center; font-size:14px;'>"
            "🎙️ Press the mic below to record, press stop when done</p>",
            unsafe_allow_html=True)

audio_bytes = st.audio_input("🎤 Voice Command", label_visibility="collapsed",
                              key="voice_input")

if audio_bytes is not None:
    # Use id() to detect new recording — only process each recording once
    audio_id = id(audio_bytes)
    if audio_id != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_id
        with st.spinner("🧠 Processing..."):
            try:
                recognizer = sr.Recognizer()
                wav_data = audio_bytes.read()
                audio_file = io.BytesIO(wav_data)
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                # en-IN → Indian English, understands Hindi words
                text = recognizer.recognize_google(audio, language="en-IN")
                st.success(f"Heard: {text}")
                handle_command(text)
                st.rerun()
            except sr.UnknownValueError:
                st.warning("Couldn't understand. Please try again.")
            except sr.RequestError as e:
                st.error(f"Speech service error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")

# ── TEXT INPUT ────────────────────────────────────────────────────────────────
st.markdown("<p style='color:rgba(255,255,255,0.5); text-align:center;"
            "font-size:13px; margin-top:6px;'>— or type a command —</p>",
            unsafe_allow_html=True)

col1, col2 = st.columns([5, 1])
with col1:
    typed = st.text_input("", placeholder="e.g. open google, play chupke se, latest news",
                          label_visibility="collapsed", key="typed_cmd")
with col2:
    if st.button("⚡ Send", use_container_width=True):
        if typed.strip():
            handle_command(typed.strip())
            st.rerun()

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
if st.session_state.messages:
    for sender, msg in reversed(st.session_state.messages):
        msg_html = str(msg).replace("\n", "<br>")
        css  = "chat-box-user"  if sender == "You"  else "chat-box-jarvis"
        icon = "🧑 You"         if sender == "You"  else "🤖 Jarvis"
        st.markdown(f"""
        <div class='{css}'>
            <b>{icon}:</b> {msg_html}
        </div>
        """, unsafe_allow_html=True)
