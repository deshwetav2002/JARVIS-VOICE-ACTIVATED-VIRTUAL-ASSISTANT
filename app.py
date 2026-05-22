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
    height: 60px;
    border-radius: 15px;
    background: linear-gradient(90deg,#00F5FF,#0077FF);
    color: #000;
    font-size: 18px;
    font-weight: bold;
    border: none;
}}
.stTextInput > div > div > input {{
    background: rgba(0,0,0,0.5) !important;
    border: 1px solid rgba(0,245,255,0.4) !important;
    color: white !important;
    border-radius: 10px !important;
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

# ── SPEAK via browser SpeechSynthesis (injected into main page, not iframe) ───
def speak_js(text):
    """Inject JS into the main Streamlit page — not inside an iframe."""
    safe = text.replace("'", "\\'").replace("\n", " ")
    st.markdown(f"""
    <script>
    (function() {{
        window.speechSynthesis.cancel();
        var u = new SpeechSynthesisUtterance('{safe}');
        u.lang  = 'en-IN';
        u.rate  = 1.0;
        u.pitch = 1.0;
        var vs = window.speechSynthesis.getVoices();
        var v  = vs.find(x => x.lang === 'en-IN') || vs.find(x => x.lang.startsWith('en'));
        if (v) u.voice = v;
        window.speechSynthesis.speak(u);
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
    speak_js(response)

# ── INPUT ─────────────────────────────────────────────────────────────────────
# Web Speech API network error happens inside iframes (components.html).
# Solution: use st.text_input with a voice button that injects JS
# directly into the MAIN page (not an iframe) via st.markdown <script>.
# The transcript is written to a hidden text field and submitted.

st.markdown("""
<script>
// ── Voice recognition running in main page context (no iframe) ──────────────
var _recognition = null;
var _listening   = false;

function jarvisListen() {
    var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        alert('Please use Chrome or Edge for voice input.');
        return;
    }
    if (_listening) {
        _recognition.stop();
        return;
    }
    _recognition = new SR();
    _recognition.lang           = 'en-IN';
    _recognition.interimResults = false;
    _recognition.continuous     = false;

    _recognition.onstart = function() {
        _listening = true;
        var btn = document.getElementById('jarvis-mic-btn');
        if (btn) {
            btn.innerText = '🔴 Listening...';
            btn.style.background = 'linear-gradient(90deg,#ff4466,#cc0033)';
            btn.style.color = '#fff';
        }
    };

    _recognition.onresult = function(e) {
        var t = e.results[0][0].transcript;
        // Write into Streamlit's text input and trigger Enter
        var inputs = window.parent.document.querySelectorAll('input[type=text]');
        for (var i = 0; i < inputs.length; i++) {
            if (inputs[i].placeholder && inputs[i].placeholder.includes('Speak')) {
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(inputs[i], t);
                inputs[i].dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(function() {
                    inputs[i].dispatchEvent(
                        new KeyboardEvent('keydown', {key:'Enter', bubbles:true})
                    );
                }, 100);
                break;
            }
        }
    };

    _recognition.onerror = function(e) {
        console.log('SR error:', e.error);
        _resetBtn();
    };
    _recognition.onend = function() { _resetBtn(); };
    _recognition.start();
}

function _resetBtn() {
    _listening = false;
    var btn = document.getElementById('jarvis-mic-btn');
    if (btn) {
        btn.innerText = '🎤 Click to Speak';
        btn.style.background = 'linear-gradient(90deg,#00F5FF,#0077FF)';
        btn.style.color = '#000';
    }
}

if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
    window.speechSynthesis.onvoiceschanged = function() {
        window.speechSynthesis.getVoices();
    };
}
</script>

<div style="display:flex; justify-content:center; margin:10px 0;">
  <button id="jarvis-mic-btn" onclick="jarvisListen()" style="
    padding:14px 40px; border-radius:14px;
    background:linear-gradient(90deg,#00F5FF,#0077FF);
    color:#000; font-size:18px; font-weight:bold;
    border:none; cursor:pointer; min-width:260px; transition:all 0.3s;">
    🎤 Click to Speak
  </button>
</div>
""", unsafe_allow_html=True)

# Text input — voice result gets injected here by JS, or user types manually
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "", placeholder="Speak or type your command here...",
        label_visibility="collapsed", key="cmd_input"
    )
with col2:
    send = st.button("⚡ Send", use_container_width=True)

if (send or user_input) and user_input.strip():
    handle_command(user_input.strip())
    st.rerun()

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
for sender, msg in reversed(st.session_state.messages):
    msg_html = str(msg).replace("\n", "<br>")
    css  = "chat-box-user"   if sender == "You"    else "chat-box-jarvis"
    icon = "🧑 You"          if sender == "You"    else "🤖 Jarvis"
    st.markdown(f"""
    <div class='{css}'>
        <b>{icon}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)
