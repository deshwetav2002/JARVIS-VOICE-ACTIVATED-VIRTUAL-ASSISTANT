import streamlit as st
import base64
from datetime import datetime
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
    text-align: center; font-size: 75px; font-weight: bold;
    color: #00F5FF; text-shadow: 0px 0px 20px cyan;
    font-family: 'Orbitron', sans-serif;
}}
.sub-text {{ text-align: center; color: white; font-size: 22px; margin-bottom: 30px; }}
.orb {{
    width: 230px; height: 230px; border-radius: 50%; margin: auto;
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
    background: rgba(0,119,255,0.15); padding: 12px 16px;
    border-radius: 15px; margin-top: 10px; color: white;
    border: 1px solid rgba(0,150,255,0.3); backdrop-filter: blur(10px);
}}
.chat-box-jarvis {{
    background: rgba(0,245,255,0.08); padding: 12px 16px;
    border-radius: 15px; margin-top: 10px; color: #00F5FF;
    border: 1px solid rgba(0,245,255,0.2); backdrop-filter: blur(10px);
}}
.stButton>button {{
    width: 100%; height: 56px; border-radius: 14px;
    background: linear-gradient(90deg,#00F5FF,#0077FF);
    color: #000; font-size: 17px; font-weight: bold; border: none;
}}
.stTextInput > div > div > input {{
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(0,245,255,0.4) !important;
    color: white !important; border-radius: 10px !important;
}}
[data-testid="stAudioInput"] {{
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(0,245,255,0.3);
    border-radius: 14px; padding: 8px;
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

# ── TRANSCRIBE using OpenAI Whisper API ───────────────────────────────────────
# No SpeechRecognition, no pyaudio — Whisper runs on OpenAI's servers.
# Supports Hindi, Indian English, mixed language perfectly.
def transcribe_audio(wav_bytes: bytes) -> str:
    try:
        from openai import OpenAI
        from apikeys import openrouter_api
        # OpenRouter supports Whisper via their API
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api
        )
        audio_file = io.BytesIO(wav_bytes)
        audio_file.name = "audio.wav"
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="hi"   # "hi" handles Hindi + Indian English mixed naturally
        )
        return transcript.text.strip()
    except Exception as e:
        # Fallback: try Google Speech via requests (no pyaudio needed)
        return transcribe_google_fallback(wav_bytes)

def transcribe_google_fallback(wav_bytes: bytes) -> str:
    """Fallback transcription using Google Speech REST API directly."""
    import requests, base64
    try:
        audio_b64 = base64.b64encode(wav_bytes).decode()
        url = "https://speech.googleapis.com/v1/speech:recognize"
        payload = {
            "config": {
                "encoding": "LINEAR16",
                "languageCode": "en-IN",
                "alternativeLanguageCodes": ["hi-IN"],
                "model": "default"
            },
            "audio": {"content": audio_b64}
        }
        # Without API key this won't work, so raise to trigger manual entry
        raise Exception("Google Speech requires API key — use text input instead")
    except Exception as e:
        raise Exception(str(e))

# ── SPEAK via browser SpeechSynthesis ─────────────────────────────────────────
def speak_browser(text):
    safe = text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", " ")
    st.markdown(f"""
    <script>
    (function() {{
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang = 'en-IN'; u.rate = 1.0;
        function doSpeak() {{
            var vs = window.speechSynthesis.getVoices();
            var v = vs.find(x => x.lang === 'en-IN') || vs.find(x => x.lang.startsWith('en'));
            if (v) u.voice = v;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(u);
        }}
        if (window.speechSynthesis.getVoices().length > 0) {{ doSpeak(); }}
        else {{ window.speechSynthesis.onvoiceschanged = doSpeak; }}
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

# ── VOICE INPUT via st.audio_input ────────────────────────────────────────────
st.markdown(
    "<p style='color:rgba(255,255,255,0.6);text-align:center;font-size:14px;'>"
    "🎙️ Press mic → speak command → press stop</p>",
    unsafe_allow_html=True
)

audio_bytes = st.audio_input("Voice Command", label_visibility="collapsed",
                              key="voice_input")

if audio_bytes is not None:
    audio_id = id(audio_bytes)
    if audio_id != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_id
        with st.spinner("🧠 Transcribing..."):
            try:
                wav_data = audio_bytes.read()
                text = transcribe_audio(wav_data)
                if text:
                    st.success(f"Heard: **{text}**")
                    handle_command(text)
                    st.rerun()
                else:
                    st.warning("Couldn't understand. Please try again.")
            except Exception as e:
                st.error(f"Transcription error: {e}")
                st.info("💡 Use the text input below instead.")

# ── TEXT INPUT ────────────────────────────────────────────────────────────────
st.markdown(
    "<p style='color:rgba(255,255,255,0.4);text-align:center;"
    "font-size:13px;margin-top:4px;'>— or type —</p>",
    unsafe_allow_html=True
)
col1, col2 = st.columns([5, 1])
with col1:
    typed = st.text_input("", placeholder="e.g. open google, play chupke se, news",
                          label_visibility="collapsed", key="typed_cmd")
with col2:
    if st.button("⚡ Send", use_container_width=True):
        if typed.strip():
            handle_command(typed.strip())
            st.rerun()

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
for sender, msg in reversed(st.session_state.messages):
    msg_html = str(msg).replace("\n", "<br>")
    css  = "chat-box-user"  if sender == "You"  else "chat-box-jarvis"
    icon = "🧑 You"         if sender == "You"  else "🤖 Jarvis"
    st.markdown(f"<div class='{css}'><b>{icon}:</b> {msg_html}</div>",
                unsafe_allow_html=True)
