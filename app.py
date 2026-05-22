import streamlit as st
import base64
from datetime import datetime

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages"     not in st.session_state: st.session_state.messages     = []
if "last_command" not in st.session_state: st.session_state.last_command = ""

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

# ── HANDLE COMMAND ────────────────────────────────────────────────────────────
def handle_command(text):
    text = text.strip()
    if not text or text == st.session_state.last_command:
        return None
    st.session_state.last_command = text
    print(f"[CMD] {text}")
    st.session_state.messages.append(("You", text))
    try:
        response = get_process_command()(text)
        response = response or "Done, sir."
    except Exception as e:
        response = f"Error: {e}"
    st.session_state.messages.append(("Jarvis", response))
    return response

# ── VOICE + SPEAK COMPONENT (pure browser — no Python TTS needed) ─────────────
# Uses Web Speech API (SpeechRecognition) for listening
# Uses SpeechSynthesis API for speaking — both built into Chrome/Edge
# No gTTS, no pyaudio, no system packages required.
# Flow: click mic → speak → silence detected → auto stops →
#       transcript sent to Streamlit → response spoken aloud by browser
import streamlit.components.v1 as components

voice_html = """
<div style="display:flex; flex-direction:column; align-items:center; gap:10px;">

  <button id="micBtn" onclick="toggleMic()" style="
    padding:14px 40px; border-radius:14px;
    background:linear-gradient(90deg,#00F5FF,#0077FF);
    color:#000; font-size:18px; font-weight:bold;
    border:none; cursor:pointer; min-width:240px;
    transition: all 0.3s;
  ">🎤 Start Listening</button>

  <p id="status" style="color:#aad4ff; font-size:14px; margin:0; text-align:center;">
    Click the button and speak your command
  </p>

</div>

<script>
var recognition = null;
var synth = window.speechSynthesis;
var listening = false;

// ── Speak using browser SpeechSynthesis (Indian English voice) ──────────────
function speakText(text) {
    synth.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    utter.lang = 'en-IN';   // Indian English accent
    utter.rate = 1.0;
    utter.pitch = 1.0;

    // Try to find an Indian English voice, fallback to default
    var voices = synth.getVoices();
    var indianVoice = voices.find(v => v.lang === 'en-IN') ||
                      voices.find(v => v.lang.startsWith('en'));
    if (indianVoice) utter.voice = indianVoice;

    synth.speak(utter);
}

// ── Toggle mic on/off ────────────────────────────────────────────────────────
function toggleMic() {
    if (listening) {
        if (recognition) recognition.stop();
        resetBtn();
    } else {
        startMic();
    }
}

function startMic() {
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        document.getElementById('status').innerText =
            'Not supported. Please use Chrome or Edge.';
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang            = 'en-IN';  // Indian English
    recognition.interimResults  = false;    // fire only when speech ends
    recognition.continuous      = false;    // auto-stop after one utterance
    recognition.maxAlternatives = 1;

    recognition.onstart = function() {
        listening = true;
        document.getElementById('micBtn').innerText = '🔴 Listening... (auto-stops)';
        document.getElementById('micBtn').style.background =
            'linear-gradient(90deg,#ff4466,#cc0033)';
        document.getElementById('micBtn').style.color = '#fff';
        document.getElementById('status').innerText = 'Speak now — stops automatically after silence';
    };

    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript.toLowerCase().trim();
        document.getElementById('status').innerText = '✅ Heard: ' + transcript;

        // Immediate audio feedback — "Ok sir" before Streamlit processes
        speakText('Ok sir');

        // Send transcript to Streamlit
        window.parent.postMessage(
            {type: 'streamlit:setComponentValue', value: transcript}, '*'
        );
    };

    recognition.onerror = function(event) {
        document.getElementById('status').innerText =
            '⚠️ Error: ' + event.error + ' — try again';
        resetBtn();
    };

    recognition.onend = function() {
        resetBtn();
    };

    recognition.start();
}

function resetBtn() {
    listening = false;
    document.getElementById('micBtn').innerText = '🎤 Start Listening';
    document.getElementById('micBtn').style.background =
        'linear-gradient(90deg,#00F5FF,#0077FF)';
    document.getElementById('micBtn').style.color = '#000';
}

// Pre-load voices (Chrome loads them async)
if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = function() { synth.getVoices(); };
}
</script>
"""

voice_result = components.html(voice_html, height=110)

# ── PROCESS VOICE RESULT ──────────────────────────────────────────────────────
if voice_result and isinstance(voice_result, str) and voice_result.strip():
    response = handle_command(voice_result.strip())
    if response:
        # Inject JS to speak the full response after Streamlit rerenders
        speak_js = f"""
        <script>
        setTimeout(function() {{
            var synth = window.speechSynthesis;
            synth.cancel();
            var utter = new SpeechSynthesisUtterance({repr(response)});
            utter.lang = 'en-IN';
            utter.rate = 1.0;
            var voices = synth.getVoices();
            var v = voices.find(v => v.lang === 'en-IN') ||
                    voices.find(v => v.lang.startsWith('en'));
            if (v) utter.voice = v;
            synth.speak(utter);
        }}, 300);
        </script>
        """
        st.markdown(speak_js, unsafe_allow_html=True)
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
for sender, msg in reversed(st.session_state.messages):
    msg_html = str(msg).replace("\n", "<br>")
    css_class = "chat-box-user" if sender == "You" else "chat-box-jarvis"
    label = "🧑 You" if sender == "You" else "🤖 Jarvis"
    st.markdown(f"""
    <div class='{css_class}'>
        <b>{label}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)
