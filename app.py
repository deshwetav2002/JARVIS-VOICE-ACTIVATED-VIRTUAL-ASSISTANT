import streamlit as st
import base64
from datetime import datetime
import time

# ── LAZY IMPORT ───────────────────────────────────────────────────────────────
def get_process_command():
    from main import processCommand
    return processCommand

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="JARVIS AI", page_icon="🤖", layout="wide")

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# ── BACKGROUND IMAGE ──────────────────────────────────────────────────────────
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

img = get_base64("background.jpg")
bg_style = f'url("data:image/jpg;base64,{img}")' if img else "none"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{
    background-image:
    linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
    {bg_style};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-color: #0a0a1a;
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
/* Style the text input */
.stTextInput > div > div > input {{
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(0,245,255,0.4) !important;
    border-radius: 15px !important;
    color: white !important;
    font-size: 18px !important;
    padding: 15px 20px !important;
    caret-color: #00F5FF;
}}
.stTextInput > div > div > input::placeholder {{
    color: rgba(255,255,255,0.4) !important;
}}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 JARVIS")
    st.success("System Online")
    st.write("✔ Text Command Interface")
    st.write("✔ AI Integrated")
    st.write("✔ Music System")
    st.write("✔ News System")
    st.divider()
    st.caption("💡 **Example commands:**")
    st.caption("• open google")
    st.caption("• play shape of you")
    st.caption("• news")
    st.caption("• what is quantum computing?")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ── MAIN UI ───────────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>JARVIS</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>AI Powered Virtual Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='orb'></div>", unsafe_allow_html=True)
current_time = datetime.now().strftime("%I:%M:%S %p")
st.markdown(f"<h2 style='text-align:center;color:white;'>🕒 {current_time}</h2>", unsafe_allow_html=True)
st.write("")
st.write("")

# ── TEXT INPUT COMMAND BAR ────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        label="command",
        placeholder="Type your command here… (e.g. 'open google', 'news', 'play song')",
        label_visibility="collapsed",
        key="cmd_input"
    )
with col2:
    send_clicked = st.button("⚡ Send")

# ── PROCESS COMMAND ───────────────────────────────────────────────────────────
if (send_clicked or (user_input and user_input != st.session_state.get("_last_cmd", ""))) and user_input.strip():
    st.session_state["_last_cmd"] = user_input
    st.session_state.messages.append(("You", user_input.strip()))
    with st.spinner("Jarvis is thinking..."):
        try:
            processCommand = get_process_command()
            response = processCommand(user_input.strip())
            st.session_state.messages.append(("Jarvis", response or "Command executed."))
        except Exception as e:
            st.session_state.messages.append(("Jarvis", f"Error: {e}"))
    st.rerun()

# ── STATUS ────────────────────────────────────────────────────────────────────
st.success("🟢 Jarvis Active — type your command above")

# ── CHAT DISPLAY ──────────────────────────────────────────────────────────────
st.write("")
st.write("")
for sender, msg in reversed(st.session_state.messages):
    msg_html = str(msg).replace("\n", "<br>")
    icon = "🧑" if sender == "You" else "🤖"
    align = "right" if sender == "You" else "left"
    color = "rgba(0,120,255,0.15)" if sender == "You" else "rgba(255,255,255,0.08)"
    border = "rgba(0,120,255,0.4)" if sender == "You" else "rgba(255,255,255,0.1)"
    st.markdown(f"""
    <div class='chat-box' style='background:{color};border-color:{border};text-align:{align};'>
    <b>{icon} {sender}:</b> {msg_html}
    </div>
    """, unsafe_allow_html=True)
