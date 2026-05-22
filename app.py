import streamlit as st
import base64
from datetime import datetime
from gtts import gTTS
import io

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages      = []
if "last_voice"    not in st.session_state: st.session_state.last_voice    = None
if "last_text_cmd" not in st.session_state: st.session_state.last_text_cmd = None

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

# ── SPEAK via gTTS → browser audio (Indian English, handles Hindi words) ──────
def speak_browser(text):
    try:
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        st.markdown(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
    except Exception as e:
        print(f"[SPEAK] {e}")

# ── HANDLE COMMAND (single place — no duplicate speak) ────────────────────────
def handle_command(text):
    text = text.strip()
    if not text:
        return
    print(f"[CMD] {text}")
    st.session_state.messages.append(("You", text))
    try:
        response = get_process_command()(text)
        response = response or "Done, sir."
    except Exception as e:
        response = f"Error: {e}"
    st.session_state.messages.append(("Jarvis", response))
    speak_browser(response)   # only called here — main.py speak() is no-op

# ── VOICE INPUT using speech_to_text (Web Speech API, runs in browser) ────────
# speech_to_text uses the browser's built-in Web Speech API — no pyaudio,
# no server mic needed. Works on Streamlit Cloud.
# language="en-IN" → Indian English, recognises Hindi words correctly.
from streamlit_mic_recorder import speech_to_text

col1, col2 = st.columns([1, 1])

with col1:
    voice_text = speech_to_text(
        start_prompt="🎤 Start Listening",
        stop_prompt="🛑 Stop",
        language="en-IN",          # Indian English — understands Hindi words
        just_once=True,            # returns text once, resets for next command
        use_container_width=True,
        key="stt"
    )

with col2:
    typed = st.text_input("", placeholder="Or type a command...",
                          label_visibility="collapsed", key="typed_cmd")
    send = st.button("⚡ Send", use_container_width=True)

# ── PROCESS VOICE RESULT ──────────────────────────────────────────────────────
# speech_to_text returns the transcribed string when done.
# We track last_voice to avoid re-processing the same result on reruns.
if voice_text and voice_text != st.session_state.last_voice:
    st.session_state.last_voice = voice_text
    handle_command(voice_text)
    st.rerun()

# ── PROCESS TEXT INPUT ────────────────────────────────────────────────────────
if send and typed.strip() and typed.strip() != st.session_state.last_text_cmd:
    st.session_state.last_text_cmd = typed.strip()
    handle_command(typed.strip())
    st.rerun()

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
for sender, msg in st.session_state.messages:
    msg_html = str(msg).replace("\n", "<br>")
    st.markdown(f"""
    <div class='chat-box'>
    <b>{sender}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)
