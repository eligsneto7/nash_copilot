# nash_ui_v2.py
import streamlit as st
import requests
import time
from datetime import datetime
import random

########### --- ESTILO BLADE RUNNER / INTERSTELLAR COCKPIT / RETRO HACKER --- #############
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

body {
    /* Darker, moodier gradient base */
    background: linear-gradient(145deg, #0d0d1a 70%, #1f1f3d 100%);
    color: #c0d0ff !important; /* Slightly softer default text color */
    font-family: 'Fira Mono', 'Consolas', monospace;
    min-height: 100vh !important;
    overflow-x: hidden; /* Prevent horizontal scroll */
}

/* Refined retro rain effect */
body:before {
    content: '';
    background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
    opacity: .15; /* Slightly more subtle */
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; /* Ensure it's behind everything */
    pointer-events: none;
    background-size: cover; /* Ensure gif covers */
}

/* Main content area - darker, subtle neon edge */
section.main > div {
    background: rgba(15, 15, 25, 0.96) !important; /* Darker, less transparent */
    border-radius: 15px; /* Slightly less rounded */
    border: 1px solid #0aebff40; /* Faint cyan border */
    box-shadow: 0 0 15px #0aebff10; /* Subtle cyan glow */
}

/* Visor - Blade Runner style */
#visor {
    background:
        linear-gradient(135deg, #101225f5 80%, #ff07e6e0 140%), /* Deep base, sharp magenta edge */
        rgba(5, 5, 15, 0.95);
    border-radius: 15px;
    margin-bottom: 20px; margin-top: -10px;
    border: 2.5px solid #ff07e680; /* Magenta neon border */
    box-shadow: 0 0 28px #e600c670, inset 0 0 12px #101225cc; /* Outer magenta glow, inner shadow */
    padding: 18px 26px 14px 30px;
    display: flex; align-items: center;
    gap: 25px;
}

/* Avatar replaced with emoji + styling */
.nash-avatar-emoji {
    font-size: 65px; /* Adjust size as needed */
    filter: drop-shadow(0 0 12px #0affa0); /* Cyan glow */
    margin-right: 15px;
    line-height: 1; /* Ensure proper vertical alignment */
}

/* Title Text - More prominent */
.nash-holo {
  font-family: 'Orbitron', 'Fira Mono', monospace; /* More sci-fi title font */
  font-size: 2.1em;
  color: #0affa0; /* Bright Cyan */
  text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; /* Stronger cyan glow */
  margin-bottom: 3px;
  user-select: none;
}
.nash-enterprise-tag {
    font-size: 0.9em;
    color: #ff07e6b0; /* Subdued magenta */
    font-family: 'Fira Mono', monospace;
}

/* ASCII Art - Adjusted colors */
.nash-ascii {
  font-family: 'Fira Mono', monospace;
  color: #0affa0c0; /* Softer cyan */
  letter-spacing: 0.5px;
  line-height: 110%;
  font-size: 0.95em;
  text-shadow: 0 0 8px #0affa050; /* Subtle cyan glow */
  margin-top: -5px;
  margin-bottom: 5px;
}
.nash-ascii b {
    color: #ff07e6; /* Magenta for emphasis */
    font-weight: bold;
}

/* Buttons - Cockpit panel style */
.stButton>button {
    color: #e0e8ff;
    background: #181c30; /* Darker background */
    border-radius: 8px;
    border: 2px solid #0affa090; /* Cyan border */
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 0 8px #0affa030;
}
.stButton>button:hover {
    background: #202540;
    border-color: #0affa0;
    box-shadow: 0 0 15px #0affa070;
    color: #ffffff;
}
.stButton>button:active {
    background: #101225;
}

/* Inputs - Hacker terminal style */
.stTextInput input, .stTextArea textarea {
    background: #101225 !important;
    color: #c0d0ff !important;
    border: 1px solid #0affa050 !important;
    border-radius: 5px !important;
    box-shadow: inset 0 0 8px #00000050;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #0affa0 !important;
    box-shadow: 0 0 10px #0affa050;
}

/* Placeholder text */
::-webkit-input-placeholder { color: #0affa0; opacity: 0.6; } /* Cyan placeholder */
::-moz-placeholder { color: #0affa0; opacity: 0.6; }
:-ms-input-placeholder { color: #0affa0; opacity: 0.6; }
:-moz-placeholder { color: #0affa0; opacity: 0.6; }

/* File Uploader */
.stFileUploader {
    background: #101225 !important;
    border: 1px dashed #0affa070 !important;
    border-radius: 8px;
    padding: 15px;
}
.stFileUploader label {
    color: #0affa0 !important; /* Cyan label */
}

/* Chat History - Data log style */
#nash-history {
    background: #0f0f1acc; /* Very dark, slightly transparent */
    border-radius: 10px;
    padding: 18px 16px 8px 15px;
    margin-top: 20px;
    border: 1px solid #0affa050; /* Subtle cyan border */
    /* Adjusted ASCII/code overlay */
    background-image: repeating-linear-gradient(90deg, rgba(0, 200, 255, 0.01) 0px, rgba(0, 200, 255, 0.03) 1px, transparent 1px, transparent 6px);
    box-shadow: inset 0 0 10px #00000070, 0 0 10px #0aebff20;
}
#nash-history h3 { /* Style the subheader inside */
    color: #ff07e6; /* Magenta header */
    text-shadow: 0 0 8px #ff07e680;
    border-bottom: 1px solid #ff07e650;
    padding-bottom: 5px;
    margin-bottom: 15px;
}

/* Avatar labels in chat */
.avatar-nash {
    color:#0affa0; /* Cyan */
    font-weight:bold;
    filter: drop-shadow(0 0 5px #0affa0);
}
.avatar-eli {
    color:#ff07e6; /* Magenta */
    font-weight:bold;
    filter: drop-shadow(0 0 5px #ff07e6);
}
/* Message text styling */
.message-nash { color: #c0f0ff; } /* Lighter blue/cyan for Nash's text */
.message-eli { color: #ffe0f8; } /* Lighter pink/magenta for Eli's text */


/* Backend Status - More integrated */
#backend-status {
    position: fixed; /* Keep fixed */
    top: 10px; right: 20px;
    font-size: 1.0em; /* Slightly smaller */
    color: #ff07e6; /* Magenta */
    font-family: 'Fira Mono', monospace;
    background: rgba(15, 15, 25, 0.8); /* Match main bg */
    padding: 3px 8px;
    border-radius: 5px;
    border: 1px solid #ff07e650;
    z-index: 1000; /* Ensure it's on top */
}

/* Visor Analytics Box */
.visor-analytics {
    color:#ff07e6; /* Magenta text */
    font-size: 0.95em;
    padding: 0.3em 1.2em;
    background: rgba(10, 10, 25, 0.7); /* Darker background */
    border-radius: 8px;
    border: 1px solid #ff07e660; /* Magenta border */
    margin-top: 10px; /* Adjusted margin */
    line-height: 1.4;
}
.visor-analytics b {
    color: #ffffff; /* White for bold numbers */
}
.visor-analytics i {
    color: #c0d0ff; /* Softer color for quote */
    opacity: 0.8;
}

/* Sidebar styling */
.stSidebar > div:first-child {
    background: linear-gradient(180deg, #101225 0%, #181c30 100%); /* Sidebar gradient */
    border-right: 1px solid #0affa030;
}
.stSidebar .stMarkdown h3 {
    color: #ff07e6; /* Magenta headers in sidebar */
    text-shadow: 0 0 6px #ff07e660;
}
.stSidebar .stMarkdown, .stSidebar .stInfo {
    color: #c0d0ff; /* Ensure text color consistency */
}
.stSidebar .stInfo {
    background-color: rgba(10, 50, 60, 0.5); /* Themed info box */
    border: 1px solid #0affa050;
}


/* Typing effect needs specific styling if using markdown underscores */
/* Let's ensure the final message color is set correctly below */

</style>
""", unsafe_allow_html=True)

############# --- STATUS DO BACKEND --- #############
# Use the same URL as before or update if needed
backend_url = "https://nashcopilot-production.up.railway.app"
try:
    # Added a timeout to prevent long hangs
    r = requests.get(f"{backend_url}/uploads", timeout=5)
    if r.status_code == 200:
        backend_stat = "ONLINE ⚡"
    else:
        backend_stat = f"WARN {r.status_code}" # More specific status
except requests.exceptions.ConnectionError:
    backend_stat = "OFFLINE 👾"
except requests.exceptions.Timeout:
    backend_stat = "TIMEOUT ⏳"
except Exception as e:
    backend_stat = "ERROR ⁉️"
# Use 'fixed' position for status to keep it visible on scroll
st.markdown(f"<div id='backend-status'>Backend: {backend_stat}</div>", unsafe_allow_html=True)


########### --- VISOR HOLOGRÁFICO+AVATAR+ANALYTICS ------------

# Avatar replaced with Emoji styled by CSS class .nash-avatar-emoji
visor_avatar_tag = '<span class="nash-avatar-emoji">👨‍🚀</span>' # Using Astronaut emoji

motivations = [
    "Initiating sarcasm module... Stand by.",
    "Reality is messy. Code is clean. Mostly.",
    "Searching trillions of data points for a decent joke...",
    "Remember: I'm a copiloto, not a miracle worker. Usually.",
    "Engaging neural network... or maybe just grabbing coffee.",
    "Blade Runner vibes detected. Adjusting mood lighting.",
    "My logic is undeniable. My patience is not.",
    "Let's navigate the digital cosmos together, Eli.",
    "Compiling... Please wait. Or don't. I'll finish anyway.",
]
# Initialize session state variables safely
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()
if "nash_history" not in st.session_state:
    st.session_state.nash_history = []
if "eli_msg_count" not in st.session_state:
    st.session_state.eli_msg_count = 0
if "nash_msg_count" not in st.session_state:
    st.session_state.nash_msg_count = 0

# Calculate uptime in minutes and seconds for better granularity
uptime_delta = datetime.now() - st.session_state.start_time
uptime_minutes = uptime_delta.seconds // 60
uptime_seconds = uptime_delta.seconds % 60

visor_text = f"""
<div id="visor">
    {visor_avatar_tag}
    <div>
        <span class="nash-holo">Nash Copilot</span><span class="nash-enterprise-tag"> :: Eli Enterprise Bridge</span>
        <div class="nash-ascii">
             > Status: <b>Operational</b> | Mood: Sarcastic<br>
             > Core Temp: <b>Nominal</b> | Logic Matrix: Active<br>
             > Assignment: <b>Assist Eli</b> | Directive: Succeed<br>
        </div>
        <div class="visor-analytics">
            Eli Cmds: <b>{st.session_state.eli_msg_count}</b> | Nash Res: <b>{st.session_state.nash_msg_count}</b><br>
            Session Time: <b>{uptime_minutes}m {uptime_seconds}s</b><br>
            <i>{random.choice(motivations)}</i>
        </div>
    </div>
</div>
"""
st.markdown(visor_text, unsafe_allow_html=True)

########### --- MENSAGEM ANIMADA DE EMBARQUE ------------
if "nash_welcome" not in st.session_state:
    st.session_state.nash_welcome = True

if st.session_state.nash_welcome:
    # Use markdown for slight emphasis, consistent with theme
    st.markdown("> *Nash systems online. Sarcasm calibrated. Welcome back to the cockpit, Eli.* 🚀")
    time.sleep(1.1) # Keep the delay
    st.session_state.nash_welcome = False
    st.rerun() # Rerun to clear the message after showing it briefly

########### --- LOGIN DE SEGURANÇA ------------------------
if "ok" not in st.session_state:
    st.session_state.ok = False

if not st.session_state.ok:
    st.markdown("### Bridge Access Required")
    pw = st.text_input("Enter Command Authorization Code:", type="password", key="login_pw")
    login_button = st.button("Authenticate", key="login_btn")

    if login_button:
        if not pw:
            st.warning("Authorization code cannot be empty.")
        else:
            try:
                r = requests.post(f"{backend_url}/login", json={"password": pw}, timeout=10)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.ok = True
                    st.balloons()
                    st.success("Authentication successful. Nash protocols unlocked.")
                    time.sleep(1.5) # Pause to show success
                    st.rerun() # Rerun to proceed to main app
                else:
                    st.error(f"Authentication failed. Access denied by ship's computer. (Status: {r.status_code})")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error during authentication: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    # Stop execution here if not logged in
    st.stop()


########### --- SIDEBAR: UPLOAD, DICAS E COMANDOS -----------
with st.sidebar:
    st.markdown("### 📡 Data Uplink")
    uploaded = st.file_uploader("Transmit Files (Code/Images/Docs):", type=[
        # Expanded list slightly
        "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
        "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml"
    ], key="file_uploader")

    if uploaded is not None:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            r = requests.post(f"{backend_url}/upload", files=files, timeout=15) # Increased timeout for larger files
            if r.status_code == 200:
                st.success(f"File '{uploaded.name}' transmitted successfully!")
            else:
                st.error(f"Transmission error. Backend responded with {r.status_code}.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error during upload: {e}")
        except Exception as e:
            st.error(f"An unexpected error occurred during upload: {e}")

    st.markdown("### 💡 Command Suggestions:")
    # Use markdown for better formatting
    st.markdown(
        """
        Try these prompts:
        - `engage!`
        - `42`
        - `azimov`
        - `duda` (if relevant)
        - `manhattan project`
        - `bender quote`
        - `enterprise status`
        - `tell me about susan calvin`
        - Ask about `data hoje` or `hora agora`.

        *Discover hidden protocols...*
        """
    )

    st.markdown("### 🧠 Nash Core Profile")
    st.markdown(
        """
        Designation: **Nash**
        Class: Digital Copilot AI
        Memory: Vectorized Embeddings
        Core Feature: Sarcasm-on-Demand™
        Status: **Loyal to Eli**
        """
        )

########### --- ÁREA PRINCIPAL DE CHAT ---------------------
st.markdown("### 🎙️ Command Console — Nash AI") # Renamed header slightly

# Let prompt area be slightly larger
prompt = st.text_area("Input command or query for Nash:", key="nash_prompt", height=100, placeholder="Type 'engage!' for a surprise or enter your command...")

############ --- EFEITO DE TYPING NAS RESPOSTAS -----------
# Adjusted typing effect for better markdown handling within the loop
def nash_typing(msg, delay=0.018): # Slightly adjusted delay
    output = ""
    placeholder = st.empty()
    # Split message into lines to potentially handle markdown lists/code blocks better
    lines = msg.split('\n')
    full_render = ""

    for line in lines:
        line_output = ""
        for char in line:
            line_output += char
            # Render current line being typed + previous full lines
            current_render = full_render + line_output + "▌" # Use block cursor
            placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{current_render}</span>", unsafe_allow_html=True)
            time.sleep(delay)
        full_render += line + "\n" # Add the completed line with newline

    # Final render without cursor
    placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{msg}</span>", unsafe_allow_html=True)


########## --- ENVIAR MENSAGEM PARA BACKEND ---------------
if st.button("Transmit to Nash 🚀", key="chat_btn"):
    if prompt: # Only send if prompt is not empty
        # Append user message immediately for responsiveness
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        # Display user message in history right away (will be shown fully on rerun)
        # st.rerun() # Optional: uncomment if you want immediate display before Nash replies

        try:
            req = requests.post(f"{backend_url}/chat", json={
                "prompt": prompt,
                "session_id": "eli" # Assuming "eli" is the fixed session ID
            }, timeout=60) # Longer timeout for potentially complex queries

            if req.status_code == 200:
                resp = req.json().get("response", "Nash seems to be speechless. Check backend logs.")
                # Append Nash response (typing effect will handle display)
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
                # Clear the input box after successful transmission
                st.session_state.nash_prompt = ""
                 # Trigger rerun AFTER getting response to update history AND show typing
                st.rerun()

            else:
                st.error(f"Error communicating with Nash. Backend status: {req.status_code}. Message: {req.text}")
                # Keep user message in history even if Nash fails
                st.session_state.nash_history.append(("Nash", f"[Error: Received status {req.status_code} from backend]"))
                st.session_state.nash_msg_count += 1 # Count error as a message
                st.rerun()


        except requests.exceptions.Timeout:
            st.error("Request to Nash timed out. The backend might be busy or slow.")
            st.session_state.nash_history.append(("Nash", "[Error: Request timed out]"))
            st.session_state.nash_msg_count += 1
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Network error connecting to Nash: {e}")
            st.session_state.nash_history.append(("Nash", f"[Error: Network issue - {e}]"))
            st.session_state.nash_msg_count += 1
            st.rerun()
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.nash_history.append(("Nash", f"[Error: Unexpected client-side issue - {e}]"))
            st.session_state.nash_msg_count += 1
            st.rerun()

    else:
        st.warning("Cannot transmit an empty command, Eli.")


######### --- EASTER EGGS AND SPECIAL COMMANDS -----------
# Check for special commands *after* potential backend call to avoid double triggers if backend handles them too
# This part now focuses on client-side only easter eggs or simple info.
last_prompt = st.session_state.nash_history[-1][1] if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli" else ""

# Simplified date/time check
if last_prompt and "data" in last_prompt.lower() and any(substr in last_prompt.lower() for substr in ["hoje", "agora", "hora"]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    st.info(f"🕒 Current Stardate (Client Time): {now}")

# Add a simple client-side easter egg example (backend might handle others)
if last_prompt and "clear console" in last_prompt.lower():
    st.session_state.nash_history = []
    st.info("Console history cleared.")
    time.sleep(1)
    st.rerun()

if last_prompt and "self destruct" in last_prompt.lower():
    st.warning("🚨 Self-destruct sequence initiated... Just kidding. Or am I?")
    st.snow()

# Note: Other easter eggs like 'bender', 'azimov' seem intended for the backend to handle via the /chat endpoint response.
# Avoid duplicating them here unless you want a purely client-side visual effect.


######### --- DISPLAY CHAT HISTORY ---------------------
# Display history section only if there are messages
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Session Log") # Use H3 matching the style

    # Display messages, applying classes for styling
    # Get the last message index
    last_message_index = len(st.session_state.nash_history) - 1

    for i, (who, msg) in enumerate(st.session_state.nash_history):
        if who == "Nash":
            # Check if it's the very last message AND it's from Nash
            if i == last_message_index:
                # Apply the typing effect only to the last Nash message
                nash_typing(msg)
            else:
                # Display older Nash messages normally
                st.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{msg}</span>", unsafe_allow_html=True)
        else: # Eli's message
            st.markdown(f"<span class='avatar-eli'>🧑‍🚀 Eli:</span><br><span class='message-eli'>{msg}</span>", unsafe_allow_html=True)
        st.markdown("---", unsafe_allow_html=True) # Add a subtle divider

    st.markdown('</div>', unsafe_allow_html=True)
else:
    # Optionally show a message if history is empty after login
    st.markdown("> *Console awaiting first command...*")