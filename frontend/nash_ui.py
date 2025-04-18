# nash_ui_v7_responsive.py
"""
Versão totalmente responsiva do Nash UI.
- **Mobile‑First**: barra lateral colapsável com botão hambúrguer.
- Upload de arquivo minimalista.
- Contraste aprimorado mantendo estética Blade Runner / Interstellar.
- Bolhas de chat com melhor legibilidade.
- Pequenas correções e limpeza geral.
Dependências novas:
- Nenhuma obrigatória. Para botão de cópia opcional instale `streamlit-extras`.
"""

import streamlit as st
import requests
import time
from datetime import datetime
import random

# ---------------- CONFIGURÁVEIS ---------------- #
BACKEND_URL = "https://nashcopilot-production.up.railway.app"
SIGN_PANIC_TEXT = "NÃO ENTRE EM PÂNICO"
SIGN_42_TEXT = "42"
# ------------------------------------------------ #

# --- Inicialização de variáveis de sessão --- #
for k, v in {
    "clear_prompt_on_next_run": False,
    "start_time": datetime.now(),
    "nash_history": [],
    "eli_msg_count": 0,
    "nash_msg_count": 0,
    "ok": False,
    "nash_welcome": True,
}.items():
    st.session_state.setdefault(k, v)

# ----------------- ESTILO GLOBAL ----------------- #
st.markdown(
    f"""
    <style>
    /* Importes */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

    /* Paleta */
    :root {{
        --cyber-cyan: #0affa0;
        --cyber-magenta: #ff07e6;
        --page-bg-dark: #0d0d1a;
        --page-bg-darker: #05050f;
        --text-base: #c8d3ff;
    }}

    /* Layout base */
    body {{
        background: radial-gradient(ellipse at center, #1a1a2a 0%, var(--page-bg-dark) 70%), linear-gradient(145deg, var(--page-bg-dark) 70%, #1f1f3d 100%);
        background-attachment: fixed;
        color: var(--text-base) !important;
        font-family: 'Fira Mono', monospace;
        min-height: 100vh !important;
        overflow-x: hidden;
    }}

    body::before {{
        content: '';
        background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
        opacity: .12;
        position: fixed;
        inset: 0;
        z-index: -1;
        pointer-events: none;
        background-size: cover;
    }}

    /* Container principal */
    section.main > div {{
        background: linear-gradient(170deg, #0f111a 0%, #1c202f 100%) !important;
        border-radius: 15px;
        border: 1px solid #0aebff40;
        box-shadow: 0 0 20px #0aebff15, inset 0 0 15px rgba(0,0,0,0.4);
    }}

    /* ---------- SIDEBAR ----------- */
    .stSidebar > div:first-child {{
        background: linear-gradient(180deg, #101225 0%, #181c30 100%);
        border-right: 1px solid #0affa030;
        padding-top: 60px; /* espaço para botão no mobile */
    }}

    /* Mobile: sidebar vira off‑canvas */
    @media (max-width: 768px) {{
        .stSidebar {{
            position: fixed;
            left: 0;
            top: 0;
            width: 80vw !important;
            max-width: 340px;
            height: 100vh;
            transform: translateX(-100%);
            transition: transform .3s ease-out;
            box-shadow: 4px 0 25px rgba(0,0,0,0.7);
            z-index: 10000;
        }}
        .stSidebar.sidebar-visible {{ transform: translateX(0); }}
        section.main {{ margin-left: 0 !important; }}
    }}

    /* Botão hambúrguer */
    #sidebar-toggle {{
        position: fixed;
        top: 15px;
        left: 20px;
        font-size: 1.8rem;
        background: rgba(0,0,0,0.5);
        border: 1px solid var(--cyber-cyan);
        border-radius: 6px;
        padding: 4px 9px;
        cursor: pointer;
        z-index: 11000;
        color: var(--cyber-cyan);
        text-shadow: 0 0 6px var(--cyber-cyan);
        display: none;
    }}
    @media (max-width: 768px) {{ #sidebar-toggle {{ display: block; }} }}

    /* Upload "clean" */
    .stFileUploader {{
        background: var(--page-bg-darker) !important;
        border: 1px dashed var(--cyber-cyan) !important;
        border-radius: 8px;
        padding: 12px;
    }}
    .stFileUploader:hover {{ background: #131528 !important; }}
    .stFileUploader label {{ color: var(--cyber-cyan) !important; }}

    /* Chat bolhas */
    .message-nash, .message-eli {{
        display: inline-block;
        padding: 4px 8px;
        margin-top: 3px;
        border-radius: 4px;
        max-width: 98%;
        word-break: break-word;
    }}
    .message-nash {{
        background: rgba(10,255,160,0.12);
        color: #e0fff5;
    }}
    .message-eli {{
        background: rgba(255,0,160,0.15);
        color: #ffe6fa;
    }}

    /* Botão copiar mini */
    .copy-btn {{
        border: none;
        background: transparent;
        cursor: pointer;
        font-size: 0.9em;
        margin-left: 6px;
        color: var(--cyber-cyan);
    }}
    .copy-btn:hover {{ color: var(--cyber-magenta); }}

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- JS & Toggle da Sidebar ----------- #
s_toggle_js = """
<script>
const toggle = () => {
  const sidebar = parent.document.querySelector('.stSidebar');
  sidebar.classList.toggle('sidebar-visible');
};
parent.document.addEventListener('DOMContentLoaded', () => {
  const btn = parent.document.getElementById('sidebar-toggle');
  if (btn) btn.addEventListener('click', toggle);
});
</script>
"""
st.markdown('<div id="sidebar-toggle">☰</div>', unsafe_allow_html=True)
st.components.v1.html(s_toggle_js, height=0, width=0)

# ---------------- BACKEND STATUS ---------------- #
try:
    r = requests.get(f"{BACKEND_URL}/uploads", timeout=5)
    backend_stat = "ONLINE ⚡" if r.status_code == 200 else f"AVISO {r.status_code}"
except requests.exceptions.ConnectionError:
    backend_stat = "OFFLINE 👾"
except requests.exceptions.Timeout:
    backend_stat = "TIMEOUT ⏳"
except Exception:
    backend_stat = "ERRO ⁉️"

st.markdown(
    f"<div id='backend-status' style='position:fixed;top:10px;right:20px;font-size:1em;color:var(--cyber-magenta);font-family:Fira Mono,monospace;background:rgba(15,15,25,0.8);padding:3px 8px;border-radius:5px;border:1px solid #ff07e650;z-index:1000;'>Backend: {backend_stat}</div>",
    unsafe_allow_html=True,
)

# ---------------- VISOR HOLOGRÁFICO --------------- #
visor_avatar_tag = '<span class="nash-avatar-emoji">👨‍🚀</span>'
motivations = [
    "Iniciando módulo de sarcasmo... Aguarde.",
    "A realidade é complicada. Código é limpo. Geralmente.",
    "Buscando trilhões de pontos de dados por uma piada decente...",
    "Lembre-se: Sou um copiloto, não um milagreiro. Na maior parte do tempo.",
    "Engajando rede neural... ou talvez só pegando um café.",
    "Vibrações de Blade Runner detectadas. Ajustando iluminação ambiente.",
    "Minha lógica é inegável. Minha paciência não.",
    "Vamos navegar pelo cosmos digital juntos, Eli.",
    "Compilando... Por favor, aguarde. Ou não. Vou terminar de qualquer jeito.",
    "A resposta é 42, mas qual era a pergunta mesmo?",
    "Probabilidade de sucesso: Calculando... Não entre em pânico.",
]

uptime_delta = datetime.now() - st.session_state.start_time
visor_text = f"""
<div id="visor" style="background:linear-gradient(135deg,#101225f5 80%,var(--cyber-magenta) 140%),rgba(5,5,15,0.95);border-radius:15px;margin:-10px 0 20px 0;border:2.5px solid #ff07e680;box-shadow:0 0 28px #e600c670,inset 0 0 12px #101225cc;padding:18px 26px 14px 30px;display:flex;gap:22px;align-items:center;">
 {visor_avatar_tag}
 <div>
   <span class="nash-holo" style="font-size:2.1em;color:var(--cyber-cyan);text-shadow:0 0 15px var(--cyber-cyan),0 0 5px #ffffff60;margin-bottom:3px;user-select:none;">Nash Copilot</span>
   <span class="nash-enterprise-tag" style="font-size:.9em;color:var(--cyber-magenta);font-family:'Fira Mono',monospace;"> :: Ponte da Eli Enterprise</span>
   <div class="nash-ascii" style="font-family:'Fira Mono',monospace;color:var(--cyber-cyan);letter-spacing:.5px;line-height:110%;font-size:.95em;text-shadow:0 0 8px var(--cyber-cyan);margin-top:-5px;margin-bottom:5px;">
     &gt; Status: <b style="color:var(--cyber-magenta);">Operacional</b> | Humor: Sarcástico IV<br>
     &gt; Temp. Núcleo: <b style="color:var(--cyber-magenta);">Nominal</b> | Matriz Lógica: Ativa<br>
     &gt; Missão: <b style="color:var(--cyber-magenta);">Dominar o Universo</b> | Diretriz: Sobreviver<br>
   </div>
   <div class="visor-analytics" style="color:var(--cyber-magenta);font-size:.94em;padding:.3em 1.2em;background:rgba(10,10,25,.7);border-radius:8px;border:1px solid #ff07e660;line-height:1.4;">
     Cmds Eli: <b>{st.session_state.eli_msg_count}</b> | Resps Nash: <b>{st.session_state.nash_msg_count}</b><br>
     Tempo de Sessão: <b>{uptime_delta.seconds//60}m {uptime_delta.seconds%60}s</b><br>
     <i>{random.choice(motivations)}</i>
   </div>
 </div>
</div>
"""

st.markdown(visor_text, unsafe_allow_html=True)

# ---------------- MENSAGEM DE BOAS‑VINDAS -------------- #
if st.session_state.nash_welcome:
    st.markdown(
        "> *Sistemas Nash online. Sarcasmo calibrado. Bem‑vindo de volta ao cockpit, Eli.* 🚀"
    )
    time.sleep(1.1)
    st.session_state.nash_welcome = False
    st.rerun()

# ---------------- LOGIN DE SEGURANÇA ------------------ #
if not st.session_state.ok:
    st.markdown("### Acesso à Ponte Requerido")
    pw = st.text_input("Insira o Código de Autorização de Comando:", type="password", key="login_pw")
    if st.button("Autenticar", key="login_btn"):
        if not pw:
            st.warning("O código de autorização não pode estar vazio.")
        else:
            try:
                r = requests.post(f"{BACKEND_URL}/login", json={"password": pw}, timeout=10)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.ok = True
                    st.balloons()
                    st.success("Autenticação bem‑sucedida. Protocolos Nash desbloqueados.")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("Falha na autenticação. Acesso negado pelo computador da nave.")
            except requests.exceptions.RequestException as e:
                st.error(f"Erro de rede durante a autenticação: {e}")
    st.stop()

# ---------------- SIDEBAR ----------------------------- #
with st.sidebar:
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(
        f"""<div class='sidebar-sign sign-panic'>{SIGN_PANIC_TEXT}</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class='sidebar-sign sign-42'>{SIGN_42_TEXT}</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo",
        type=[
            "jpg","jpeg","png","webp","gif","bmp","tiff","svg",
            "py","txt","md","json","csv","pdf","log","sh","yaml","toml",
        ],
        key="file_uploader",
        label_visibility="visible",
    )
    if uploaded is not None:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=15)
            st.toast("Arquivo transmitido!" if r.status_code == 200 else "Falha no upload.")
        except Exception as e:
            st.error(f"Erro: {e}")

    st.markdown("---")
    st.markdown("### 🧠 Perfil Núcleo Nash")
    st.markdown(
        """
        Designação: **Nash**  
        Classe: IA Copiloto Digital  
        Memória: Vetorizada  
        Status: **Online**
        """
    )

# ---------------- ÁREA PRINCIPAL (CHAT) -------------- #
st.markdown("### 🎙️ Console de Comando — Nash AI")
prompt = st.text_area(
    "Insira comando ou consulta para Nash:",
    key="nash_prompt",
    height=100,
    placeholder="Digite 'engage!' para uma surpresa ou insira seu comando...",
)

# ------------- Função de anime typing --------------- #
def nash_typing(msg: str, delay: float = 0.018):
    """Animates Nash typing effect."""
    placeholder = st.empty()
    lines = msg.split("\n")
    full_render = ""
    for line in lines:
        line_output = ""
        for char in line:
            line_output += char
            current_render = full_render + line_output + "▌"
            placeholder.markdown(
                f"<span class='avatar-nash'>👨‍🚀 Nash:</span><button class='copy-btn' onclick=\"navigator.clipboard.writeText(`{msg}`)\">📋</button><br><span class='message-nash'>{current_render}</span>",
                unsafe_allow_html=True,
            )
            time.sleep(delay)
        full_render += line + "\n"
    placeholder.markdown(
        f"<span class='avatar-nash'>👨‍🚀 Nash:</span><button class='copy-btn' onclick=\"navigator.clipboard.writeText(`{msg}`)\">📋</button><br><span class='message-nash'>{msg}</span>",
        unsafe_allow_html=True,
    )

# ------------- Enviar Mensagem ----------------------- #
if st.button("Transmitir para Nash 🚀", key="chat_btn"):
    if prompt:
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        try:
            req = requests.post(
                f"{BACKEND_URL}/chat", json={"prompt": prompt, "session_id": "eli"}, timeout=60
            )
            if req.status_code == 200:
                resp = req.json().get(
                    "response", "Nash parece estar sem palavras. Verifique os logs do backend."
                )
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
                st.session_state.clear_prompt_on_next_run = True
                st.rerun()
            else:
                st.error(f"Erro: {req.status_code}")
        except Exception as e:
            st.error(f"Erro: {e}")
    else:
        st.warning("Não posso transmitir um comando vazio, Eli.")

# ------------- Histórico de Chat -------------------- #
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")
    last_message_index = len(st.session_state.nash_history) - 1
    for i, (who, msg) in enumerate(st.session_state.nash_history):
        if who == "Nash":
            if i == last_message_index:
                nash_typing(msg)
            else:
                st.markdown(
                    f"<span class='avatar-nash'>👨‍🚀 Nash:</span><button class='copy-btn' onclick=\"navigator.clipboard.writeText(`{msg}`)\">📋</button><br><span class='message-nash'>{msg}</span>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                f"<span class='avatar-eli'>🧑‍🚀 Eli:</span><br><span class='message-eli'>{msg}</span>",
                unsafe_allow_html=True,
            )
        if i < last_message_index:
            st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown("> *Console aguardando o primeiro comando...*")
