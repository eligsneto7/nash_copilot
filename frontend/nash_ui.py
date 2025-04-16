# nash_ui_v7_retro_cockpit.py
import streamlit as st
import requests
import time
from datetime import datetime
import random

# --- Textos Customizáveis para os Sinais ---
sign_panic_text = "NÃO ENTRE EM PÂNICO"
sign_42_text = "42"
# ------------------------------------------

# --- Inicialização do Sinalizador para Limpar Prompt ---
if "clear_prompt_on_next_run" not in st.session_state:
    st.session_state.clear_prompt_on_next_run = False
# ----------------------------------------------------

########### --- ESTILO V7 - RETRO COCKPIT EDITION --- #############
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;700&family=Orbitron:wght@400;500;700;900&family=Share+Tech+Mono&display=swap');

/* --- ANIMAÇÕES --- */
@keyframes scan {{
  0%, 100% {{ background-position: 0% 0%; }}
  50% {{ background-position: 100% 100%; }}
}}

@keyframes glow {{
  0%, 100% {{ text-shadow: 0 0 5px rgba(10, 255, 160, 0.7), 0 0 10px rgba(10, 255, 160, 0.5); }}
  50% {{ text-shadow: 0 0 15px rgba(10, 255, 160, 0.9), 0 0 25px rgba(10, 255, 160, 0.7); }}
}}

@keyframes blink {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.7; }}
}}

@keyframes flicker {{
  0%, 100% {{ opacity: 1; }}
  92% {{ opacity: 1; }}
  93% {{ opacity: 0.4; }}
  94% {{ opacity: 1; }}
  95% {{ opacity: 0.8; }}
  96% {{ opacity: 1; }}
  97% {{ opacity: 0.5; }}
  98% {{ opacity: 1; }}
}}

@keyframes terminal-cursor {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0; }}
}}

/* --- ESTILOS BASE --- */
body, .stApp {{
    background-color: #0a0d12 !important;
    color: #c8e3ff !important;
    font-family: 'Share Tech Mono', 'Fira Code', monospace !important;
    background-image: url('{background_url}'), 
                      linear-gradient(135deg, rgba(2,9,22,0.97) 0%, rgba(7,19,37,0.92) 100%);
    background-size: 200px auto, 100% 100%;
    background-position: center;
    background-repeat: repeat, no-repeat;
    background-attachment: fixed;
    margin: 0;
    overflow-x: hidden;
    position: relative;
}}

/* Efeito de scan-lines em toda a tela */
body::after {{
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('{scanline_url}');
    opacity: 0.03;
    pointer-events: none;
    z-index: 1000;
    animation: scan 120s linear infinite;
}}

/* Ajustes para texto padrão */
p, div, span, li {{
    color: #c8e3ff;
    text-shadow: 0 0 2px rgba(200, 227, 255, 0.5);
}}

/* Flicker e Noise Effect */
.noise-container {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: url('{noise_url}');
    opacity: 0.015;
    pointer-events: none;
    z-index: 999;
    animation: flicker 10s infinite;
}}

/* CONTAINER PRINCIPAL */
section.main > div {{
    max-width: 1200px !important;
    background: linear-gradient(170deg, rgba(12,18,30,0.95) 0%, rgba(20,30,45,0.9) 100%) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0,170,255,0.3) !important;
    box-shadow: 0 0 30px rgba(0,170,255,0.1), 
                inset 0 0 20px rgba(0,0,0,0.4) !important;
    padding: 1.5rem !important;
    margin: 0 auto !important;
    position: relative;
    z-index: 10;
}}

/* VISOR REDESENHADO - Mais destaque e altura reduzida em mobile */
#visor {{
    background: linear-gradient(135deg, #060c1df2 80%, #3e064ee0 140%);
    border-radius: 12px;
    margin-bottom: 20px;
    margin-top: -5px;
    border: 2px solid rgba(255, 7, 230, 0.5);
    box-shadow: 0 0 28px rgba(230, 0, 198, 0.3), 
                inset 0 0 15px rgba(16, 18, 37, 0.8);
    padding: clamp(15px, 4vw, 25px);
    display: flex;
    align-items: center;
    gap: clamp(15px, 3vw, 25px);
    position: relative;
    overflow: hidden;
}}

/* Efeito de highlight no visor */
#visor::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -150%;
    width: 80%;
    height: 100%;
    background: linear-gradient(90deg, 
                transparent, 
                rgba(255, 255, 255, 0.05), 
                transparent);
    transform: skewX(-25deg);
    animation: scan 8s ease-in-out infinite;
}}

/* AVATAR EMOJI - Mantido mas otimizado para mobile */
.nash-avatar-emoji {{
    font-size: clamp(45px, 10vw, 65px);
    filter: drop-shadow(0 0 12px rgba(10, 255, 160, 0.7));
    margin-right: clamp(10px, 2vw, 15px);
    line-height: 1;
    animation: glow 4s ease-in-out infinite;
}}

/* TÍTULO NASH E TAGS - Melhor responsividade */
.nash-holo, 
.nash-enterprise-tag {{
    font-family: 'Orbitron', 'Share Tech Mono', monospace;
    letter-spacing: 1px;
}}

.nash-holo {{ 
    font-size: clamp(1.6em, 5vw, 2.1em); 
    font-weight: 700;
    color: #0affa0; 
    text-shadow: 0 0 15px rgba(10, 255, 160, 0.6), 
                 0 0 5px rgba(255, 255, 255, 0.4);
    margin-bottom: 3px; 
    user-select: none;
}}

.nash-enterprise-tag {{ 
    font-size: clamp(0.7em, 3vw, 0.9em);
    color: rgba(255, 7, 230, 0.8);
    font-family: 'Share Tech Mono', monospace;
}}

/* ASCII ART - Melhor legibilidade */
.nash-ascii {{ 
    font-family: 'Fira Code', monospace;
    color: rgba(10, 255, 160, 0.8);
    letter-spacing: 0;
    line-height: 125%;
    font-size: clamp(0.75em, 2.8vw, 0.95em);
    text-shadow: 0 0 8px rgba(10, 255, 160, 0.3);
    margin-top: -2px;
    margin-bottom: 5px;
    white-space: nowrap;
}}

.nash-ascii b {{ 
    color: #ff07e6;
    font-weight: bold;
    text-shadow: 0 0 5px rgba(255, 7, 230, 0.6);
}}

/* ANALYTICS NO VISOR - Melhor legibilidade */
.visor-analytics {{
    color: #ff07e6;
    font-size: clamp(0.75em, 2.8vw, 0.95em);
    padding: 0.5em 1em;
    background: rgba(10, 10, 25, 0.8);
    border-radius: 8px;
    border: 1px solid rgba(255, 7, 230, 0.4);
    margin-top: 10px;
    line-height: 1.4;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.5);
}}

.visor-analytics b {{ 
    color: #ffffff;
    text-shadow: 0 0 3px rgba(255, 255, 255, 0.5);
}}

.visor-analytics i {{ 
    color: #c8e3ff;
    opacity: 0.9;
    font-style: italic;
}}

/* BOTÕES - Design melhorado e mais consistente */
.stButton>button {{
    color: #e0e8ff !important;
    background: linear-gradient(180deg, #1a2139 0%, #121629 100%) !important;
    border-radius: 8px !important;
    border: 2px solid rgba(10, 255, 160, 0.6) !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 8px rgba(10, 255, 160, 0.2) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    padding: 0.6em 1.2em !important;
    font-family: 'Orbitron', 'Share Tech Mono', monospace !important;
    font-size: 0.9em !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

.stButton>button:hover {{ 
    background: linear-gradient(180deg, #202540 0%, #1a2139 100%) !important;
    border-color: rgba(10, 255, 160, 0.9) !important;
    box-shadow: 0 0 15px rgba(10, 255, 160, 0.4) !important;
    color: #ffffff !important;
    transform: translateY(-2px) !important;
}}

.stButton>button:active {{ 
    background: #101225 !important;
    transform: translateY(1px) !important;
    box-shadow: 0 0 5px rgba(10, 255, 160, 0.2) !important;
}}

/* INPUT AREA - Contraste melhorado drasticamente */
.stTextArea textarea {{
    background: #0a0e1b !important;
    color: #e0f0ff !important;
    border: 1px solid rgba(10, 255, 160, 0.4) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.7) !important;
    padding: 12px !important;
    font-family: 'Share Tech Mono', 'Fira Code', monospace !important;
    font-size: 1em !important;
    line-height: 1.5 !important;
    resize: vertical !important;
    transition: all 0.3s ease !important;
}}

.stTextArea textarea:focus {{
    border-color: rgba(10, 255, 160, 0.8) !important;
    box-shadow: 0 0 10px rgba(10, 255, 160, 0.3), 
                inset 0 0 10px rgba(0, 0, 0, 0.7) !important;
    background: #0c1022 !important;
}}

/* Placeholder mais visível */
.stTextArea textarea::placeholder {{ 
    color: rgba(10, 255, 160, 0.7) !important;
    opacity: 0.7 !important;
}}

/* FILE UPLOADER - Design refinado */
.stFileUploader {{
    background: #0a0e1b !important;
    border: 1px dashed rgba(10, 255, 160, 0.5) !important;
    border-radius: 8px !important;
    padding: 15px !important;
    transition: all 0.3s ease !important;
}}

.stFileUploader:hover {{
    background: #0c1022 !important;
    border-color: rgba(10, 255, 160, 0.8) !important;
}}

.stFileUploader label {{
    color: rgba(10, 255, 160, 0.9) !important;
    font-family: 'Share Tech Mono', 'Fira Code', monospace !important;
}}

/* HISTÓRICO DE CHAT - Contraste melhorado drasticamente */
#nash-history {{
    background: rgba(8, 12, 20, 0.95);
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 20px;
    border: 1px solid rgba(10, 255, 160, 0.3);
    background-image: repeating-linear-gradient(
        90deg, 
        rgba(0, 200, 255, 0.02) 0px, 
        rgba(0, 200, 255, 0.04) 1px, 
        transparent 1px, 
        transparent 8px
    );
    box-shadow: inset 0 0 12px rgba(0, 0, 0, 0.7), 
                0 0 10px rgba(10, 235, 255, 0.1);
    position: relative;
    overflow: hidden;
}}

/* Efeito de scan no histórico */
#nash-history::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
        to bottom,
        transparent 50%,
        rgba(10, 255, 160, 0.03) 51%,
        transparent 52%
    );
    background-size: 100% 30px;
    animation: scan 10s linear infinite;
    pointer-events: none;
    z-index: 1;
}}

#nash-history h3 {{
    color: #ff07e6;
    text-shadow: 0 0 8px rgba(255, 7, 230, 0.5);
    border-bottom: 1px solid rgba(255, 7, 230, 0.4);
    padding-bottom: 8px;
    margin-bottom: 20px;
    font-family: 'Orbitron', 'Share Tech Mono', monospace;
    font-size: clamp(1.1em, 4vw, 1.3em);
    font-weight: 700;
    letter-spacing: 1px;
    position: relative;
    z-index: 2;
}}

/* AVATARES NO HISTÓRICO - Maior destaque */
.avatar-nash, .avatar-eli {{
    font-weight: bold;
    padding: 3px 8px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 5px;
    letter-spacing: 1px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}}

.avatar-nash {{ 
    color: #0affa0;
    background-color: rgba(10, 255, 160, 0.1);
    border: 1px solid rgba(10, 255, 160, 0.3);
    text-shadow: 0 0 5px rgba(10, 255, 160, 0.5);
}}

.avatar-eli {{ 
    color: #ff07e6;
    background-color: rgba(255, 7, 230, 0.1);
    border: 1px solid rgba(255, 7, 230, 0.3);
    text-shadow: 0 0 5px rgba(255, 7, 230, 0.5);
}}

/* MENSAGENS - Contraste DRASTICAMENTE melhorado */
.message-nash, .message-eli {{
    display: block;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 5px;
    margin-bottom: 15px;
    line-height: 1.5;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
    position: relative;
    white-space: pre-wrap;
    word-wrap: break-word;
}}

.message-nash {{ 
    color: #e8fff8; 
    background-color: rgba(10, 255, 160, 0.07);
    border-left: 3px solid rgba(10, 255, 160, 0.5);
}}

.message-eli {{ 
    color: #fff0fa;
    background-color: rgba(255, 7, 230, 0.07); 
    border-left: 3px solid rgba(255, 7, 230, 0.5);
}}

/* Efeito cursor em mensagens de Nash sendo digitadas */
.message-nash .cursor {{
    display: inline-block;
    width: 10px;
    height: 18px;
    background: #0affa0;
    animation: terminal-cursor 1s infinite;
    vertical-align: middle;
    margin-left: 2px;
}}

/* Divisor melhorado */
#nash-history hr {{
    margin: 20px 0;
    border: none;
    height: 1px;
    background: linear-gradient(
        90deg,
        rgba(10, 255, 160, 0.05),
        rgba(10, 255, 160, 0.2),
        rgba(10, 255, 160, 0.05)
    );
}}

/* STATUS DO BACKEND - Mais destaque */
#backend-status {{
    position: fixed;
    top: 10px;
    right: 20px;
    font-size: 0.9em;
    color: #ff07e6;
    font-family: 'Share Tech Mono', monospace;
    background: rgba(10, 10, 25, 0.9);
    padding: 5px 10px;
    border-radius: 5px;
    border: 1px solid rgba(255, 7, 230, 0.5);
    z-index: 1000;
    text-shadow: 0 0 5px rgba(255, 7, 230, 0.5);
    box-shadow: 0 0 10px rgba(255, 7, 230, 0.2);
}}

/* SIDEBAR - Design refinado */
.stSidebar > div:first-child {{
    background: linear-gradient(180deg, #0a0d15 0%, #131a2c 100%);
    border-right: 1px solid rgba(10, 255, 160, 0.2);
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
}}

.stSidebar .stMarkdown h3 {{
    color: #ff07e6;
    text-shadow: 0 0 6px rgba(255, 7, 230, 0.4);
    font-family: 'Orbitron', 'Share Tech Mono', monospace;
    font-size: 1.1em;
    font-weight: 700;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(255, 7, 230, 0.3);
    padding-bottom: 5px;
    margin-bottom: 15px;
}}

.stSidebar .stMarkdown {{
    color: #c8e3ff;
}}

/* SINAIS HTML NEON - Design melhorado */
.sidebar-sign {{
    font-family: 'Orbitron', 'Share Tech Mono', monospace;
    font-weight: bold;
    padding: 8px 15px;
    margin: 15px auto;
    border-radius: 8px;
    text-align: center;
    display: block;
    width: fit-content;
    background-color: rgba(0, 0, 10, 0.6);
    border: 1px solid;
    letter-spacing: 1px;
    box-shadow: inset 0 0 15px rgba(0, 0, 0, 0.6);
    position: relative;
    overflow: hidden;
}}

/* Efeito de scan lines nos sinais */
.sidebar-sign::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: repeating-linear-gradient(
        to bottom,
        transparent,
        transparent 1px,
        rgba(0, 0, 0, 0.1) 1px,
        rgba(0, 0, 0, 0.1) 2px
    );
    pointer-events: none;
}}

.sign-panic {{ 
    color: #ff07e6;
    border-color: rgba(255, 7, 230, 0.5);
    animation: blink 1.5s infinite;
    font-size: 1.1em;
    text-shadow: 0 0 10px rgba(255, 7, 230, 0.8);
}}

.sign-42 {{ 
    color: #0affa0;
    border-color: rgba(10, 255, 160, 0.5);
    text-shadow: 0 0 5px #0affa0, 0 0 12px #0affa0, 0 0 18px #0affa0;
    font-size: 1.8em;
    padding: 5px 20px;
}}

/* ALERTA E MENSAGENS */
.stAlert {{ background-color: rgba(10, 20, 40, 0.8) !important; }}
.stAlert p {{ color: #e0e8ff !important; }}
.stWarning {{ border-color: rgba(255, 200, 0, 0.5) !important; }}
.stWarning p {{ color: #ffeb99 !important; }}
.stError {{ border-color: rgba(255, 50, 50, 0.5) !important; }}
.stError p {{ color: #ffb3b3 !important; }}
.stInfo {{ border-color: rgba(0, 150, 255, 0.5) !important; }}
.stInfo p {{ color: #b3e0ff !important; }}
.stSuccess {{ border-color: rgba(10, 255, 160, 0.5) !important; }}
.stSuccess p {{ color: #ccffeb !important; }}

/* MARKDOWN MELHORADO */
blockquote {{
    border-left: 3px solid rgba(10, 255, 160, 0.5) !important;
    background-color: rgba(10, 255, 160, 0.05) !important;
    padding: 10px 15px !important;
    margin: 10px 0 !important;
    border-radius: 0 8px 8px 0 !important;
    color: #e0ffff !important;
}}

code {{
    background-color: rgba(10, 10, 25, 0.6) !important;
    color: #e0ffff !important;
    padding: 2px 5px !important;
    border-radius: 4px !important;
    font-family: 'Fira Code', monospace !important;
    border: 1px solid rgba(10, 255, 160, 0.2) !important;
}}

/* Melhorias para Mobile */
@media (max-width: 768px) {{
    #visor {{
        flex-direction: column;
        text-align: center;
        padding: 15px 10px;
    }}
    
    .nash-avatar-emoji {{
        margin-right: 0;
        margin-bottom: 10px;
    }}
    
    .nash-ascii {{
        white-space: normal;
        word-break: break-word;
    }}
    
    /* Ajustes para histórico em telas pequenas */
    #nash-history {{
        padding: 15px 10px;
    }}
    
    .message-nash, .message-eli {{
        padding: 8px 12px;
    }}
    
    /* Mais espaço no padding da página em dispositivos móveis */
    section.main > div {{
        padding: 10px !important;
    }}
    
    /* Status do backend em mobile */
    #backend-status {{
        font-size: 0.75em;
        padding: 3px 6px;
        top: 5px;
        right: 10px;
    }}
}}

/* Efeito de ruído dinâmico para o fundo */
@keyframes grain {{
    0%, 100% {{ transform: translate(0, 0); }}
    10% {{ transform: translate(-5%, -5%); }}
    20% {{ transform: translate(-10%, 5%); }}
    30% {{ transform: translate(5%, -10%); }}
    40% {{ transform: translate(-5%, 15%); }}
    50% {{ transform: translate(-10%, 5%); }}
    60% {{ transform: translate(15%, 0); }}
    70% {{ transform: translate(0, 10%); }}
    80% {{ transform: translate(-15%, 0); }}
    90% {{ transform: translate(10%, 5%); }}
}}

/* Scroll bar personalizada */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
::-webkit-scrollbar-track {{
    background: rgba(10, 13, 18, 0.8);
}}
::-webkit-scrollbar-thumb {{
    background: rgba(10, 255, 160, 0.5);
    border-radius: 4px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: rgba(10, 255, 160, 0.7);
}}

/* Headers e Text styling refinados */
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Orbitron', 'Share Tech Mono', monospace !important;
    color: #0affa0 !important;
    text-shadow: 0 0 10px rgba(10, 255, 160, 0.4) !important;
}}

/* Estilos específicos para botões nos modais do Streamlit */
.stButton.css-1kqq6q3 button {{
    background-color: rgba(10, 255, 160, 0.1) !important;
    color: #0affa0 !important;
}}

</style>

<div class="noise-container"></div>
""", unsafe_allow_html=True) # Fim do st.markdown CSS


# --- Lógica para Limpar o Prompt (mantida) ---
if st.session_state.clear_prompt_on_next_run:
    st.session_state.nash_prompt = ""
    st.session_state.clear_prompt_on_next_run = False


############# --- STATUS DO BACKEND --- #############
backend_url = "https://nashcopilot-production.up.railway.app"
try:
    r = requests.get(f"{backend_url}/uploads", timeout=5)
    if r.status_code == 200: backend_stat = "ONLINE ⚡"
    else: backend_stat = f"AVISO {r.status_code}"
except requests.exceptions.ConnectionError: backend_stat = "OFFLINE 👾"
except requests.exceptions.Timeout: backend_stat = "TIMEOUT ⏳"
except Exception as e: backend_stat = "ERRO ⁉️"
st.markdown(f"<div id='backend-status'>Backend: {backend_stat}</div>", unsafe_allow_html=True)

########### --- VISOR HOLOGRÁFICO+AVATAR+ANALYTICS ------------
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
    "Ajustando parâmetros quânticos... ou só fingindo que sei o que isso significa.",
    "Iniciando sequência de decolagem digital. Mantenha os braços dentro do terminal.",
    "Analisando dados como se o futuro da humanidade dependesse disso... e talvez dependa.",
    "Turbinas em potência máxima. Sarcasmo em níveis críticos."
]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "nash_history" not in st.session_state: st.session_state.nash_history = []
if "eli_msg_count" not in st.session_state: st.session_state.eli_msg_count = 0
if "nash_msg_count" not in st.session_state: st.session_state.nash_msg_count = 0
uptime_delta = datetime.now() - st.session_state.start_time
uptime_minutes = uptime_delta.seconds // 60
uptime_seconds = uptime_delta.seconds % 60
visor_text = f"""<div id="visor">{visor_avatar_tag}<div> <span class="nash-holo">Nash Copilot</span><span class="nash-enterprise-tag"> :: Ponte da Eli Enterprise</span> <div class="nash-ascii"> > Status: <b>Operacional</b> | Humor: Sarcástico IV<br> > Temp. Núcleo: <b>Nominal</b> | Matriz Lógica: Ativa<br> > Missão: <b>Dominar o Universo</b> | Diretriz: Sobreviver<br> </div> <div class="visor-analytics"> Cmds Eli: <b>{st.session_state.eli_msg_count}</b> | Resps Nash: <b>{st.session_state.nash_msg_count}</b><br> Tempo de Sessão: <b>{uptime_minutes}m {uptime_seconds}s</b><br> <i>{random.choice(motivations)}</i> </div></div></div>"""
st.markdown(visor_text, unsafe_allow_html=True)

########### --- MENSAGEM ANIMADA DE EMBARQUE ------------
if "nash_welcome" not in st.session_state: st.session_state.nash_welcome = True
if st.session_state.nash_welcome:
    st.markdown("> *Sistemas Nash online. Sarcasmo calibrado. Bem-vindo de volta ao cockpit, Eli.* 🚀")
    time.sleep(1.1); st.session_state.nash_welcome = False; st.rerun()

########### --- LOGIN DE SEGURANÇA ------------------------
if "ok" not in st.session_state: st.session_state.ok = False
if not st.session_state.ok:
    st.markdown("### Acesso à Ponte Requerido")
    pw = st.text_input("Insira o Código de Autorização de Comando:", type="password", key="login_pw")
    if st.button("Autenticar", key="login_btn"):
        if not pw: st.warning("O código de autorização não pode estar vazio.")
        else:
            try:
                r = requests.post(f"{backend_url}/login", json={"password": pw}, timeout=10)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.ok = True; st.balloons(); st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                    time.sleep(1.5); st.rerun()
                else: st.error(f"Falha na autenticação. Acesso negado pelo computador da nave. (Status: {r.status_code})")
            except requests.exceptions.RequestException as e: st.error(f"Erro de rede durante a autenticação: {e}")
            except Exception as e: st.error(f"Ocorreu um erro inesperado: {e}")
    st.stop()

########### --- SIDEBAR REORGANIZADA --- ###########
with st.sidebar:
    # 1. Sinais do Cockpit
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42">{sign_42_text}</div>""", unsafe_allow_html=True)

    st.markdown("---") # Divisor

    # 2. Comandos Rápidos (NOVA SEÇÃO)
    st.markdown("### 🚀 Comandos Rápidos")
    cols = st.columns(2)
    with cols[0]:
        if st.button("🔄 Reiniciar", help="Limpa o histórico de conversas"):
            st.session_state.nash_history = []
            st.rerun()
    with cols[1]:
        if st.button("⏰ Data", help="Mostra a data estelar atual"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"🕒 Data Estelar: {now}")

    # 3. Uplink de Dados
    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo",
        type=[
            "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
            "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml"
        ],
        key="file_uploader",
        label_visibility="visible"
    )
    if uploaded is not None:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            r = requests.post(f"{backend_url}/upload", files=files, timeout=15)
            if r.status_code == 200: st.success(f"Arquivo '{uploaded.name}' transmitido!")
            else: st.error(f"Erro na transmissão ({r.status_code}).")
        except requests.exceptions.RequestException as e: st.error(f"Erro de rede: {e}")
        except Exception as e: st.error(f"Erro inesperado no upload: {e}")

    st.markdown("---") # Divisor

    # 4. Perfil Nash
    st.markdown("### 🧠 Perfil Núcleo Nash")
    st.markdown(
        """
        Designação: **Nash**  
        Classe: IA Copiloto Digital  
        Memória: Vetorizada  
        Recurso: Todos™  
        Status: **Online**
        """
        )
    
    # 5. Configurações da Interface (NOVA SEÇÃO)
    st.markdown("### ⚙️ Configurações")
    theme = st.selectbox(
        "Tema da Interface",
        ["Retro Cockpit", "Futuro Minimalista", "Blade Runner"],
        index=0,
        help="Altera o tema visual da interface (em desenvolvimento)"
    )
    
    # 6. Sobre o Sistema (NOVA SEÇÃO)
    st.markdown("### ℹ️ Sobre")
    st.markdown(
        """
        **Nash Copilot v7.0**  
        *"Seu navegador no cosmos digital"*  
        © 2025 Eli Enterprise
        """
    )

########### --- ÁREA PRINCIPAL DE CHAT ---------------------
st.markdown("### 🎙️ Console de Comando — Nash AI")
prompt = st.text_area("Insira comando ou consulta para Nash:", key="nash_prompt", height=100, placeholder="Digite 'engage!' para uma surpresa ou insira seu comando...")

############ --- EFEITO DE TYPING NAS RESPOSTAS -----------
def nash_typing(msg, delay=0.018):
    output = ""; placeholder = st.empty(); lines = msg.split('\n'); full_render = ""
    for line in lines:
        line_output = ""
        for char in line:
            line_output += char; current_render = full_render + line_output + "▌"
            placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{current_render}</span>", unsafe_allow_html=True)
            time.sleep(delay)
        full_render += line + "\n"
    placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{msg}</span>", unsafe_allow_html=True)

########## --- ENVIAR MENSAGEM PARA BACKEND ---------------
if st.button("Transmitir para Nash 🚀", key="chat_btn"):
    if prompt:
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        try:
            req = requests.post(f"{backend_url}/chat", json={"prompt": prompt,"session_id": "eli"}, timeout=60)
            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras. Verifique os logs do backend.")
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
                st.session_state.clear_prompt_on_next_run = True # Sinaliza para limpar
                st.rerun()
            else:
                st.error(f"Erro ao comunicar com Nash. Status: {req.status_code}. Msg: {req.text}")
                st.session_state.nash_history.append(("Nash", f"[Erro: Status {req.status_code}]"))
                st.session_state.nash_msg_count += 1
                st.session_state.clear_prompt_on_next_run = True; st.rerun()
        except requests.exceptions.Timeout:
            st.error("Requisição para Nash expirou (timeout)."); st.session_state.nash_history.append(("Nash", "[Erro: Timeout]"))
            st.session_state.nash_msg_count += 1; st.session_state.clear_prompt_on_next_run = True; st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de rede: {e}"); st.session_state.nash_history.append(("Nash", f"[Erro: Rede]"))
            st.session_state.nash_msg_count += 1; st.session_state.clear_prompt_on_next_run = True; st.rerun()
        except Exception as e:
            st.error(f"Erro inesperado: {e}"); st.session_state.nash_history.append(("Nash", f"[Erro: Cliente]"))
            st.session_state.nash_msg_count += 1; st.session_state.clear_prompt_on_next_run = True; st.rerun()
    else: st.warning("Não posso transmitir um comando vazio, Eli.")

######### --- EASTER EGGS E COMANDOS ESPECIAIS (Lado Cliente) -----------
last_prompt = st.session_state.nash_history[-1][1] if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli" else ""
if last_prompt and "data" in last_prompt.lower() and any(substr in last_prompt.lower() for substr in ["hoje", "agora", "hora"]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"); st.info(f"🕒 Data Estelar Atual (Cliente): {now}")
if last_prompt and "limpar console" in last_prompt.lower():
    st.session_state.nash_history = []; st.info("Histórico do console limpo."); time.sleep(1); st.rerun()
if last_prompt and "auto destruir" in last_prompt.lower():
    st.warning("🚨 Sequência de auto-destrução iniciada... Brincadeirinha."); st.snow()
# Novo Easter Egg
if last_prompt and "engage" in last_prompt.lower():
    st.success("🚀 Sistemas de propulsão engajados!"); 
    st.balloons();
    time.sleep(0.5);
    st.session_state.nash_history.append(("Nash", "Turbinas em velocidade de dobra, Capitão. Esperando suas coordenadas para o salto. Destino: o infinito e além!"))
    st.session_state.nash_msg_count += 1
    st.rerun()

######### --- EXIBIR HISTÓRICO DE CHAT ---------------------
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")
    last_message_index = len(st.session_state.nash_history) - 1
    for i, (who, msg) in enumerate(st.session_state.nash_history):
        if who == "Nash":
            if i == last_message_index: nash_typing(msg)
            else: st.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{msg}</span>", unsafe_allow_html=True)
        else: st.markdown(f"<span class='avatar-eli'>🧑‍🚀 Eli:</span><br><span class='message-eli'>{msg}</span>", unsafe_allow_html=True)
        if i < last_message_index: st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
else: st.markdown("> *Console aguardando o primeiro comando...*")