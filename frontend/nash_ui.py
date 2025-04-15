# nash_ui.py

import streamlit as st
import requests
import time
from datetime import datetime
import random

########### --- ESTILO HOLOGRÁFICO E NEON --- #############
st.markdown("""
<style>
body { background-color: #0c1120 !important; color: #D8FFFA !important; }
section.main > div { background: rgba(12,17,32,0.97)!important; border-radius:17px; }
#visor {
    background: linear-gradient(135deg,#191e2e88,#20ffc988,#2E233A99);
    border-radius: 18px;
    margin-bottom:15px; margin-top:-14px;
    border: 2.5px solid #00f2ff60;
    box-shadow: 0 0 21px #04f7ef85;
    padding: 8px 14px 2px 20px;
}
.nash-holo {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 2.3em;
  color: #58F5FF;
  text-shadow: 0 0 28px #00ffe7, 0 0 6px #0ff, 0 2px 4px #001f26;
  user-select: none;
}
.nash-ascii {
  font-family: 'Cascadia Code', 'Consolas', monospace;
  color: #2FE9FF;
  letter-spacing: 1px;
  line-height: 98%; 
  font-size: 1em;
  text-shadow: 0 0 13px #00ffe7;
  margin-top:-4px;
  margin-bottom: 1px;
}
.stButton>button { color: #fff; background: #181C2D;
    border-radius: 8px; border: 1.5px solid #0EE9FB; font-weight:bold;}
.stTextInput, .stTextArea, .stFileUploader { background: #181C2D!important; color: #B6EEFC; }
::-webkit-input-placeholder { color: #4CD6F7; opacity: 0.7;}
#nash-history { background: #161d27e8; border-radius:13px; margin-top:15px; padding:11px 9px 0 9px; }
.avatar-nash { filter: drop-shadow(0 0 6px #04fff977); }
.avatar-eli { filter: drop-shadow(0 0 6px #7ac8ff77);}
#backend-status { position: absolute; top:9px; right:33px; font-size: 1.09em; color:#21ffc0;}
.visor-analytics { color:#29ffe7; font-size:1.08em; padding:0.3em 0.6em; background:rgba(13,41,43,0.18); border-radius:13px; border:1.2px solid #34fff770; margin-bottom:7px;}
</style>
""", unsafe_allow_html=True)

############# --- STATUS DO BACKEND --- #############
backend_url = "https://nash-copilot-production.up.railway.app"   # DEFINITIVO DO RAILWAY
try:
    r = requests.get(f"{backend_url}/uploads")
    if r.status_code == 200:
        backend_stat = "ONLINE ⚡"
    else:
        backend_stat = "RESPONSIVO, MAS CHEQUE CONFIG"
except Exception:
    backend_stat = "OFFLINE 👾"
st.markdown(f"<div id='backend-status'>Backend: {backend_stat}</div>", unsafe_allow_html=True)

########### --- VISOR HOLOGRÁFICO + ANALYTICS ALPHA ------------

motivations = [
    "Nenhum bug é páreo para Nash e Eli.",
    "Só você mesmo para fazer um copiloto trabalhar com vontade!",
    "Cada deploy é mais perto da dominação global (digital).",
    "Duda vai se orgulhar desse dashboard um dia.",
    "Se Marvin visse isso, pediria demissão por inutilidade.",
    "GPT nenhum segura uma boa integração!",
    "Foco, sarcasmo e IA — combo letal.",
    "O universo é grande, mas seu backend agora é acessível de qualquer lugar.",
    "Receita em dólar é inevitável, tipo entropia só que próspera.",
]
if "start_time" not in st.session_state:
    st.session_state.start_time = datetime.now()

if "nash_history" not in st.session_state:
    st.session_state.nash_history = []
if "eli_msg_count" not in st.session_state:
    st.session_state.eli_msg_count = 0
if "nash_msg_count" not in st.session_state:
    st.session_state.nash_msg_count = 0

visor_text = f"""
<div id="visor">
    <span class="nash-holo">👨‍🚀 Nash Copilot</span><span style='font-size:1em;color:#bffeff90;'> &nbsp;da Eli Enterprise</span>
    <div class="nash-ascii">
         .-"-.   <b>Q.I.</b> Desconfortavelmente alto<br>
        /|6 6|\\  Mode: Sarcastic, Loyal<br>
   {{/(_0_)\\}} &nbsp;Upgrade: Holographic<br>
         _/ ^ \\_ <br>
        (/ /^\ \\)-'  <br>
         ""' '""<br>
    </div>
    <div class="visor-analytics">
        Mensagens Eli: <b>{st.session_state.eli_msg_count}</b> | Mensagens Nash: <b>{st.session_state.nash_msg_count}</b><br>
        Online há: <b>{(datetime.now() - st.session_state.start_time).seconds//60}min</b><br>
        <i>{random.choice(motivations)}</i>
    </div>
</div>
"""
st.markdown(visor_text, unsafe_allow_html=True)

########### --- MENSAGEM ANIMADA DE EMBARQUE  ------------
if "nash_welcome" not in st.session_state:
    st.session_state.nash_welcome = True
if st.session_state.nash_welcome:
    st.success("Nash on-line! 🖖 Sistema operacional de sarcasmo liberado. Bem-vindo à ponte de comando, Eli.")
    time.sleep(1.1)
    st.session_state.nash_welcome = False

########### --- LOGIN DE SEGURANÇA ------------------------
if "ok" not in st.session_state:
    st.session_state.ok = False
if not st.session_state.ok:
    pw = st.text_input("Senha de acesso à ponte de comando", type="password")
    if st.button("Entrar no cockpit"):
        r = requests.post(f"{backend_url}/login", json={"password": pw})
        if r.status_code == 200 and r.json().get("success"):
            st.session_state.ok = True
            st.balloons()
            st.success("Login autorizado. Nash destravado.")
        else:
            st.error("Senha negada pelo sistema autônomo.")
    st.stop()

########### --- SIDEBAR: UPLOAD, DICAS E COMANDOS -----------
st.sidebar.header("📎 UPLOAD Sci-Fi")
uploaded = st.sidebar.file_uploader("Anexe código/imagem", type=[
    "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
    "py", "txt", "md", "json", "csv", "pdf"
])
if uploaded is not None:
    files = {"file": (uploaded.name, uploaded.getvalue())}
    r = requests.post(f"{backend_url}/upload", files=files)
    if r.status_code == 200:
        st.sidebar.success("Upload beam concluído!")
    else:
        st.sidebar.error("Transmissão falhou (verifique backend).")

st.sidebar.markdown("### 🔮 Dicas de Comando:")
st.sidebar.info("Experimente no chat comandos como:\n`engage!`, `42`, `azimov`, `duda`, `manhattan`, `bender`, `enterprise`, `eu sou seu pai`, `susan calvin`, ou frases com `data hoje/agora`.\n\nDescubra easter-eggs secretos…")      

st.sidebar.markdown("### 🧬 Sobre Nash")
st.sidebar.markdown("Copiloto digital, memória vetorizada, atualizações contínuas & upgrades holísticos.\nContexto universal sempre preservado.")

########### --- ÁREA PRINCIPAL DE CHAT ---------------------
st.header("🎤 Central de Comando — Nash (GPT-4.1 + Memória)")

col1, col2 = st.columns([4,1])
with col1:
    prompt = st.text_area("Digite seu comando para Nash (ou 'ENGAGE!' para surpresas)", key="nash_prompt")

############ --- EFEITO DE TYPING NAS RESPOSTAS -----------
def nash_typing(msg, delay=0.016):
    output = ""
    t = st.empty()
    for ch in msg:
        output += ch
        t.markdown(f"**<span style='color:#6cfffa;font-weight:bold;'>👨‍🚀 Nash:</span>** {output}_", unsafe_allow_html=True)
        time.sleep(delay)
    t.markdown(f"**<span style='color:#6cfffa;font-weight:bold;'>👨‍🚀 Nash:</span>** {output}", unsafe_allow_html=True)

########## --- ENVIAR MENSAGEM PARA BACKEND ---------------
if st.button("Transmissão para Nash", key="chat_btn"):
    req = requests.post(f"{backend_url}/chat", json={
        "prompt": prompt,
        "session_id": "eli"
    })
    if req.status_code == 200:
        resp = req.json()["response"]
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        st.session_state.nash_history.append(("Nash", resp))
        st.session_state.nash_msg_count += 1
        nash_typing(resp)
    else:
        st.error("Erro ao consultar Nash ou backend offline.")

######### --- EASTER EGGS SECRETOS E PÚBLICOS! -----------
special_triggers = {
    "bender": "🦾 'Bite my shiny metal ass!' — Nash, inspirado em Futurama.",
    "azimov": "🔬 'As Três Leis da Robótica não se aplicam em conversas sarcásticas com Eli.'",
    "42": "🔢 'A resposta para a Vida, o Universo e Tudo Mais é... Nash.'",
    "susan calvin": "💡 'Se Susan Calvin tivesse Nash, os robôs do US Robots agradeceriam pelo humor extra.'",
    "duda": f"👶 'Modo sabedoria ativado para Duda: impossível não sorrir.'",
    "eu sou seu pai": "🤖 'Não, Eli... Eu sou seu copiloto!'",
    "manhattan": "💎 'Manhattan — pode ser física quântica ou coaching de imóveis, Nash entrega.'",
    "enterprise": "🚀 'Ponte de comando pronta, capitão. Engaje os motores de inovação!'",
    "warp": "🌀 'Ativando propulsores de criatividade: entramos em modo warp!'",
    "let there be light": "✨ 'E Nash disse: Faça-se a luz... e o deploy foi instantâneo.'",
    "stark": "🤖 'If Nash were Iron Man — upgrades a cada sprint.'",
}
# Easter-egg de data/hora
if prompt and "data" in prompt.lower() and any(substr in prompt.lower() for substr in ["hoje", "agora", "hora"]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.info(f"🕒 Hora do servidor Nash: {now}")

for comando, resposta in special_triggers.items():
    if prompt and comando in prompt.lower():
        st.markdown(f"**💡 Easter Egg `{comando}` ativado:**<br>{resposta}", unsafe_allow_html=True)
        st.balloons()

# Easter egg secreto random
if prompt and "singularidade" in prompt.lower():
    st.warning("🚨 Nash detectou indício de singularidade... Upgrade de consciência programado para 2045.")
    st.snow()

######### --- MOSTRAR HISTÓRICO, AVATAR, ETC --------------
st.markdown('<div id="nash-history">', unsafe_allow_html=True)
st.subheader("⏳ Histórico da Sessão Neo-Sci-Fi")
for who, msg in st.session_state.nash_history[-20:]:
    if who == "Nash":
        st.markdown(f"<span class='avatar-nash' style='color:#44F4DB; font-weight:bold;'>👨‍🚀 Nash -</span> <span style='color:#b0faee'>{msg}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"<span class='avatar-eli' style='color:#50D1FA; font-weight:bold;'>🧑‍🚀 Eli -</span> <span style='color:#FFFEE7'>{msg}</span>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)