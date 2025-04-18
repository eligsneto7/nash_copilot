# nash_ui_v7_responsive.py
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

########### --- ESTILO V7 --- #############
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

@keyframes blink-neon {{
  0%, 100% {{ opacity: 1; text-shadow: 0 0 7px #ff07e6, 0 0 15px #ff07e6, 0 0 20px #ff07e6; }}
  50% {{ opacity: 0.7; text-shadow: 0 0 5px #ff07e6a0, 0 0 10px #ff07e6a0; }}
}}

@keyframes matrix-rain {{
  0% {{ background-position: 0% 0%; }}
  100% {{ background-position: 0% 100%; }}
}}

/* Animação de pulso para elementos interativos */
@keyframes pulse-glow {{
  0%, 100% {{ box-shadow: 0 0 8px #0affa050; }}
  50% {{ box-shadow: 0 0 15px #0affa080; }}
}}

body {{
    /* Fundo com gradiente radial aprimorado */
    background: radial-gradient(ellipse at center, #1a1a2a 0%, #0d0d1a 70%), 
                linear-gradient(145deg, #0d0d1a 70%, #1f1f3d 100%);
    background-attachment: fixed;
    color: #c8d3ff !important; 
    font-family: 'Fira Mono', 'Consolas', monospace;
    min-height: 100vh !important;
    overflow-x: hidden;
}}

body:before {{
    /* Chuva hacker com animação aprimorada */
    content: '';
    background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
    opacity: .12;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
    pointer-events: none;
    background-size: cover;
    animation: matrix-rain 120s linear infinite;
}}

/* Melhorias de responsividade */
.main .block-container {{
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-top: 2rem !important;
}}

section.main > div {{
    background: linear-gradient(170deg, #0f111a 0%, #1c202f 100%) !important;
    border-radius: 15px;
    border: 1px solid #0aebff40;
    box-shadow: 0 0 20px #0aebff15, inset 0 0 15px rgba(0,0,0,0.4);
    padding: 1.5rem !important;
}}

#visor {{
    /* Visor aprimorado com melhor contraste e responsividade */
    background: linear-gradient(135deg, #101225f5 80%, #ff07e6e0 140%),
                rgba(5, 5, 15, 0.95);
    border-radius: 15px;
    margin-bottom: 20px; margin-top: -10px;
    border: 2.5px solid #ff07e680;
    box-shadow: 0 0 28px #e600c670, inset 0 0 12px #101225cc;
    padding: 18px 20px 14px 20px;
    display: flex; 
    flex-wrap: wrap;
    align-items: center;
    gap: 15px;
}}

/* Responsividade do visor para mobile */
@media (max-width: 768px) {{
    #visor {{
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 15px;
    }}
    
    .nash-avatar-emoji {{
        margin-right: 0 !important;
        margin-bottom: 10px;
    }}
    
    .visor-analytics {{
        padding: 0.3em 0.8em !important;
        width: 100%;
    }}
}}

.nash-avatar-emoji {{
    font-size: 65px;
    filter: drop-shadow(0 0 12px #0affa0);
    margin-right: 15px;
    line-height: 1;
}}

.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b {{
    font-family: 'Orbitron', 'Fira Mono', monospace;
}}

.nash-holo {{ 
    font-size: 2.1em; 
    color: #0affa0; 
    text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; 
    margin-bottom: 3px; 
    user-select: none; 
}}

.nash-enterprise-tag {{ 
    font-size: 0.9em; 
    color: #ff07e6b0; 
    font-family: 'Fira Mono', monospace; 
}}

.nash-ascii {{ 
    font-family: 'Fira Mono', monospace; 
    color: #0affa0c0; 
    letter-spacing: 0.5px; 
    line-height: 110%; 
    font-size: 0.95em; 
    text-shadow: 0 0 8px #0affa050; 
    margin-top: -5px; 
    margin-bottom: 5px; 
}}

.nash-ascii b {{ 
    color: #ff07e6; 
    font-weight: bold; 
}}

/* Botões com efeito de pulso */
.stButton>button {{
    color: #e0e8ff; 
    background: #181c30; 
    border-radius: 8px; 
    border: 2px solid #0affa090; 
    font-weight: bold; 
    transition: all 0.3s ease; 
    animation: pulse-glow 3s infinite;
}}

.stButton>button:hover {{ 
    background: #202540; 
    border-color: #0affa0; 
    box-shadow: 0 0 20px #0affa090 !important; 
    color: #ffffff; 
    animation: none;
}}

.stButton>button:active {{ 
    background: #101225; 
    transform: scale(0.98);
}}

/* Input Area com contraste melhorado */
.stTextArea textarea {{
    background: #0c0e1a !important;  /* Mais escuro para melhor contraste */
    color: #e0e8ff !important;      /* Mais claro para melhor leitura */
    border: 1px solid #0affa050 !important;
    border-radius: 5px !important;
    box-shadow: inset 0 0 8px #00000050;
    font-family: 'Fira Mono', monospace !important;
    letter-spacing: 0.5px;
}}

.stTextArea textarea:focus {{
    border-color: #0affa0 !important;
    box-shadow: 0 0 15px #0affa070;
}}

::-webkit-input-placeholder {{ color: #0affa0; opacity: 0.6; }}
::-moz-placeholder {{ color: #0affa0; opacity: 0.6; }}
:-ms-input-placeholder {{ color: #0affa0; opacity: 0.6; }}
:-moz-placeholder {{ color: #0affa0; opacity: 0.6; }}

/* Upload area mais limpa e moderna */
.stFileUploader {{
    background: linear-gradient(135deg, #0c0e1a 0%, #101225 100%) !important; 
    border: 1px dashed #0affa070 !important; 
    border-radius: 8px; 
    padding: 12px !important;
    transition: all 0.3s ease;
}}

.stFileUploader:hover {{
    border-color: #0affa0 !important;
    box-shadow: 0 0 10px #0affa040;
}}

.stFileUploader label {{
    color: #0affa0 !important;
    font-weight: bold;
    letter-spacing: 0.5px;
}}

/* Upload button styling */
.stFileUploader button {{
    background: linear-gradient(135deg, #101225 0%, #181c30 100%) !important;
    color: #0affa0 !important;
    border: 1px solid #0affa060 !important;
    border-radius: 6px !important;
    transition: all 0.3s ease;
}}

.stFileUploader button:hover {{
    background: linear-gradient(135deg, #181c30 0%, #202540 100%) !important;
    border-color: #0affa0 !important;
    box-shadow: 0 0 10px #0affa050;
}}

/* Chat History com melhor contraste */
#nash-history {{
    background: #0a0c13e6; 
    border-radius: 10px;
    padding: 18px 16px 8px 15px;
    margin-top: 20px;
    border: 1px solid #0affa050;
    background-image: repeating-linear-gradient(90deg, rgba(0, 200, 255, 0.01) 0px, rgba(0, 200, 255, 0.02) 1px, transparent 1px, transparent 8px);
    box-shadow: inset 0 0 12px #00000090, 0 0 10px #0aebff15;
}}

#nash-history h3 {{
    color: #ff07e6; 
    text-shadow: 0 0 8px #ff07e680; 
    border-bottom: 1px solid #ff07e650; 
    padding-bottom: 5px; 
    margin-bottom: 15px;
}}

.avatar-nash, .avatar-eli {{
    font-weight: bold; 
    filter: drop-shadow(0 0 5px);
    display: block;
    margin-bottom: 5px;
}}

.avatar-nash {{ 
    color: #0affa0; 
}}

.avatar-eli {{ 
    color: #ff07e6; 
}}

/* Mensagens com fundo contrastante para melhor legibilidade */
.message-container {{
    padding: 10px;
    margin-bottom: 15px;
    border-radius: 8px;
}}

.message-nash-container {{
    background-color: rgba(10, 17, 30, 0.7);
    border-left: 3px solid #0affa080;
}}

.message-eli-container {{
    background-color: rgba(20, 10, 30, 0.7);
    border-left: 3px solid #ff07e680;
}}

.message-nash, .message-eli {{
    display: block;
    padding: 5px 8px;
    border-radius: 5px;
    line-height: 1.5;
}}

.message-nash {{ 
    color: #e8ffff !important; /* Cyan mais claro para melhor legibilidade */
    text-shadow: 0 0 2px #0affa030;
}}

.message-eli {{ 
    color: #ffe8f8 !important; /* Rosa mais claro para melhor legibilidade */
    text-shadow: 0 0 2px #ff07e630;
}}

#nash-history hr {{
    margin: 12px 0; 
    border: none; 
    border-top: 1px solid #ffffff1a;
}}

/* Status do backend melhorado */
#backend-status {{
    position: fixed; 
    top: 10px; 
    right: 20px; 
    font-size: 1.0em; 
    color: #ff07e6; 
    font-family: 'Fira Mono', monospace; 
    background: rgba(10, 10, 20, 0.85); 
    padding: 5px 10px; 
    border-radius: 8px; 
    border: 1px solid #ff07e650; 
    z-index: 1000;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}}

/* Ajuste para mobile */
@media (max-width: 768px) {{
    #backend-status {{
        top: 5px;
        right: 5px;
        font-size: 0.85em;
        padding: 3px 6px;
    }}
}}

.visor-analytics {{
    color: #ff07e6; 
    font-size: 0.95em; 
    padding: 0.3em 1.2em; 
    background: rgba(10, 10, 25, 0.8); 
    border-radius: 8px; 
    border: 1px solid #ff07e660; 
    margin-top: 10px; 
    line-height: 1.4;
}}

.visor-analytics b {{ 
    color: #ffffff; 
}}

.visor-analytics i {{ 
    color: #e0e8ff; 
    opacity: 0.9; 
}}

/* Sidebar styling aprimorado para mobile */
.stSidebar > div:first-child {{
    background: linear-gradient(180deg, #101225 0%, #181c30 100%); 
    border-right: 1px solid #0affa030;
}}

.stSidebar .stMarkdown h3 {{
    color: #ff07e6; 
    text-shadow: 0 0 6px #ff07e660;
    margin-top: 1.5em;
}}

.stSidebar .stMarkdown {{
    color: #e0e8ff;
}}

/* Mobile sidebar toggle improvement */
@media (max-width: 768px) {{
    button[kind="header"] {{
        background-color: #ff07e6 !important;
        border-color: #ff07e680 !important;
    }}
    
    .stSidebar {{
        width: 80vw !important;
        min-width: 0 !important;
    }}
}}

/* Sinais HTML Neon aprimorados */
.sidebar-sign {{
    font-family: 'Orbitron', 'Fira Mono', monospace; 
    font-weight: bold; 
    padding: 8px 15px; 
    margin: 15px auto; 
    border-radius: 5px; 
    text-align: center; 
    display: block; 
    width: fit-content; 
    background-color: rgba(0, 0, 10, 0.4); 
    border: 1px solid; 
    letter-spacing: 1px; 
    box-shadow: inset 0 0 8px rgba(0,0,0,0.5);
}}

.sign-panic {{ 
    color: #ff07e6; 
    border-color: #ff07e680; 
    animation: blink-neon 1.5s infinite; 
    font-size: 1.1em; 
}}

.sign-42 {{ 
    color: #0affa0; 
    border-color: #0affa080; 
    text-shadow: 0 0 5px #0affa0, 0 0 12px #0affa0, 0 0 18px #0affa0; 
    font-size: 1.8em; 
    padding: 5px 20px; 
}}

/* Nova funcionalidade: Botão de Tema */
.theme-toggle {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: rgba(10, 10, 25, 0.8);
    border: 1px solid #0affa060;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
    transition: all 0.3s ease;
}}

.theme-toggle:hover {{
    border-color: #0affa0;
    box-shadow: 0 0 20px #0affa080;
}}

/* Loading indicator */
.loader {{
    width: 100%;
    height: 4px;
    background: linear-gradient(90deg, #0affa0, #ff07e6);
    background-size: 200% 100%;
    animation: gradient-shift 2s infinite linear;
    margin: 10px 0;
    border-radius: 2px;
}}

@keyframes gradient-shift {{
    0% {{ background-position: 0% 50%; }}
    100% {{ background-position: 100% 50%; }}
}}

/* Nova feature: Notificações */
.notification {{
    position: fixed;
    top: 60px;
    right: 20px;
    background: rgba(10, 10, 25, 0.9);
    border-left: 3px solid #0affa0;
    padding: 10px 15px;
    border-radius: 5px;
    color: #e0e8ff;
    z-index: 1001;
    box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
    transform: translateX(120%);
    transition: transform 0.3s ease;
    max-width: 300px;
}}

.notification.show {{
    transform: translateX(0);
}}

.notification.error {{
    border-left-color: #ff3860;
}}

.notification.success {{
    border-left-color: #0affa0;
}}

/* Nova feature: Área de ajuda rápida */
.quick-help {{
    margin-top: 20px;
    background: rgba(10, 10, 25, 0.5);
    border-radius: 8px;
    padding: 10px;
    border: 1px solid #0affa040;
}}

.quick-help h4 {{
    color: #0affa0;
    margin-bottom: 10px;
}}

.command-chip {{
    display: inline-block;
    background: rgba(10, 255, 160, 0.1);
    border: 1px solid #0affa060;
    border-radius: 15px;
    padding: 3px 10px;
    margin: 3px;
    cursor: pointer;
    transition: all 0.2s ease;
}}

.command-chip:hover {{
    background: rgba(10, 255, 160, 0.2);
    border-color: #0affa0;
    box-shadow: 0 0 10px #0affa050;
}}

</style>

<!-- Template para notificações -->
<div id="notification-template" class="notification">
    <span id="notification-message">Mensagem</span>
</div>

<!-- Botão de tema flutuante -->
<div class="theme-toggle" onclick="toggleTheme()" title="Alternar tema">
    🔄
</div>

<script>
// Função para mostrar notificações
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification-template').cloneNode(true);
    notification.id = 'active-notification';
    notification.querySelector('#notification-message').innerText = message;
    
    if (type === 'error') {
        notification.classList.add('error');
    } else {
        notification.classList.add('success');
    }
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// Alternância de tema (nova funcionalidade)
let currentTheme = 'dark';
function toggleTheme() {
    if (currentTheme === 'dark') {
        document.body.style.setProperty('--main-bg', '#15172c');
        document.body.style.setProperty('--accent-color', '#ff07e6');
        currentTheme = 'light';
        showNotification('Tema Interstellar ativado!');
    } else {
        document.body.style.setProperty('--main-bg', '#0d0d1a');
        document.body.style.setProperty('--accent-color', '#0affa0');
        currentTheme = 'dark';
        showNotification('Tema Blade Runner ativado!');
    }
}

// Copiar comando para área de input
function copyCommand(cmd) {
    const textarea = document.querySelector('.stTextArea textarea');
    if (textarea) {
        textarea.value = cmd;
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        showNotification('Comando inserido!');
    }
}

// Inicializar após carregar documento
document.addEventListener('DOMContentLoaded', function() {
    // Adicionar ouvintes de evento aos chips de comando
    document.querySelectorAll('.command-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            copyCommand(this.getAttribute('data-cmd'));
        });
    });
});
</script>
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
    "Sistemas de navegação ativados. Destino: qualquer lugar menos o escritório.",
    "Você tá me escutando? Ou só olhando pras luzes piscando?",
    "Detectando café no sistema. Processamento otimizado: +15%"
]

# Inicialização de variáveis de estado
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "nash_history" not in st.session_state: st.session_state.nash_history = []
if "eli_msg_count" not in st.session_state: st.session_state.eli_msg_count = 0
if "nash_msg_count" not in st.session_state: st.session_state.nash_msg_count = 0
if "theme" not in st.session_state: st.session_state.theme = "blade_runner"

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
    col1, col2 = st.columns([3, 1])
    with col1:
        pw = st.text_input("Insira o Código de Autorização de Comando:", type="password", key="login_pw")
    with col2:
        login_btn = st.button("Autenticar", key="login_btn", use_container_width=True)
    
    if login_btn:
        if not pw: 
            st.warning("O código de autorização não pode estar vazio.")
        else:
            # Mostrar animação de carregamento
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            try:
                r = requests.post(f"{backend_url}/login", json={"password": pw}, timeout=10)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.ok = True
                    st.balloons()
                    st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                    time.sleep(1.5)
                    st.rerun()
                else: 
                    st.error(f"Falha na autenticação. Acesso negado pelo computador da nave. (Status: {r.status_code})")
            except requests.exceptions.RequestException as e: 
                st.error(f"Erro de rede durante a autenticação: {e}")
            except Exception as e: 
                st.error(f"Ocorreu um erro inesperado: {e}")
    st.stop()

########### --- SIDEBAR REORGANIZADA PARA MOBILE --- ###########
with st.sidebar:
    # 1. Sinais do Cockpit (Primeiro item)
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42">{sign_42_text}</div>""", unsafe_allow_html=True)

    st.markdown("---") # Divisor

    # 2. Uplink de Dados (Redesenhado para ser mais limpo)
    st.markdown("### 📡 Uplink de Dados")
    # Upload container redesenhado para ser mais clean
    uploaded = st.file_uploader(
        "Enviar arquivo para Nash",
        type=[
            "jpg", "jpeg", "png", "webp", "gif", "bmp", "svg",
            "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml"
        ],
        key="file_uploader",
        label_visibility="collapsed" # Ocultamos o rótulo para um visual mais limpo
    )
    
    # Texto de ajuda simplificado abaixo do uploader
    st.caption("Arraste arquivos ou clique para enviar ao Nash.")
    
    if uploaded is not None:
        # Mostrar animação de carregamento
        st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            r = requests.post(f"{backend_url}/upload", files=files, timeout=15)
            if r.status_code == 200: 
                st.success(f"'{uploaded.name}' transmitido!")
            else: 
                st.error(f"Erro na transmissão ({r.status_code}).")
        except requests.exceptions.RequestException as e: 
            st.error(f"Erro de rede: {e}")
        except Exception as e: 
            st.error(f"Erro inesperado no upload: {e}")

    st.markdown("---") # Divisor

    # 3. Perfil Nash 
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
    
    # 4. NOVA SEÇÃO: Comandos Rápidos
    st.markdown("### 💬 Comandos Rápidos")
    st.markdown(
        """
        <div class="quick-help">
            <h4>Comandos Úteis:</h4>
            <div class="command-chip" data-cmd="data estelar">data estelar</div>
            <div class="command-chip" data-cmd="limpar console">limpar console</div>
            <div class="command-chip" data-cmd="status do sistema">status do sistema</div>
            <div class="command-chip" data-cmd="engage!">engage!</div>
        </div>
        """, 
        unsafe_allow_html=True
    )

########### --- ÁREA PRINCIPAL DE CHAT ---------------------
st.markdown("### 🎙️ Console de Comando — Nash AI")

# Layout em colunas para o campo de entrada e botão
col1, col2 = st.columns([4, 1])
with col1:
    prompt = st.text_area(
        "Insira comando ou consulta para Nash:", 
        key="nash_prompt", 
        height=100, 
        placeholder="Digite 'engage!' para uma surpresa ou insira seu comando..."
    )
with col2:
    # Botão centralizado verticalmente
    st.markdown("<br>", unsafe_allow_html=True)
    chat_btn = st.button("Transmitir 🚀", key="chat_btn", use_container_width=True)

############ --- EFEITO DE TYPING APRIMORADO NAS RESPOSTAS -----------
def nash_typing(msg, delay=0.018):
    output = ""
    placeholder = st.empty()
    lines = msg.split('\n')
    full_render = ""
    
    # HTML para container de mensagem aprimorado
    container_start = '<div class="message-container message-nash-container">'
    container_end = '</div>'
    
    for line in lines:
        line_output = ""
        for char in line:
            line_output += char
            current_render = full_render + line_output + "▌"
            placeholder.markdown(
                f'<span class="avatar-nash">👨‍🚀 Nash:</span>{container_start}<span class="message-nash">{current_render}</span>{container_end}', 
                unsafe_allow_html=True
            )
            time.sleep(delay)
        full_render += line + "\n"
    
    placeholder.markdown(
        f'<span class="avatar-nash">👨‍🚀 Nash:</span>{container_start}<span class="message-nash">{msg}</span>{container_end}', 
        unsafe_allow_html=True
    )

########## --- ENVIAR MENSAGEM PARA BACKEND ---------------
if chat_btn:
    if prompt:
        # Adicionar mensagem ao histórico
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        
        # Mostrar animação de carregamento
        st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
        
        try:
            req = requests.post(
                f"{backend_url}/chat", 
                json={"prompt": prompt, "session_id": "eli"}, 
                timeout=60
            )
            
            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras. Verifique os logs do backend.")
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
                st.session_state.clear_prompt_on_next_run = True
                st.rerun()
            else:
                st.error(f"Erro ao comunicar com Nash. Status: {req.status_code}. Msg: {req.text}")
                st.session_state.nash_history.append(("Nash", f"[Erro: Status {req.status_code}]"))
                st.session_state.nash_msg_count += 1
                st.session_state.clear_prompt_on_next_run = True
                st.rerun()
        except requests.exceptions.Timeout:
            st.error("Requisição para Nash expirou (timeout).")
            st.session_state.nash_history.append(("Nash", "[Erro: Timeout]"))
            st.session_state.nash_msg_count += 1
            st.session_state.clear_prompt_on_next_run = True
            st.rerun()
        except requests.exceptions.RequestException as e:
            st.error(f"Erro de rede: {e}")
            st.session_state.nash_history.append(("Nash", f"[Erro: Rede]"))
            st.session_state.nash_msg_count += 1
            st.session_state.clear_prompt_on_next_run = True
            st.rerun()
        except Exception as e:
            st.error(f"Erro inesperado: {e}")
            st.session_state.nash_history.append(("Nash", f"[Erro: Cliente]"))
            st.session_state.nash_msg_count += 1
            st.session_state.clear_prompt_on_next_run = True
            st.rerun()
    else: 
        st.warning("Não posso transmitir um comando vazio, Eli.")

######### --- EASTER EGGS E COMANDOS ESPECIAIS (Lado Cliente) -----------
last_prompt = st.session_state.nash_history[-1][1] if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli" else ""

# Comando de data/hora
if last_prompt and "data" in last_prompt.lower() and any(substr in last_prompt.lower() for substr in ["hoje", "agora", "hora", "estelar"]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    st.info(f"🕒 Data Estelar Atual (Cliente): {now}")

# Comando de limpar
if last_prompt and "limpar console" in last_prompt.lower():
    st.session_state.nash_history = []
    st.info("Histórico do console limpo.")
    time.sleep(1)
    st.rerun()

# Comando de auto-destruir
if last_prompt and "auto destruir" in last_prompt.lower():
    st.warning("🚨 Sequência de auto-destruição iniciada... Brincadeirinha.")
    st.snow()

# Easter egg: comando engage
if last_prompt and last_prompt.lower().strip() == "engage!":
    st.balloons()
    st.session_state.nash_history.append(("Nash", "🚀 *Sistemas de dobra espacial ativados, Capitão Eli. Velocidade de dobra 9... ENGAGE!*"))
    st.session_state.nash_msg_count += 1
    st.rerun()

# Easter egg: status do sistema
if last_prompt and "status do sistema" in last_prompt.lower():
    system_status = f"""
📊 **Relatório de Status do Sistema**
- Núcleo de IA: `Operando a 97.3%`
- Memória Quântica: `{random.randint(82, 99)}% disponível`
- Fluxo de Dilutiom: `Estável a {random.randint(120, 140)} MH/s`
- Integridade do Campo de Contenção: `{random.randint(95, 100)}%`
- Sistemas de Suporte Vital: `Nominal`
- Café na Replicadora: `Pronto para servir`
    """
    st.session_state.nash_history.append(("Nash", system_status))
    st.session_state.nash_msg_count += 1
    st.rerun()

######### --- EXIBIR HISTÓRICO DE CHAT APRIMORADO ---------------------
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")
    
    last_message_index = len(st.session_state.nash_history) - 1
    
    for i, (who, msg) in enumerate(st.session_state.nash_history):
        if who == "Nash":
            if i == last_message_index: 
                nash_typing(msg)
            else: 
                # Usar container para melhorar o contraste
                st.markdown(
                    f'<span class="avatar-nash">👨‍🚀 Nash:</span><div class="message-container message-nash-container"><span class="message-nash">{msg}</span></div>', 
                    unsafe_allow_html=True
                )
        else: 
            # Usar container para mensagens do Eli também
            st.markdown(
                f'<span class="avatar-eli">🧑‍🚀 Eli:</span><div class="message-container message-eli-container"><span class="message-eli">{msg}</span></div>', 
                unsafe_allow_html=True
            )
        
        if i < last_message_index: 
            st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
else: 
    st.markdown("> *Console aguardando o primeiro comando...*")

# Injeta Javascript para habilitar o botão de mostrar/esconder a barra lateral em mobile
st.markdown("""
<script>
// Adiciona indicador de notificação quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    // Mostrar mensagem de boas-vindas
    setTimeout(function() {
        try {
            showNotification('Bem-vindo à ponte da nave, Comandante!');
        } catch (e) {
            console.log('Erro ao mostrar notificação:', e);
        }
    }, 2000);
});
</script>
""", unsafe_allow_html=True)