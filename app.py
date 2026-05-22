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
if "last_command"  not in st.session_state: st.session_state.last_command  = ""
if "pending_cmd"   not in st.session_state: st.session_state.pending_cmd   = ""

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
st.markdown(f"<h2 style='text-align:center;color:white;'>🕒 {current_time}</h2>",
            unsafe_allow_html=True)
st.write("")

# ── SPEAK via gTTS → browser (Indian English, handles Hindi words) ─────────────
def speak_browser(text):
    try:
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        st.markdown(
            f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" '
            f'type="audio/mp3"></audio>',
            unsafe_allow_html=True
        )
    except Exception as e:
        print(f"[SPEAK] {e}")

# ── HANDLE COMMAND ────────────────────────────────────────────────────────────
def handle_command(text):
    text = text.strip()
    if not text or text == st.session_state.last_command:
        return False
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
    return True

# ── VOICE INPUT — Web Speech API (auto-stops after silence, no button needed) ─
# Uses browser's built-in SpeechRecognition via a small JS component.
# interimResults=false → only fires when speech naturally ends (silence detected)
# → user speaks → pauses → result comes back → Streamlit reruns → processed.
# sendPrompt sends the transcript as a query param which Streamlit reads.

voice_component = """
<div style="display:flex; justify-content:center; margin-bottom:10px;">
  <button id="micBtn" onclick="toggleMic()" style="
      padding: 14px 36px;
      border-radius: 14px;
      background: linear-gradient(90deg,#00F5FF,#0077FF);
      color: #000;
      font-size: 18px;
      font-weight: bold;
      border: none;
      cursor: pointer;
      min-width: 220px;
  ">🎤 Start Listening</button>
</div>
<p id="status" style="text-align:center; color:#aad4ff; font-size:14px; margin:0;">
  Click the button and speak your command
</p>

<script>
var recognition = null;
var listening = false;

function toggleMic() {
    if (listening) {
        stopMic();
    } else {
        startMic();
    }
}

function startMic() {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        document.getElementById('status').innerText = 'Speech API not supported. Use Chrome.';
        return;
    }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-IN';          // Indian English — understands Hindi words
    recognition.interimResults = false;  // only fire when speech ends naturally
    recognition.continuous = false;      // auto-stops after one utterance
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        listening = true;
        document.getElementById('micBtn').innerText = '🔴 Listening...';
        document.getElementById('micBtn').style.background = 'linear-gradient(90deg,#ff4466,#cc0033)';
        document.getElementById('status').innerText = 'Speak your command now...';
    };

    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript.toLowerCase().trim();
        document.getElementById('status').innerText = 'Heard: ' + transcript;
        // Send transcript to Streamlit via query param trick
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: transcript}, '*');
    };

    recognition.onerror = function(event) {
        document.getElementById('status').innerText = 'Error: ' + event.error + '. Try again.';
        resetBtn();
    };

    recognition.onend = function() {
        resetBtn();
    };

    recognition.start();
}

function stopMic() {
    if (recognition) recognition.stop();
    resetBtn();
}

function resetBtn() {
    listening = false;
    document.getElementById('micBtn').innerText = '🎤 Start Listening';
    document.getElementById('micBtn').style.background = 'linear-gradient(90deg,#00F5FF,#0077FF)';
}
</script>
"""

import streamlit.components.v1 as components
voice_result = components.html(voice_component, height=100)

# components.html returns the value sent via postMessage
if voice_result and isinstance(voice_result, str):
    if handle_command(voice_result):
        st.rerun()

# ── TEXT INPUT ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    typed = st.text_input("", placeholder="Or type a command...",
                          label_visibility="collapsed", key="typed_cmd")
with col2:
    if st.button("⚡ Send", use_container_width=True):
        if typed.strip():
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
