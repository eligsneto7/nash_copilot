# nash_ui.py – versão revisada (abril 2025)
# -----------------------------------------------------------
# UI Streamlit para o Nash Copilot – inclui:
# • correções gpt‑4o
# • barra lateral compacta
# • contraste melhorado no modo Cyberpunk
# • prevenção de mensagens duplicadas
# -----------------------------------------------------------

import streamlit as st
import requests, time, random, re, html
from datetime import datetime, timedelta

# ---------------- Config -----------------
BACKEND_URL = "https://nashcopilot-production.up.railway.app"
REQUEST_TIMEOUT = (5, 65)  # (connect timeout, read timeout)

sign_panic_text = "NÃO ENTRE EM PÂNICO"
sign_42_text = "42"

# --------------- Temas CSS ---------------

CYBERPUNK_CSS = """
<style>
/* fontes e animações omitidas para brevidade */

/* --- Barra lateral compacta --- */
.stSidebar .stMarkdown,
.stSidebar .stMarkdown > *,
.stSidebar .stFileUploader,
.stSidebar .stButton,
.stSidebar .stSelectbox {
  margin-bottom: 0.35rem;
}
.sidebar-sign { margin: 8px auto; }

/* --- Contraste nas mensagens --- */
.message-nash {
  color:#e8faff; background:#16203d; border-left:3px solid #0affa070;
  display:inline-block; padding:5px 10px; border-radius:5px;
}
.message-eli {
  color:#ffe3f7; background:#3d163d; border-left:3px solid #ff07e670;
  display:inline-block; padding:5px 10px; border-radius:5px;
}
</style>
"""

LIGHT_MODE_CSS = """<style>/* light mode original aqui */</style>"""

THEMES = {
    "Cyberpunk": CYBERPUNK_CSS,
    "Light Mode": LIGHT_MODE_CSS,
}

# ------------- Session State ------------
default_session_state = {
    "clear_prompt_on_next_run": False,
    "start_time": datetime.now(),
    "nash_history": [],
    "eli_msg_count": 0,
    "nash_msg_count": 0,
    "nash_welcome": True,
    "ok": False,
    "backend_status": "VERIFICANDO...",
    "last_backend_check": datetime.min,
    "waiting_for_nash": False,
    "uploaded_file_info": None,
    "selected_theme": "Cyberpunk",
    "nash_prompt": "",
    "login_pw_input_value": "",
}
for k, v in default_session_state.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ------------- Helper funcs -------------
def check_backend_status(force=False):
    now = datetime.now()
    if not force and (now - st.session_state.last_backend_check) < timedelta(seconds=60):
        return st.session_state.backend_status
    try:
        r = requests.get(f"{BACKEND_URL}/uploads", timeout=REQUEST_TIMEOUT[0])
        status = "ONLINE ⚡" if r.status_code == 200 else f"AVISO {r.status_code}"
    except requests.exceptions.Timeout:
        status = "TIMEOUT ⏳"
    except requests.exceptions.ConnectionError:
        status = "OFFLINE "
    except Exception:
        status = "ERRO ⁉️"
    st.session_state.backend_status = status
    st.session_state.last_backend_check = now
    return status

def escape_html(text) -> str:
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text, quote=False)

# ----------- Apply Theme --------------
st.markdown(THEMES[st.session_state.selected_theme], unsafe_allow_html=True)

# ----------- Visor simplificado -------
st.markdown(f"#### Nash Copilot — Sessão iniciada às {st.session_state.start_time:%H:%M:%S}")

# ----------- Sidebar ------------------
with st.sidebar:
    st.markdown("### Aparência")
    theme_sel = st.selectbox(
        "Tema:", list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.selected_theme)
    )
    if theme_sel != st.session_state.selected_theme:
        st.session_state.selected_theme = theme_sel
        st.rerun()

    st.markdown("---")
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"<div class='sidebar-sign sign-panic'>{sign_panic_text}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sidebar-sign sign-42'>{sign_42_text}</div>", unsafe_allow_html=True)
    st.markdown("---")

# ------------- Chat input -------------
prompt = st.text_area(
    "Comando para Nash:",
    value=st.session_state.nash_prompt,
    height=110,
    key="nash_prompt"
)
send_btn = st.button("Transmitir para Nash 🚀", disabled=st.session_state.waiting_for_nash)

# ------------- Send logic -------------
if send_btn:
    if prompt.strip():
        if not (st.session_state.nash_history and st.session_state.nash_history[-1] == ("Eli", prompt)):
            st.session_state.nash_history.append(("Eli", prompt))
            st.session_state.eli_msg_count += 1
        st.session_state.waiting_for_nash = True
        st.session_state.clear_prompt_on_next_run = True
        st.rerun()
    else:
        st.warning("Comando vazio? Nem pensar!")

# ------------- Communicate backend -----
if st.session_state.waiting_for_nash:
    last_prompt = st.session_state.nash_history[-1][1] if st.session_state.nash_history else ""
    try:
        r = requests.post(f"{BACKEND_URL}/chat",
                          json={"prompt": last_prompt, "session_id": "eli"},
                          timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            resp = r.json().get("response", "Nash está mudo…")
            if not (st.session_state.nash_history and st.session_state.nash_history[-1] == ("Nash", resp)):
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
        else:
            err = r.json().get("error", r.text)
            st.session_state.nash_history.append(("Nash", f"[Erro {r.status_code}: {err}]"))
            st.error(f"Nash retornou status {r.status_code}.")
    except Exception as e:
        st.session_state.nash_history.append(("Nash", f"[Erro: {e}]"))
        st.error(f"Falha ao contactar Nash: {e}")
    finally:
        st.session_state.waiting_for_nash = False

# ------------- Render history ----------
if st.session_state.nash_history:
    st.markdown("### Log da Sessão")
    for who, msg in st.session_state.nash_history:
        class_name = "message-nash" if who == "Nash" else "message-eli"
        st.markdown(f"<span class='{class_name}'><b>{who}:</b> {escape_html(msg)}</span>", unsafe_allow_html=True)
