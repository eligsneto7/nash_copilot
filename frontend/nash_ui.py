# --- START OF FILE nash_ui.py (Refatorado e Traduzido) ---

import os
import sys

# 1) Injeta o /backend no path antes de tentar importar qualquer coisa dele
HERE        = os.path.dirname(__file__)
BACKEND_DIR = os.path.join(HERE, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# 2) Agora sim import dos seus módulos
from nash_utils import (
    init_openai,
    init_pinecone,
    init_github,
    init_google_search,
    fetch_relevant_memories,
    register_memory,
    nash_log,
    allowed_file       as ALLOWED_EXTENSIONS,
    IMAGE_EXTS,
    CODE_EXTS,
    get_github_file_content,
    propose_github_change,
    perform_google_search,
    get_text_embedding
)

import streamlit as st
import requests
import time
import random
import html
import uuid  # Usado para keys únicas se necessário
from datetime import datetime, timedelta
from streamlit_extras.add_vertical_space import add_vertical_space
import json  # Para exibir conteúdo de código formatado

# --- Constantes ---
# Use st.secrets para produção ou variáveis de ambiente para o URL do backend
# BACKEND_URL = st.secrets.get("BACKEND_URL", "https://nashcopilot-production.up.railway.app")
BACKEND_URL = os.getenv("BACKEND_URL", "https://nashcopilot-production.up.railway.app") # Melhor ler do ambiente
REQUEST_TIMEOUT = (5, 65) # (connect timeout, read timeout em segundos)

# --- Definição do Tema CSS (Light Mode Adaptado e Traduzido) ---
# Escolhendo um tema clean e moderno como base.
MODERN_LIGHT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Fira+Mono:wght@400&display=swap');

/* --- Variáveis CSS --- */
:root {
    --ui-bg: #f7f9fc; /* Fundo principal ligeiramente off-white */
    --ui-card-bg: #ffffff; /* Fundo dos cards e chat */
    --ui-text: #212529; /* Cor principal do texto (escuro) */
    --ui-text-secondary: #6c757d; /* Cor secundária (cinza) */
    --ui-primary: #0052cc; /* Azul primário (um pouco mais vibrante) */
    --ui-primary-light: #e6f0ff; /* Azul bem claro para fundos sutis */
    --ui-accent: #007bff; /* Azul de destaque (links, etc.) */
    --ui-border-color: #dee2e6; /* Cor padrão de borda */
    --ui-input-bg: #ffffff; /* Fundo dos inputs */
    --ui-input-border: #ced4da; /* Borda dos inputs */
    --ui-code-bg: #f8f9fa; /* Fundo dos blocos de código */
    --ui-avatar-user-bg: #e6f0ff; /* Fundo avatar usuário (azul claro) */
    --ui-avatar-assistant-bg: #e9ecef; /* Fundo avatar assistente (cinza claro) */
    --font-sans: 'Inter', sans-serif;
    --font-mono: 'Fira Mono', 'Consolas', monospace;
}

/* --- Body e Geral --- */
body {
    background-color: var(--ui-bg);
    color: var(--ui-text) !important;
    font-family: var(--font-sans);
    line-height: 1.6;
    min-height: 100vh !important;
    overflow-x: hidden;
}

/* --- Área Principal --- */
.main > div {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1rem 1.5rem; /* Espaçamento interno */
}

/* --- Visor Superior --- */
#visor {
    background: var(--ui-card-bg);
    border-radius: 12px; margin-bottom: 2rem; border: 1px solid var(--ui-border-color);
    box-shadow: 0 2px 10px rgba(0, 82, 204, 0.05); padding: 1.25rem 1.75rem;
    display: flex; align-items: center; gap: 1.5rem; /* Alinhado ao centro verticalmente */
}
.nash-avatar-emoji {
    font-size: 3rem; line-height: 1; display: flex; align-items: center; justify-content: center;
    width: 60px; height: 60px; background-color: var(--ui-avatar-assistant-bg); border-radius: 50%;
    color: var(--ui-primary); /* Cor do emoji pode variar */
}
.visor-content { display: flex; flex-direction: column; flex-grow: 1; }
.nash-holo { font-size: 1.6em; color: var(--ui-primary); margin-bottom: 0px; font-weight: 700; }
.nash-enterprise-tag { font-size: 0.9em; color: var(--ui-text-secondary); margin-bottom: 0.75rem; }
.visor-analytics {
    color: var(--ui-text-secondary); font-size: 0.85em; padding: 0.6em 1em; background: var(--ui-bg);
    border-radius: 8px; border: 1px solid var(--ui-border-color); margin-top: 0.5rem; line-height: 1.5;
    font-family: var(--font-mono);
}
.visor-analytics b { color: var(--ui-text); font-weight: 500; }
.visor-analytics i { color: var(--ui-primary); opacity: 1; font-style: normal; } /* Ícone ou detalhe */

/* --- Botões --- */
.stButton > button {
    color: #ffffff; background-color: var(--ui-primary); border-radius: 8px; border: 1px solid var(--ui-primary);
    font-weight: 500; transition: all 0.2s ease; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); padding: 0.5rem 1rem; font-family: var(--font-sans);
    line-height: 1.5; /* Ajuste para alinhar texto */
}
.stButton > button:hover { background-color: #0041a3; border-color: #003b93; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1); color: #ffffff; }
.stButton > button:active { background-color: #003b93; }
.stButton > button:disabled { background-color: #adb5bd; color: #ffffff; border-color: #adb5bd; cursor: not-allowed; opacity: 0.7; }
/* Botão secundário/perigoso */
.stButton.clear-button > button { background-color: #dc3545; border-color: #dc3545; }
.stButton.clear-button > button:hover { background-color: #bb2d3b; border-color: #b02a37; }

/* --- Área de Input (st.chat_input) --- */
.stChatInputContainer {
    background: #ffffff; border-top: 1px solid var(--ui-border-color);
    padding: 0.8rem 1rem; margin: 0 -1.5rem -1rem -1.5rem; /* Ajusta para tocar bordas */
    box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.04);
}
.stChatInputContainer section { /* Container interno */
     border: 1px solid var(--ui-input-border) !important; background: var(--ui-input-bg) !important; border-radius: 8px !important;
     box-shadow: none !important;
}
.stChatInputContainer textarea {
    background: transparent !important; color: var(--ui-text) !important; border: none !important;
    box-shadow: none !important; font-size: 1em; padding: 0.6rem 0.8rem;
    font-family: var(--font-sans) !important; line-height: 1.5;
}
.stChatInputContainer textarea:focus { border-color: var(--ui-primary) !important; box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.15) !important; }
.stChatInputContainer ::placeholder { color: var(--ui-text-secondary) !important; opacity: 0.8 !important; }
.stChatInputContainer button[kind="icon"] { /* Botão de Enviar */
    background: var(--ui-primary) !important; border: none !important; border-radius: 50% !important; box-shadow: none !important;
    fill: #ffffff !important; padding: 5px !important; margin: 0 5px; /* Ajustes finos */
    transition: background-color 0.2s ease;
}
.stChatInputContainer button[kind="icon"]:hover { background: #0041a3 !important; }
.stChatInputContainer button[kind="secondary"] { /* Botão anexar (se visível) */
    border: none !important; fill: var(--ui-text-secondary) !important;
}

/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: var(--ui-bg) !important; border: 2px dashed var(--ui-border-color) !important; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;
}
.stFileUploader label > span { /* Texto "Arraste e solte..." */
    color: var(--ui-text-secondary) !important; font-size: 0.95em; display: block; text-align: center;
}
.stFileUploader label svg { /* Ícone de upload */
    color: var(--ui-primary) !important; margin: 0 auto 0.5rem auto; display: block; width: 30px; height: 30px;
}
.stFileUploader small { /* Texto "Limite X MB" */
    color: var(--ui-text-secondary) !important; font-size: 0.8em; text-align: center; display: block;
}
.stFileUploader div[data-testid="stFileUploaderButton"] button { /* Botão "Procurar arquivos" */
     margin: 0.5rem auto 0 auto; display: block; /* Centralizar botão */
}
.stFileUploader .uploadedFileName { /* Nome do arquivo após upload */
    font-family: var(--font-mono); font-size: 0.9em; background-color: var(--ui-primary-light); color: var(--ui-primary);
    padding: 0.3rem 0.6rem; border-radius: 4px; margin-top: 0.5rem; display: inline-block;
}

/* --- Histórico de Chat (st.chat_message) --- */
.stChatMessage {
    background-color: var(--ui-card-bg); border: 1px solid var(--ui-border-color); border-left-width: 4px;
    border-radius: 8px; margin-bottom: 1rem; padding: 0.8rem 1.1rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03); gap: 1rem !important;
    width: 98%; /* Evitar que cole na borda direita */
    max-width: 800px; /* Largura máxima para legibilidade */
}
/* Alinhamento e cores por role */
.stChatMessage[data-testid="chatAvatarIcon-user"] { /* Usuário (Eli) */
    margin-left: auto; margin-right: 0; /* Alinha à direita */
    border-left-color: var(--ui-accent); /* Usando accent (azul mais claro) */
}
.stChatMessage[data-testid="chatAvatarIcon-assistant"] { /* Assistente (Nash) */
     margin-left: 0; margin-right: auto; /* Alinha à esquerda */
     border-left-color: var(--ui-primary);
}
/* Avatares */
.stChatMessage .stChatMessageContent div[data-testid="chatAvatarIcon"] { /* Container do Avatar */
    width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; /* Tamanho do emoji */
}
.stChatMessage[data-testid="chatAvatarIcon-user"] .stChatMessageContent div[data-testid="chatAvatarIcon"] {
    background-color: var(--ui-avatar-user-bg);
}
.stChatMessage[data-testid="chatAvatarIcon-assistant"] .stChatMessageContent div[data-testid="chatAvatarIcon"] {
     background-color: var(--ui-avatar-assistant-bg);
}
/* Conteúdo do Markdown */
.stChatMessage .stMarkdown { color: var(--ui-text); line-height: 1.6; }
.stChatMessage .stMarkdown p { margin-bottom: 0.5rem; } /* Espaçamento entre parágrafos */
.stChatMessage .stMarkdown strong { color: var(--ui-primary); font-weight: 600;}
.stChatMessage .stMarkdown code { /* Código inline */
    font-family: var(--font-mono); background-color: var(--ui-primary-light); color: var(--ui-primary);
    padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.9em;
}
.stChatMessage .stMarkdown a { color: var(--ui-accent); text-decoration: none; border-bottom: 1px solid var(--ui-accent);}
.stChatMessage .stMarkdown a:hover { color: #0056b3; border-bottom-width: 2px;}

/* --- Blocos de Código (st.code) dentro do chat --- */
.stCodeBlock {
    border: 1px solid var(--ui-border-color); border-radius: 8px; background-color: var(--ui-code-bg) !important; margin: 1rem 0;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.04);
}
.stCodeBlock code {
    color: #212529; background-color: transparent !important; font-family: var(--font-mono);
    font-size: 0.9em; white-space: pre-wrap !important; word-wrap: break-word !important; padding: 1rem;
}
/* Toolbar do bloco de código (Copiar) */
.stCodeBlock div[data-testid="stCodeToolbar"] {
    background-color: var(--ui-code-bg) !important; border-bottom: 1px solid var(--ui-border-color); padding: 0.3rem 0.5rem;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: transparent !important; border: none !important; color: var(--ui-text-secondary) !important;
    opacity: 0.7; transition: opacity 0.3s ease; border-radius: 4px; padding: 0.2rem 0.4rem !important;
    display: flex; align-items: center; gap: 0.3rem;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover {
    opacity: 1; color: var(--ui-primary) !important; background-color: rgba(0, 82, 204, 0.05) !important;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button svg { /* Ícone de copiar */
    width: 16px; height: 16px;
}


/* --- Status do Backend Flutuante --- */
#backend-status {
    position: fixed; top: 10px; right: 15px; font-size: 0.85em; color: var(--ui-text-secondary); font-family: var(--font-mono);
    background: rgba(255, 255, 255, 0.9); padding: 5px 12px; border-radius: 15px; border: 1px solid var(--ui-border-color); z-index: 1000;
    box-shadow: 0 1px 5px rgba(0,0,0,0.07); backdrop-filter: blur(4px);
    display: flex; align-items: center; gap: 0.5rem;
}
#backend-status .status-dot { /* Pequeno círculo indicando status */
    width: 8px; height: 8px; border-radius: 50%; display: inline-block;
}
#backend-status .status-online { background-color: #28a745; /* Verde */ }
#backend-status .status-offline { background-color: #dc3545; /* Vermelho */ }
#backend-status .status-checking { background-color: #ffc107; /* Amarelo */ }
#backend-status .status-error { background-color: #fd7e14; /* Laranja */ }

/* --- Sidebar --- */
.stSidebar > div:first-child {
    background: var(--ui-card-bg); border-right: 1px solid var(--ui-border-color); padding: 1.5rem 1rem; /* Mais padding */
}
.stSidebar .stMarkdown h3 {
    color: var(--ui-primary); text-shadow: none; margin-top: 1.5rem; margin-bottom: 0.5rem; font-size: 1.1em; font-weight: 700;
    border-bottom: 1px solid var(--ui-border-color); padding-bottom: 0.3rem;
}
.stSidebar .stMarkdown h3:first-child { margin-top: 0; } /* Remove margem do primeiro título */

.stSidebar .stMarkdown, .stSidebar .stSelectbox label, .stSidebar .stCheckbox label, .stSidebar .stTextInput label, .stSidebar .stTextArea label {
     color: var(--ui-text); font-size: 0.95em; margin-bottom: 0.2rem; font-weight: 500;
}
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stCheckbox, .stSidebar .stExpander {
     margin-bottom: 1rem; /* Espaçamento entre elementos */
}
.stSidebar .stButton { margin-top: 0.5rem; } /* Menos margem acima dos botões */

.nash-profile-details { font-size: 0.9em; line-height: 1.5; margin-top: 0.5rem; color: var(--ui-text-secondary); padding-left: 5px; border-left: 3px solid var(--ui-primary-light); }
.nash-profile-details b { color: var(--ui-text); font-weight: 500; }

/* Inputs na Sidebar */
.stSidebar .stTextInput input, .stSidebar .stTextArea textarea {
     border: 1px solid var(--ui-input-border); border-radius: 6px; background-color: var(--ui-input-bg); color: var(--ui-text); font-size: 0.95em; padding: 0.5rem 0.7rem;
}
.stSidebar .stTextInput input:focus, .stSidebar .stTextArea textarea:focus {
    border-color: var(--ui-primary); box-shadow: 0 0 0 2px rgba(0, 82, 204, 0.15);
}

/* Expander na Sidebar (para Ações de Código) */
.stSidebar .stExpander {
    background-color: transparent !important; border: 1px solid var(--ui-border-color) !important; border-radius: 8px !important; margin-bottom: 1rem;
}
.stSidebar .stExpander header { /* Cabeçalho do Expander */
     background-color: transparent !important; border-bottom: none !important; padding: 0.6rem 0.8rem !important; font-weight: 500; color: var(--ui-primary);
}
.stSidebar .stExpander header:hover { background-color: rgba(0, 82, 204, 0.03) !important; }
.stSidebar .stExpander svg { fill: var(--ui-primary) !important; } /* Ícone de expandir/recolher */
.stSidebar .stExpander div[data-testid="stExpanderDetails"] { /* Conteúdo do Expander */
    padding: 0.8rem !important; background: var(--ui-bg); border-top: 1px solid var(--ui-border-color);
}

/* --- Indicador de Loading (st.spinner) --- */
.stSpinner > div { border-top-color: var(--ui-primary) !important; border-left-color: var(--ui-primary) !important; width: 30px !important; height: 30px !important; } /* Cor e tamanho do spinner */

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 15px; }
    .main > div { padding: 0.8rem; }
    #visor { flex-direction: column; align-items: flex-start; gap: 1rem; padding: 1rem; }
    .nash-avatar-emoji { font-size: 2.5rem; width: 50px; height: 50px; }
    .visor-content { align-items: flex-start; }
    .nash-holo { font-size: 1.4em; }
    .nash-enterprise-tag { font-size: 0.85em; }
    .visor-analytics { font-size: 0.8em; }
    .stChatMessage { padding: 0.6rem 0.8rem; margin-bottom: 0.75rem; width: 100%; max-width: none;}
    .stCodeBlock code { font-size: 0.85em; }
    #backend-status { font-size: 0.75em; padding: 4px 10px; top: 5px; right: 10px; }
    .stChatInputContainer { padding: 0.5rem; margin: 0 -0.8rem -0.8rem -0.8rem; }
    .stChatInputContainer textarea { font-size: 0.95em; }
    .stSidebar > div:first-child { padding: 1rem 0.8rem; }
    .stSidebar .stMarkdown h3 { font-size: 1.05em; }
}
</style>
"""

# --- Funções Auxiliares ---

def check_backend_status(force_check=False) -> tuple[str, str]:
    """Verifica o status do backend. Retorna (status_texto, status_classe_css)."""
    now = datetime.now()
    # Cache simples para evitar checagens muito frequentes
    cache_duration = timedelta(seconds=30)
    if not force_check and "last_backend_check" in st.session_state and \
       (now - st.session_state.last_backend_check) < cache_duration:
        return st.session_state.backend_status, st.session_state.backend_status_class

    status_text = "Verificando..."
    status_class = "status-checking"
    status_code = None

    try:
        ping_url = f"{BACKEND_URL}/pingnet"
        r = requests.get(ping_url, timeout=REQUEST_TIMEOUT[0]) # Timeout curto para ping
        status_code = r.status_code

        if status_code == 200:
            # <<< NOVO >>> Verificar se integrações estão ativas
            data = r.json()
            gh_ok = data.get("github_enabled", False)
            search_ok = data.get("search_enabled", False)
            if gh_ok and search_ok:
                 status_text = "ONLINE"
            elif gh_ok or search_ok:
                 status_text = "ONLINE (Parcial)"
            else:
                 status_text = "ONLINE (Base)"
            status_class = "status-online"
        else:
            status_text = f"Erro {status_code}"
            status_class = "status-error"

    except requests.exceptions.Timeout:
        status_text = "Timeout"
        status_class = "status-offline" # Considerar timeout como offline
    except requests.exceptions.ConnectionError:
        status_text = "Offline"
        status_class = "status-offline"
    except Exception as e:
        log.error(f"Erro inesperado ao checar backend: {e}")
        status_text = "Erro"
        status_class = "status-error"

    st.session_state.backend_status = status_text
    st.session_state.backend_status_class = status_class
    st.session_state.last_backend_check = now
    return status_text, status_class

def escape_html_tags(text: str) -> str:
    """Escapa caracteres HTML para exibição segura."""
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text, quote=True)

# <<< REMOVIDO >>> scroll_to_bottom_js() - Streamlit gerencia melhor o scroll agora com chat_message/chat_input

# --- Inicialização do Estado da Sessão ---
def init_session_state():
    """Inicializa as variáveis do estado da sessão se não existirem."""
    defaults = {
        "start_time": datetime.now(),
        "history": [], # Histórico do chat
        "eli_msg_count": 0,
        "nash_msg_count": 0,
        "is_authenticated": False, # Status de autenticação
        "backend_status": "N/A",
        "backend_status_class": "status-checking",
        "last_backend_check": None,
        "waiting_for_nash": False, # Flag para indicar espera por resposta
        "uploaded_file_info": None, # Info do arquivo anexado {'name': ..., 'type': ..., 'backend_ref': ...}
        "uploaded_file_id": None,   # ID único do arquivo carregado para evitar re-upload
        "login_error": None, # Mensagem de erro do login
        "auto_scroll": True, # Se scrolla automaticamente (pode ser desabilitado)
        "session_uuid": str(uuid.uuid4()) # ID único para a sessão da UI (pode ser útil)
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
    log.info(f"Estado da sessão inicializado (UUID: {st.session_state.session_uuid}). Autenticado: {st.session_state.is_authenticated}")

# --- Renderização do Visor ---
def render_visor():
    """Renderiza o componente do visor superior com informações."""
    status, _ = check_backend_status() # Pega só o texto do status
    uptime_delta = datetime.now() - st.session_state.start_time
    # Formatar uptime de forma mais legível
    total_seconds = int(uptime_delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours:02}:{minutes:02}:{seconds:02}"

    # Métrica simples de engajamento
    engagement = st.session_state.eli_msg_count + st.session_state.nash_msg_count
    engagement_level = "HIGH" if engagement > 10 else ("MEDIUM" if engagement > 3 else "LOW")

    visor_html = f"""
    <div id="visor">
        <span class="nash-avatar-emoji">👨‍🚀</span>
        <div class="visor-content">
            <span class="nash-holo">Nash Copilot</span>
            <span class="nash-enterprise-tag">Interface de Comando Digital Eli</span>
            <div class="visor-analytics" title="Estatísticas da Sessão">
                <span>Sessão: <b>{uptime_str}</b></span> |
                <span>Cmds: <b>{st.session_state.eli_msg_count}</b></span> |
                <span>Resps: <b>{st.session_state.nash_msg_count}</b></span> |
                <span>Engajamento: <i>{engagement_level}</i></span>
            </div>
        </div>
    </div>
    """
    st.markdown(visor_html, unsafe_allow_html=True)

# --- Lógica de Login ---
def handle_login():
    """Gerencia a tela e o processo de login."""
    st.markdown("### Autenticação Necessária")
    st.markdown("Por favor, insira o código de autorização para ativar o Nash.")

    if st.session_state.login_error:
        st.error(f"Falha na autenticação: {st.session_state.login_error}")

    password = st.text_input(
        "Código de Autorização:",
        type="password",
        key="login_password_input",
        placeholder="Digite o código aqui...",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 3]) # Coluna para botão e espaço
    with col1:
        login_pressed = st.button("Autenticar ✨", key="login_button", use_container_width=True, disabled=st.session_state.waiting_for_nash)

    # Tenta logar se o botão foi pressionado ou se já estava esperando (após rerun)
    if login_pressed or (st.session_state.waiting_for_nash and not st.session_state.is_authenticated):
        if not password and login_pressed: # Verifica senha vazia apenas no clique inicial
            st.session_state.login_error = "O código de autorização não pode estar vazio."
            st.session_state.waiting_for_nash = False # Resetar flag se falhou antes de tentar
            st.rerun()

        # Marcar que está tentando / esperando
        st.session_state.waiting_for_nash = True
        st.session_state.login_error = None # Limpar erro anterior

        # Mostrar spinner enquanto tenta logar (só aparece após rerun)
        with st.spinner("Verificando credenciais com o backend..."):
            login_success = False
            actual_password = st.session_state.login_password_input # Pega a senha do estado atual
            try:
                log.info("Tentando autenticar no backend...")
                r = requests.post(f"{BACKEND_URL}/login", json={"password": actual_password}, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.is_authenticated = True
                    login_success = True
                    st.session_state.login_error = None
                    log.info("Autenticação bem-sucedida!")
                    st.toast("Autenticação bem-sucedida! Protocolos ativados.", icon="✅")
                else:
                    error_msg = r.json().get("msg", f"Falha (Status: {r.status_code})")
                    st.session_state.login_error = escape_html_tags(error_msg)
                    log.warning(f"Falha na autenticação: {error_msg}")

            except requests.exceptions.RequestException as e:
                st.session_state.login_error = f"Erro de rede durante autenticação: {e}"
                log.error(f"Erro de rede na autenticação: {e}")
            except Exception as e:
                st.session_state.login_error = f"Erro inesperado durante autenticação: {e}"
                log.exception("Erro inesperado na autenticação:")
            finally:
                st.session_state.waiting_for_nash = False # Terminou a tentativa
                if login_success:
                    # Limpar campo de senha visualmente (rerun necessário)
                    st.session_state.login_password_input = "" # Limpa o valor no estado
                    time.sleep(0.5) # Pequena pausa para toast
                    st.rerun()
                else:
                    # Apenas reroda para mostrar o erro (ou manter estado se já estava esperando)
                    st.rerun()

    # Se não autenticado, parar aqui
    if not st.session_state.is_authenticated:
        st.stop()


# --- Lógica de Upload ---
def handle_file_upload(upload_status_placeholder):
    """Gerencia o upload de arquivos na sidebar."""
    uploaded_file = st.file_uploader(
        "Anexar Arquivo (Opcional)",
        # type=[ext.lstrip('.') for ext in ALLOWED_FILE_EXTENSIONS], # Gerar tipos permitidos
        key="file_uploader_widget",
        label_visibility="collapsed", # O título da seção já serve como label
        help="Anexe um arquivo para análise junto com seu próximo comando."
    )

    if uploaded_file is not None:
        # Verificar se é um arquivo novo para evitar re-upload a cada rerun
        # Usar nome e tamanho como identificador simples
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        previous_file_id = st.session_state.get("uploaded_file_id")

        # Processar apenas se for um arquivo diferente do anterior
        if current_file_id != previous_file_id:
            st.session_state.uploaded_file_info = None # Resetar info antiga

            # Validar extensão no frontend também (embora backend valide)
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            # Reconstruir lista de extensões permitidas para mensagem de erro
            allowed_ext_list = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg",
                                ".py", ".txt", ".md", ".json", ".csv", ".pdf", ".log", ".sh", ".yaml", ".toml", ".html", ".css", ".js", ".ipynb",
                                ".mp3", ".wav", ".ogg", ".mp4", ".mov", ".avi", ".webm"} # Exemplo, idealmente viria do backend
            if file_ext not in allowed_ext_list:
                 upload_status_placeholder.error(f"Tipo de arquivo '{file_ext}' não permitido.")
                 st.session_state.uploaded_file_id = None # Marca como não enviado
                 # Limpar o uploader visualmente (requer rerun com chave diferente ou truque)
                 # st.session_state.file_uploader_widget = None # Tentar limpar estado (pode não funcionar)
                 return # Não processa

            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                with upload_status_placeholder, st.spinner(f"Transmitindo '{escape_html_tags(uploaded_file.name)}'..."):
                    log.info(f"Iniciando upload para backend: {uploaded_file.name} ({uploaded_file.size} bytes)")
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT) # Timeout maior para uploads

                if r.status_code == 200:
                    response_data = r.json()
                    st.session_state.uploaded_file_info = {
                        "name": uploaded_file.name,
                        "type": uploaded_file.type,
                        "backend_ref": response_data.get("filename") # Referência do backend
                    }
                    st.session_state.uploaded_file_id = current_file_id # Marcar como enviado com sucesso
                    upload_status_placeholder.success(f"✅ '{escape_html_tags(uploaded_file.name)}' anexado!")
                    log.info(f"Upload bem-sucedido: {response_data.get('filename')}")
                else:
                    error_msg = r.json().get("message", r.text)
                    upload_status_placeholder.error(f"Falha no Upload ({r.status_code}): {escape_html_tags(error_msg)}")
                    log.error(f"Falha no upload ({r.status_code}): {error_msg}")
                    st.session_state.uploaded_file_info = None
                    st.session_state.uploaded_file_id = None

            except requests.exceptions.Timeout:
                upload_status_placeholder.error("Timeout durante o upload. Tente novamente.")
                log.error("Timeout durante upload.")
                st.session_state.uploaded_file_info = None
                st.session_state.uploaded_file_id = None
            except requests.exceptions.RequestException as e:
                 upload_status_placeholder.error(f"Erro de rede durante upload: {e}")
                 log.error(f"Erro de rede no upload: {e}")
                 st.session_state.uploaded_file_info = None
                 st.session_state.uploaded_file_id = None
            except Exception as e:
                upload_status_placeholder.error(f"Erro inesperado no upload: {e}")
                log.exception("Erro inesperado no upload:")
                st.session_state.uploaded_file_info = None
                st.session_state.uploaded_file_id = None
        # else: # Mesmo arquivo, já foi processado (não precisa fazer nada ou mostrar msg)
             # upload_status_placeholder.info(f"📎 Anexado: `{escape_html_tags(uploaded_file.name)}`")

    elif uploaded_file is None and st.session_state.uploaded_file_info:
        # Se o uploader foi limpo pelo usuário (clicou no 'x'), limpar o estado
        log.info("Arquivo desanexado pelo usuário.")
        st.session_state.uploaded_file_info = None
        st.session_state.uploaded_file_id = None
        upload_status_placeholder.empty() # Limpa a mensagem de status

    # Mostrar info do arquivo pronto para ser anexado (se houver)
    if st.session_state.uploaded_file_info and uploaded_file: # Mostra só se ainda estiver no uploader
         upload_status_placeholder.info(f"📎 Pronto: `{escape_html_tags(st.session_state.uploaded_file_info['name'])}`")


# --- Renderização da Sidebar ---
def render_sidebar():
    """Renderiza a sidebar com controles, informações e novas ações."""
    with st.sidebar:
        st.markdown("### 🛰️ Upload de Dados")
        upload_status_placeholder = st.empty() # Placeholder para mensagens de status do upload
        handle_file_upload(upload_status_placeholder)
        add_vertical_space(1)

        # <<< NOVO >>> Ações de Código
        st.markdown("### 💻 Ações de Código (GitHub)")
        with st.expander("Ler ou Propor Alterações no Código", expanded=False):
            st.caption("Interaja diretamente com o código-fonte do Nash no GitHub.")

            # Ler Arquivo
            st.markdown("**Ler Arquivo:**")
            read_file_path = st.text_input("Caminho do Arquivo (e.g., `nash_api.py`)", key="read_code_path", placeholder="src/arquivo.py")
            if st.button("Ler Conteúdo 📄", key="read_code_btn", use_container_width=True):
                if read_file_path:
                    handle_read_code(read_file_path)
                else:
                    st.warning("Por favor, insira o caminho do arquivo para leitura.")

            add_vertical_space(1)

            # Propor Mudança
            st.markdown("**Propor Mudança:**")
            propose_file_path = st.text_input("Caminho do Arquivo para Modificar", key="propose_code_path", placeholder="nash_utils.py")
            propose_desc = st.text_area("Descrição da Mudança Solicitada", key="propose_code_desc", placeholder="Ex: Adicionar tratamento para erro X na função Y")
            # O conteúdo novo será gerado pelo LLM no backend a partir da descrição

            if st.button("Gerar e Propor Mudança ✨", key="propose_code_btn", use_container_width=True):
                 if propose_file_path and propose_desc:
                     handle_propose_change(propose_file_path, propose_desc)
                 else:
                     st.warning("Por favor, preencha o caminho do arquivo e a descrição da mudança.")

        add_vertical_space(1)

        st.markdown("### ⚙️ Controles da Sessão")
        st.checkbox("Scroll Automático", key="auto_scroll", help="Rolar automaticamente para a última mensagem.")
        if st.button("Limpar Histórico da Sessão", key="clear_chat_btn", help="Apagar todas as mensagens desta sessão.", use_container_width=True, type="secondary"):
             clear_session() # Chama função para limpar estado
             st.rerun() # Atualiza a UI

        add_vertical_space(2)

        st.markdown("### 🧠 Perfil Nash Core")
        status_text, status_class = check_backend_status()
        # <<< MODIFICADO >>> Atualizado com novas capacidades
        profile_html = f"""
        <div class="nash-profile-details">
            Designação: <b>Nash</b><br>
            Classe: Copiloto Digital AI<br>
            Memória: Vetorizada (Pinecone)<br>
            Backend: <span title="Última verificação: {st.session_state.last_backend_check}">{status_text}</span><br>
            Autenticação: <b>{'CONCEDIDA' if st.session_state.is_authenticated else 'REQUERIDA'}</b><br>
            <b>Capacidades Ativas:</b><br>
             - Busca Web (Google)<br>
             - Leitura Código (GitHub)<br>
             - Proposta Código (GitHub)<br>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)

# --- <<< NOVO >>> Funções para Ações de Código ---
def handle_read_code(file_path):
    """Envia requisição para ler arquivo do GitHub via backend."""
    st.session_state.waiting_for_nash = True # Usa a mesma flag de espera
    st.rerun() # Rerun para mostrar spinner

def process_read_code(file_path):
    """Processa a leitura do código após o rerun."""
    if not st.session_state.waiting_for_nash: return

    code_content = None
    error_message = None
    try:
        with st.spinner(f"Lendo '{escape_html_tags(file_path)}' do GitHub..."):
            log.info(f"Enviando pedido /read_code para backend: {file_path}")
            r = requests.post(f"{BACKEND_URL}/read_code", json={"file_path": file_path}, timeout=REQUEST_TIMEOUT)

            if r.status_code == 200:
                code_content = r.json().get("content")
                log.info(f"Conteúdo de '{file_path}' recebido com sucesso.")
                # Adiciona ao histórico como uma 'resposta' informativa
                st.session_state.history.append({
                    "role": "assistant", # Ou um role customizado "system" ou "tool"?
                    "content": f"**Conteúdo de `{file_path}` lido do GitHub:**\n```python\n{code_content}\n```"
                })
                st.session_state.nash_msg_count += 1 # Conta como uma resposta
            else:
                error_message = r.json().get("error", f"Erro desconhecido ({r.status_code})")
                log.error(f"Erro ao ler código via backend ({r.status_code}): {error_message}")

    except requests.exceptions.RequestException as e:
        error_message = f"Erro de rede ao contatar o backend: {e}"
        log.error(f"Erro de rede em /read_code: {e}")
    except Exception as e:
        error_message = f"Erro inesperado: {e}"
        log.exception("Erro inesperado em process_read_code:")
    finally:
        if error_message:
             st.session_state.history.append({
                 "role": "assistant",
                 "content": f"**Falha ao ler `{file_path}`:**\n```\n{escape_html_tags(error_message)}\n```"
             })
             st.session_state.nash_msg_count += 1
        st.session_state.waiting_for_nash = False
        st.rerun() # Rerun final para exibir o conteúdo ou erro

def handle_propose_change(file_path, description):
    """Envia requisição para propor mudança no GitHub via backend."""
    # Guardar os parâmetros para usar após o rerun
    st.session_state.propose_params = {"file_path": file_path, "description": description}
    st.session_state.waiting_for_nash = True
    st.rerun()

def process_propose_change():
    """Processa a proposta de mudança após o rerun."""
    if not st.session_state.waiting_for_nash or "propose_params" not in st.session_state:
        st.session_state.waiting_for_nash = False # Limpa flag se params sumiram
        return

    params = st.session_state.propose_params
    file_path = params["file_path"]
    description = params["description"]
    response_message = None
    error_message = None

    try:
        spinner_msg = f"Gerando e propondo mudanças para '{escape_html_tags(file_path)}'..."
        with st.spinner(spinner_msg):
            log.info(f"Enviando pedido /propose_code_change para backend: {file_path}")
            payload = {"file_path": file_path, "description": description}
            # Adicionar base_branch se necessário: payload["base_branch"] = "develop"
            r = requests.post(f"{BACKEND_URL}/propose_code_change", json=payload, timeout=(10, 120)) # Timeout maior para LLM + Git

            if r.status_code == 200:
                result = r.json()
                response_message = f"✅ **Proposta de mudança criada com sucesso!**\n" \
                                   f"- **Arquivo:** `{result.get('file_path')}`\n" \
                                   f"- **Branch:** `{result.get('branch')}`\n" \
                                   f"- **Commit:** `{result.get('commit_sha', 'N/A')[:7]}`\n" \
                                   f"*Revise e faça o merge no GitHub quando estiver pronto.*"
                log.info(f"Proposta de mudança criada: Branch {result.get('branch')}")
            else:
                error_message = r.json().get("error", f"Erro desconhecido ({r.status_code})")
                log.error(f"Erro ao propor mudança via backend ({r.status_code}): {error_message}")

    except requests.exceptions.Timeout:
        error_message = "Timeout: A geração ou proposta da mudança demorou demais."
        log.error("Timeout em /propose_code_change.")
    except requests.exceptions.RequestException as e:
        error_message = f"Erro de rede ao contatar o backend: {e}"
        log.error(f"Erro de rede em /propose_code_change: {e}")
    except Exception as e:
        error_message = f"Erro inesperado: {e}"
        log.exception("Erro inesperado em process_propose_change:")
    finally:
        if response_message:
            st.session_state.history.append({"role": "assistant", "content": response_message})
            st.session_state.nash_msg_count += 1
        elif error_message:
             st.session_state.history.append({
                 "role": "assistant",
                 "content": f"**Falha ao propor mudança para `{file_path}`:**\n```\n{escape_html_tags(error_message)}\n```"
             })
             st.session_state.nash_msg_count += 1
        # Limpar parâmetros e flag de espera
        st.session_state.waiting_for_nash = False
        if "propose_params" in st.session_state:
            del st.session_state.propose_params
        st.rerun() # Rerun final para exibir o resultado

# --- Limpeza da Sessão ---
def clear_session():
     """Limpa o histórico e contadores da sessão."""
     st.session_state.history = []
     st.session_state.eli_msg_count = 0
     st.session_state.nash_msg_count = 0
     st.session_state.uploaded_file_info = None
     st.session_state.uploaded_file_id = None
     # Poderia resetar outros estados se necessário
     log.info("Histórico da sessão limpo.")
     st.toast("🧹 Histórico da sessão limpo!", icon="✨")
     time.sleep(0.5)

# --- Renderização do Histórico ---
def render_history(chat_container):
    """Renderiza o histórico de mensagens no container fornecido."""
    with chat_container:
        if not st.session_state.history:
             st.markdown("> *Console de comando aguardando input... Digite sua instrução abaixo.*")
             return # Sai se não há histórico

        for i, message in enumerate(st.session_state.history):
            role = message["role"] # "user" or "assistant"
            content = message["content"]
            avatar = "🧑‍🚀" if role == "user" else "👨‍🚀" # Eli | Nash
            # Usar key única para cada mensagem ajuda Streamlit a gerenciar o estado
            with st.chat_message(role, avatar=avatar):
                # Renderiza o conteúdo como Markdown
                # unsafe_allow_html=True pode ser necessário para HTML específico, mas False é mais seguro
                st.markdown(content, unsafe_allow_html=False)

    # <<< REMOVIDO >>> JS de scroll - Deixar Streamlit gerenciar

# --- Envio de Prompt e Comunicação com Backend ---
def handle_chat_input(prompt: str):
    """Processa o input do usuário, envia ao backend e atualiza o histórico."""
    if not prompt:
        return # Não faz nada se o prompt estiver vazio

    log.debug(f"Usuário digitou: {prompt[:50]}...")
    # Adiciona mensagem do usuário ao histórico imediatamente
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.eli_msg_count += 1

    # Prepara payload para backend
    payload = {"prompt": prompt, "session_id": st.session_state.session_uuid} # Usar UUID da sessão

    # Anexa informação do arquivo se houver
    if st.session_state.uploaded_file_info:
        # O backend precisa saber como usar essa info (ex: ler do /uploads/<backend_ref>)
        payload["attachment_info"] = {
            "filename": st.session_state.uploaded_file_info["name"],
            "type": st.session_state.uploaded_file_info["type"],
            "backend_ref": st.session_state.uploaded_file_info["backend_ref"]
        }
        log.info(f"Anexando info do arquivo ao prompt: {st.session_state.uploaded_file_info['name']}")
        # Limpa info do arquivo após anexar ao prompt (para não anexar de novo automaticamente)
        st.session_state.uploaded_file_info = None
        st.session_state.uploaded_file_id = None
        # Limpar o widget de upload visualmente é complicado, usuário pode precisar re-anexar

    # Marca que está esperando e reroda para mostrar mensagem do usuário + spinner
    st.session_state.waiting_for_nash = True
    st.rerun()

# --- Lógica Principal pós-rerun para buscar resposta do Chat ---
def fetch_nash_response():
    """Chamado após rerun se waiting_for_nash for True. Busca resposta do backend."""
    if not st.session_state.waiting_for_nash:
        return # Só executa se estiver esperando resposta do chat

    # Pega a última mensagem do usuário para reenviar (backend pode não ter histórico completo)
    last_user_message = next((msg for msg in reversed(st.session_state.history) if msg["role"] == "user"), None)
    if not last_user_message:
        log.error("Não foi possível encontrar a última mensagem do usuário no histórico.")
        st.session_state.waiting_for_nash = False
        # Adicionar mensagem de erro ao histórico?
        st.session_state.history.append({"role": "assistant", "content": "[Erro Interno da UI: Não encontrei sua última mensagem para enviar ao Nash.]"})
        st.rerun()
        return

    # Reconstrói payload (sem anexo, já foi tratado no handle_chat_input)
    payload = {"prompt": last_user_message["content"], "session_id": st.session_state.session_uuid}
    log.info(f"Enviando prompt para /chat backend: {payload['prompt'][:50]}...")

    response_content = ""
    try:
        # Exibe spinner DENTRO da mensagem de "pensando" do Nash
        with st.chat_message("assistant", avatar="👨‍🚀"):
            with st.spinner("Nash está processando seu comando..."):
                req = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=REQUEST_TIMEOUT)

                if req.status_code == 200:
                    response_content = req.json().get("response", "[Nash não retornou uma resposta textual.]")
                    log.info(f"Resposta recebida do /chat: {response_content[:50]}...")
                    st.session_state.nash_msg_count += 1
                else:
                    try: error_payload = req.json().get("error", req.text)
                    except ValueError: error_payload = req.text # Se não for JSON
                    response_content = f"**[Erro do Backend {req.status_code}]**\nOcorreu um problema ao processar seu pedido:\n```\n{escape_html_tags(str(error_payload)[:300])}\n```" # Limita tamanho
                    log.error(f"Erro do backend /chat ({req.status_code}): {error_payload}")
                    st.session_state.nash_msg_count += 1 # Conta erro como resposta

    except requests.exceptions.Timeout:
        response_content = "[Timeout da Requisição] Nash demorou muito para responder. Verifique o status do backend ou tente novamente."
        log.error("Timeout ao chamar /chat backend.")
        st.session_state.nash_msg_count += 1
    except requests.exceptions.RequestException as e:
        response_content = f"[Erro de Rede] Não foi possível conectar ao núcleo do Nash.\n```\n{escape_html_tags(str(e))}\n```"
        log.error(f"Erro de rede ao chamar /chat: {e}")
        st.session_state.nash_msg_count += 1
    except Exception as e:
        response_content = f"[Erro Inesperado na UI] Ocorreu um problema ao buscar a resposta.\n```\n{escape_html_tags(str(e))}\n```"
        log.exception("Erro inesperado em fetch_nash_response:")
        st.session_state.nash_msg_count += 1
    finally:
        st.session_state.history.append({"role": "assistant", "content": response_content})
        st.session_state.waiting_for_nash = False
        # Rerun final para exibir a resposta do Nash
        st.rerun()


# --- Função Principal da Aplicação ---
def main():
    """Função principal que organiza a UI do Streamlit."""
    st.set_page_config(page_title="Nash Copilot", page_icon="👨‍🚀", layout="wide")

    # Inicializa logger para UI (se não feito globalmente)
    global log
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

    # Aplica o CSS moderno
    st.markdown(MODERN_LIGHT_CSS, unsafe_allow_html=True)

    init_session_state() # Garante que o estado da sessão existe

    # Status flutuante (atualizado no início de cada run)
    status_text, status_class = check_backend_status()
    st.markdown(f"""
    <div id='backend-status' title='Status do Backend Nash'>
        <span class="status-dot {status_class}"></span>
        Backend: {status_text}
    </div>""", unsafe_allow_html=True)

    # Renderiza Sidebar (sempre visível)
    render_sidebar()

    # Lógica de Autenticação / Bloqueio
    if not st.session_state.is_authenticated:
        handle_login() # Função cuida do input, botão, chamada e st.stop()
        # O código abaixo só roda se handle_login *não* chamar st.stop()
        # (ou seja, após autenticação bem-sucedida e rerun)

    # Área Principal (Visor + Chat) - Só mostra se autenticado
    render_visor()

    # Container para o histórico de chat (altura pode ser ajustada se necessário)
    # chat_container = st.container(height=600) # Exemplo com altura fixa
    chat_container = st.container()
    render_history(chat_container) # Renderiza o histórico atual

    # Lógica pós-rerun para ações pendentes (chat, leitura de código, proposta de mudança)
    # A flag waiting_for_nash agora diferencia qual ação está pendente (implícito pelo estado)
    if st.session_state.waiting_for_nash:
        if "propose_params" in st.session_state:
             process_propose_change()
        elif st.session_state.get("read_code_path_pending"): # Necessário um marcador se não tiver params
             # Implementar process_read_code() - Assumindo que foi chamado por handle_read_code()
             # Deveria ter o file_path no estado
             # process_read_code(st.session_state.read_code_path_pending) # Exemplo
             pass # Adicionar lógica de chamada para process_read_code aqui
        else:
            # Assume que é uma resposta de chat pendente
            fetch_nash_response()

    # Input de Chat (Usando st.chat_input) - Deve ser o último elemento interativo principal
    if prompt := st.chat_input("Digite seu comando para Nash...", key="chat_input_widget", disabled=st.session_state.waiting_for_nash):
        handle_chat_input(prompt)


# --- Execução ---
if __name__ == "__main__":
    # Definir log global aqui se necessário
    log = logging.getLogger(__name__)
    main()

# --- END OF FILE nash_ui.py ---
