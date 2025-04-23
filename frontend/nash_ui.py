# --- START OF FILE nash_ui.py (Refatorado) ---

import streamlit as st
import requests
import time
import random
import html
import uuid
from datetime import datetime, timedelta
from streamlit_extras.add_vertical_space import add_vertical_space # Exemplo de uso de extras
# Considerar 'from streamlit_extras.stoggle import stoggle' para seções colapsáveis se necessário

# --- Constantes ---
# Use st.secrets para produção ou variáveis de ambiente
# BACKEND_URL = st.secrets.get("BACKEND_URL", "https://nashcopilot-production.up.railway.app") # Exemplo com secrets
BACKEND_URL = "https://nashcopilot-production.up.railway.app" # Mantendo como no original por enquanto
REQUEST_TIMEOUT = (5, 65) # (connect timeout, read timeout)

# Textos dos Sinais (Mantidos)
SIGN_PANIC_TEXT = "NÃO ENTRE EM PÂNICO"
SIGN_42_TEXT = "42"

# --- Definições de Temas CSS ---

# Tema Cyberpunk Refinado
CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

/* --- Variáveis CSS (Exemplo) --- */
:root {
    --cyber-bg: #0d0f18;
    --cyber-bg-gradient: radial-gradient(ellipse at center, #10121f 0%, #0b0c14 70%), linear-gradient(145deg, #0b0c14 70%, #181a29 100%);
    --cyber-text: #d0d8ff;
    --cyber-primary: #0affa0; /* Verde Neon */
    --cyber-secondary: #ff07e6; /* Magenta Neon */
    --cyber-accent: #0aebff; /* Azul Neon Claro */
    --cyber-border-color: #0affa040;
    --cyber-border-color-hover: #0affa090;
    --cyber-input-bg: #101225;
    --cyber-code-bg: rgba(10, 12, 25, 0.9);
    --cyber-card-bg: linear-gradient(170deg, #0f111a 0%, #1c202f 100%);
    --font-mono: 'Fira Mono', 'Consolas', monospace;
    --font-display: 'Orbitron', 'Fira Mono', monospace;
}

/* --- Animações --- */
@keyframes blink-neon {
  0%, 100% { opacity: 1; text-shadow: 0 0 7px var(--cyber-secondary), 0 0 15px var(--cyber-secondary), 0 0 20px var(--cyber-secondary); }
  50% { opacity: 0.7; text-shadow: 0 0 5px color-mix(in srgb, var(--cyber-secondary), transparent 40%), 0 0 10px color-mix(in srgb, var(--cyber-secondary), transparent 40%); }
}
@keyframes subtle-pulse { 0%, 100% { opacity: 0.9; } 50% { opacity: 1; } }
@keyframes thinking-pulse {
    0% { background-color: color-mix(in srgb, var(--cyber-primary), transparent 70%); box-shadow: 0 0 8px color-mix(in srgb, var(--cyber-primary), transparent 70%); }
    50% { background-color: color-mix(in srgb, var(--cyber-primary), transparent 60%); box-shadow: 0 0 15px color-mix(in srgb, var(--cyber-primary), transparent 50%); }
    100% { background-color: color-mix(in srgb, var(--cyber-primary), transparent 70%); box-shadow: 0 0 8px color-mix(in srgb, var(--cyber-primary), transparent 70%); }
}
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Body e Geral --- */
body {
    background: var(--cyber-bg-gradient);
    background-attachment: fixed;
    color: var(--cyber-text) !important;
    font-family: var(--font-mono);
    min-height: 100vh !important;
    overflow-x: hidden;
}
body::before { /* Overlay sutil de chuva/estática */
    content: ''; background-image: url('https://www.transparenttextures.com/patterns/scanlines.png'), linear-gradient(rgba(10, 255, 160, 0.02), rgba(10, 255, 160, 0.01));
    opacity: .08; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;
    pointer-events: none; background-size: auto, cover; mix-blend-mode: overlay;
}

/* --- Área Principal --- */
.main > div { /* Container principal do Streamlit */
    background: none !important; /* Remove fundo padrão */
    border: none !important; /* Remove borda padrão */
    box-shadow: none !important;
}

/* --- Visor Holográfico --- */
#visor {
    background: linear-gradient(135deg, rgba(16, 18, 37, 0.97) 80%, color-mix(in srgb, var(--cyber-secondary), transparent 15%) 140%), rgba(5, 5, 15, 0.96);
    border-radius: 15px; margin-bottom: 25px; border: 2.5px solid color-mix(in srgb, var(--cyber-secondary), transparent 60%);
    box-shadow: 0 0 30px color-mix(in srgb, var(--cyber-secondary), transparent 70%), inset 0 0 15px rgba(16, 18, 37, 0.88); padding: 18px 26px 14px 30px;
    display: flex; align-items: flex-start; gap: 25px; /* Alinhar ao topo */
}
.nash-avatar-emoji { font-size: 4rem; filter: drop-shadow(0 0 15px color-mix(in srgb, var(--cyber-primary), transparent 40%)); line-height: 1; animation: subtle-pulse 3s infinite ease-in-out; }
.visor-content { display: flex; flex-direction: column; } /* Container para texto */
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b { font-family: var(--font-display); user-select: none; }
.nash-holo { font-size: 2.1em; color: var(--cyber-primary); text-shadow: 0 0 15px color-mix(in srgb, var(--cyber-primary), transparent 40%), 0 0 5px rgba(255, 255, 255, 0.37); margin-bottom: 3px; }
.nash-enterprise-tag { font-size: 0.9em; color: color-mix(in srgb, var(--cyber-secondary), transparent 30%); font-family: var(--font-mono); }
.nash-ascii { font-family: var(--font-mono); color: color-mix(in srgb, var(--cyber-primary), transparent 20%); letter-spacing: 0.5px; line-height: 1.2; font-size: 0.95em; text-shadow: 0 0 8px color-mix(in srgb, var(--cyber-primary), transparent 80%); margin-top: 10px; margin-bottom: 10px; white-space: pre; }
.nash-ascii b { color: var(--cyber-secondary); font-weight: bold; }
.visor-analytics {
    color: var(--cyber-secondary); font-size: 0.95em; padding: 0.4em 1.3em; background: rgba(10, 10, 25, 0.75);
    border-radius: 8px; border: 1px solid color-mix(in srgb, var(--cyber-secondary), transparent 70%); margin-top: 12px; line-height: 1.45;
}
.visor-analytics b { color: #ffffff; }
.visor-analytics i { color: #c8d3ff; opacity: 0.85; }

/* --- Botões --- */
.stButton > button {
    color: #e0e8ff; background: #1f243d; border-radius: 8px; border: 2px solid var(--cyber-border-color);
    font-weight: bold; transition: all 0.3s ease; box-shadow: 0 0 10px rgba(10, 255, 160, 0.12); padding: 0.4rem 0.8rem; font-family: var(--font-mono);
}
.stButton > button:hover { background: #2a3050; border-color: var(--cyber-border-color-hover); box-shadow: 0 0 18px rgba(10, 255, 160, 0.37); color: #ffffff; }
.stButton > button:active { background: #15182a; }
.stButton > button:disabled { background: #2d334a; color: #7b84a3; border-color: #424861; cursor: not-allowed; }
.stButton.clear-button > button { border-color: color-mix(in srgb, var(--cyber-secondary), transparent 55%); color: #ffc0e8; box-shadow: 0 0 10px color-mix(in srgb, var(--cyber-secondary), transparent 80%); }
.stButton.clear-button > button:hover { border-color: var(--cyber-secondary); background: #3d1f35; box-shadow: 0 0 18px color-mix(in srgb, var(--cyber-secondary), transparent 60%); color: #ffffff; }

/* --- Área de Input (st.chat_input) --- */
.stChatInputContainer {
    background: transparent; /* Fundo já é do body */
    border-top: 1px solid var(--cyber-border-color);
    padding: 1rem 0.5rem;
    margin: 0;
}
.stChatInputContainer textarea {
    background: var(--cyber-input-bg) !important;
    color: var(--cyber-text) !important;
    border: 1px solid var(--cyber-border-color) !important;
    border-radius: 8px !important;
    box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.37);
    font-size: 1.05em; padding: 10px 12px;
    font-family: var(--font-mono) !important;
}
.stChatInputContainer textarea:focus { border-color: var(--cyber-border-color-hover) !important; box-shadow: 0 0 12px color-mix(in srgb, var(--cyber-primary), transparent 75%); }
.stChatInputContainer ::placeholder { color: var(--cyber-primary) !important; opacity: 0.5 !important; }
/* Send button (might need adjustment based on Streamlit version) */
.stChatInputContainer button[kind="icon"] {
    background: var(--cyber-primary);
    border: 1px solid var(--cyber-primary);
    border-radius: 50%;
    fill: var(--cyber-bg) !important;
}
.stChatInputContainer button[kind="icon"]:hover { background: color-mix(in srgb, var(--cyber-primary), white 20%); }

/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: color-mix(in srgb, var(--cyber-input-bg), transparent 20%) !important;
    border: 1px dashed var(--cyber-border-color) !important; border-radius: 8px; padding: 12px; margin-top: 5px;
}
.stFileUploader label { color: color-mix(in srgb, var(--cyber-primary), transparent 30%) !important; font-size: 0.95em; }
.stFileUploader small { color: color-mix(in srgb, var(--cyber-primary), transparent 50%) !important; font-size: 0.8em; }
.stFileUploader button { display: none !important; } /* Oculta botão default */

/* --- Histórico de Chat (st.chat_message) --- */
    /* --- Histórico de Chat (st.chat_message) --- */
    .stChatMessage {
        /* Optional: Make base background very subtle or remove if setting below */
        background: rgba(16, 18, 37, 0.6); /* Example: Darker, slightly transparent base */
        border: 1px solid transparent;
        border-left: 3px solid; /* Color still set below */
        border-radius: 8px;
        margin-bottom: 1rem;
        padding: 0.75rem 1rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        gap: 0.75rem !important;
    }

    /* Mensagens do Usuário (Eli) */
    /* Target the container directly */
    .stChatMessage[data-testid="chatAvatarIcon-user"] {
        background: #251523; /* Example: Dark purple/magenta tint for user */
        border-left-color: var(--cyber-secondary); /* Keep the border color distinct */
    }
    .stChatMessage[data-testid="chatAvatarIcon-user"] .stMarkdown p,
    .stChatMessage[data-testid="chatAvatarIcon-user"] .stCodeBlock code { color: var(--cyber-text); }


    /* Mensagens do Assistente (Nash) */
    /* Target the container directly */
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] {
         background: #152523; /* Example: Dark teal/green tint for assistant */
         border-left-color: var(--cyber-primary); /* Keep the border color distinct */
    }
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] .stMarkdown p,
    .stChatMessage[data-testid="chatAvatarIcon-assistant"] .stCodeBlock code { color: var(--cyber-text); } /* Ajuste a cor se necessário */
/* Links */
.stChatMessage .stMarkdown a {
    color: var(--cyber-accent); text-decoration: underline; text-decoration-style: dashed; text-underline-offset: 3px;
}
.stChatMessage .stMarkdown a:hover { color: #ffffff; text-decoration-style: solid; }

/* --- Estilos para st.code dentro do chat --- */
.stCodeBlock {
    border: 1px solid var(--cyber-border-color); border-radius: 5px; background-color: var(--cyber-code-bg) !important; margin: 10px 0;
}
.stCodeBlock code {
    color: #e0e8ff; background-color: transparent !important; font-family: var(--font-mono);
    font-size: 0.95em; white-space: pre-wrap !important; word-wrap: break-word !important;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: #1f243d !important; border: 1px solid var(--cyber-border-color-hover) !important; color: #e0e8ff !important;
    opacity: 0.7; transition: opacity 0.3s ease; border-radius: 4px;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover {
    opacity: 1; background-color: #2a3050 !important; border-color: var(--cyber-primary) !important;
}

/* --- Status do Backend --- */
#backend-status {
    position: fixed; top: 10px; right: 15px; font-size: 0.85em; color: var(--cyber-secondary); font-family: var(--font-mono);
    background: rgba(15, 15, 25, 0.85); padding: 4px 10px; border-radius: 5px; border: 1px solid color-mix(in srgb, var(--cyber-secondary), transparent 75%); z-index: 1000;
    backdrop-filter: blur(3px);
}

/* --- Sidebar --- */
.stSidebar > div:first-child {
    background: linear-gradient(180deg, rgba(16, 18, 37, 0.94) 0%, rgba(24, 28, 48, 0.94) 100%);
    border-right: 1px solid color-mix(in srgb, var(--cyber-primary), transparent 80%);
    backdrop-filter: blur(5px); padding-top: 1rem;
}
.stSidebar .stMarkdown h3 {
    color: var(--cyber-secondary); text-shadow: 0 0 8px color-mix(in srgb, var(--cyber-secondary), transparent 70%); margin-top: 10px; margin-bottom: 4px; font-family: var(--font-display); font-size: 1.2em;
}
.stSidebar .stMarkdown, .stSidebar .stSelectbox label, .stSidebar .stCheckbox label { color: #c8d3ff; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stCheckbox {
    margin-bottom: 0.75rem;
}
.stSidebar .stButton { margin-top: 0.5rem; }
.nash-profile-details {
    font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #c8d3ff;
}
.stSelectbox > div { border-radius: 6px; border-color: var(--cyber-border-color); background-color: var(--cyber-input-bg); }
.stSelectbox div[data-baseweb="select"] > div { background-color: var(--cyber-input-bg); border-color: var(--cyber-border-color) !important; }
.stSelectbox div[role="listbox"] ul { background-color: var(--cyber-input-bg); }
.stSelectbox div[role="option"] { color: var(--cyber-text); }
.stSelectbox div[role="option"]:hover { background-color: #2a3050; }

/* --- Sinais Neon --- */
.sidebar-sign {
    font-family: var(--font-display); font-weight: bold; padding: 8px 15px; margin: 9px auto;
    border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: rgba(0, 0, 10, 0.5);
    border: 1px solid; letter-spacing: 1px; box-shadow: inset 0 0 10px rgba(0,0,0,0.6); user-select: none;
}
.sign-panic {
    color: var(--cyber-secondary); border-color: color-mix(in srgb, var(--cyber-secondary), transparent 60%); animation: blink-neon 1.5s infinite; font-size: 1.1em;
}
.sign-42 {
    color: var(--cyber-primary); border-color: color-mix(in srgb, var(--cyber-primary), transparent 60%); text-shadow: 0 0 6px var(--cyber-primary), 0 0 14px var(--cyber-primary), 0 0 20px var(--cyber-primary);
    font-size: 1.8em; padding: 5px 20px;
}

/* --- Indicador de Loading (usado com st.spinner) --- */
/* Estilização padrão do spinner é geralmente suficiente, mas pode ser customizada se necessário */
.stSpinner > div { border-top-color: var(--cyber-primary) !important; border-left-color: var(--cyber-primary) !important; } /* Cor do spinner */

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 14px; }
    #visor { flex-direction: column; align-items: center; gap: 15px; padding: 15px; text-align: center; }
    .nash-avatar-emoji { font-size: 3.5rem; margin-bottom: 10px; }
    .visor-content { align-items: center; } /* Centralizar texto no mobile */
    .nash-holo { font-size: 1.8em; }
    .nash-enterprise-tag { font-size: 0.8em; }
    .nash-ascii { font-size: 0.85em; line-height: 1.3; }
    .visor-analytics { font-size: 0.9em; padding: 0.3em 1em; text-align: left; } /* Manter stats alinhadas */
    .stChatMessage { padding: 0.5rem 0.75rem; margin-bottom: 0.75rem; }
    .stCodeBlock code { font-size: 0.9em; }
    #backend-status { font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }
    .stChatInputContainer { padding: 0.5rem 0.25rem; }
    .stChatInputContainer textarea { font-size: 1em; }
    .stSidebar > div:first-child { padding-top: 0.5rem; }
    .stSidebar .stMarkdown h3 { font-size: 1.1em; }
}
</style>
"""

# Tema Light Mode Refinado
LIGHT_MODE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400&family=Roboto:wght@400;700&display=swap');

/* --- Variáveis CSS --- */
:root {
    --light-bg: #f0f2f5;
    --light-text: #333333;
    --light-primary: #0d6efd; /* Azul Padrão Bootstrap */
    --light-secondary: #6c757d; /* Cinza Secundário */
    --light-accent: #d63384; /* Rosa/Magenta para Eli */
    --light-border-color: #d1d5db;
    --light-input-bg: #ffffff;
    --light-code-bg: #f8f9fa;
    --light-card-bg: #ffffff;
    --font-sans: 'Roboto', sans-serif;
    --font-mono: 'Fira Mono', 'Consolas', monospace;
}

/* --- Body e Geral --- */
body { background: var(--light-bg); color: var(--light-text) !important; font-family: var(--font-sans); min-height: 100vh !important; overflow-x: hidden; }

/* --- Área Principal --- */
.main > div { background: none !important; border: none !important; box-shadow: none !important; }

/* --- Visor --- */
#visor {
    background: linear-gradient(135deg, #eef2f7 80%, #d6e4f5 140%);
    border-radius: 10px; margin-bottom: 25px; border: 1px solid #c3daef;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), inset 0 0 10px rgba(0,0,0,0.03); padding: 18px 26px;
    display: flex; align-items: flex-start; gap: 20px;
}
.nash-avatar-emoji { font-size: 3.5rem; filter: none; line-height: 1; color: var(--light-primary); } /* Emoji com cor primária */
.visor-content { display: flex; flex-direction: column; }
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b { font-family: var(--font-sans); user-select: none; }
.nash-holo { font-size: 1.9em; color: var(--light-primary); text-shadow: none; margin-bottom: 2px; font-weight: bold; }
.nash-enterprise-tag { font-size: 0.9em; color: var(--light-secondary); }
.nash-ascii { font-family: var(--font-mono); color: #555; letter-spacing: 0; line-height: 1.3; font-size: 0.9em; text-shadow: none; margin-top: 10px; margin-bottom: 10px; white-space: pre; }
.nash-ascii b { color: var(--light-primary); font-weight: bold; }
.visor-analytics {
    color: #4a5568; font-size: 0.9em; padding: 0.5em 1.1em; background: #e9ecef;
    border-radius: 6px; border: 1px solid #ced4da; margin-top: 12px; line-height: 1.5;
}
.visor-analytics b { color: #111; }
.visor-analytics i { color: #6c757d; opacity: 1; }

/* --- Botões --- */
.stButton > button {
    color: #ffffff; background: var(--light-primary); border-radius: 6px; border: 1px solid var(--light-primary);
    font-weight: normal; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1); padding: 0.4rem 0.8rem; font-family: var(--font-sans);
}
.stButton > button:hover { background: #0b5ed7; border-color: #0a58ca; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #ffffff; }
.stButton > button:active { background: #0a58ca; }
.stButton > button:disabled { background: #ced4da; color: #6c757d; border-color: #ced4da; cursor: not-allowed; }
.stButton.clear-button > button { background: #dc3545; border-color: #dc3545; color: #fff; }
.stButton.clear-button > button:hover { background: #bb2d3b; border-color: #b02a37; }

/* --- Área de Input (st.chat_input) --- */
.stChatInputContainer {
    background: #ffffff;
    border-top: 1px solid var(--light-border-color);
    padding: 1rem 0.5rem; margin: 0;
    box-shadow: 0 -1px 5px rgba(0,0,0,0.05);
}
.stChatInputContainer textarea {
    background: var(--light-input-bg) !important; color: var(--light-text) !important; border: 1px solid #ced4da !important;
    border-radius: 6px !important; box-shadow: inset 0 1px 2px rgba(0,0,0,0.075); font-size: 1em; padding: 8px 10px;
    font-family: var(--font-sans) !important;
}
.stChatInputContainer textarea:focus { border-color: #86b7fe !important; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); }
.stChatInputContainer ::placeholder { color: #6c757d !important; opacity: 1 !important; }
.stChatInputContainer button[kind="icon"] {
    background: var(--light-primary);
    border: 1px solid var(--light-primary);
    border-radius: 50%;
    fill: #ffffff !important;
}
.stChatInputContainer button[kind="icon"]:hover { background: #0b5ed7; }


/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: #f8f9fa !important; border: 1px dashed #ced4da !important; border-radius: 6px; padding: 12px; margin-top: 5px;
}
.stFileUploader label { color: var(--light-primary) !important; font-size: 0.95em; }
.stFileUploader small { color: #6c757d !important; font-size: 0.8em; }

/* --- Histórico de Chat (st.chat_message) --- */
.stChatMessage {
    background: var(--light-card-bg);
    border: 1px solid var(--light-border-color);
    border-left: 4px solid; /* Será colorida por role */
    border-radius: 8px;
    margin-bottom: 1rem;
    padding: 0.8rem 1.1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    gap: 1rem !important;
}
/* Mensagens do Usuário (Eli) */
.stChatMessage[data-testid="chatAvatarIcon-user"] + div { border-left-color: var(--light-accent); }
.stChatMessage[data-testid="chatAvatarIcon-user"] .stMarkdown p,
.stChatMessage[data-testid="chatAvatarIcon-user"] .stCodeBlock code { color: var(--light-text); }
/* Mensagens do Assistente (Nash) */
.stChatMessage[data-testid="chatAvatarIcon-assistant"] + div { border-left-color: var(--light-primary); }
.stChatMessage[data-testid="chatAvatarIcon-assistant"] .stMarkdown p,
.stChatMessage[data-testid="chatAvatarIcon-assistant"] .stCodeBlock code { color: var(--light-text); }
/* Links */
.stChatMessage .stMarkdown a { color: var(--light-primary); text-decoration: underline; }
.stChatMessage .stMarkdown a:hover { color: #0a58ca; }

/* --- Estilos para st.code dentro do chat --- */
.stCodeBlock {
    border: 1px solid #dee2e6; border-radius: 5px; background-color: var(--light-code-bg) !important; margin: 10px 0;
}
.stCodeBlock code {
    color: #212529; background-color: transparent !important; font-family: var(--font-mono);
    font-size: 0.9em; white-space: pre-wrap !important; word-wrap: break-word !important;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: #e9ecef !important; border: 1px solid #ced4da !important; color: #495057 !important;
    opacity: 0.8; transition: opacity 0.3s ease; border-radius: 4px;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover { opacity: 1; background-color: #ced4da !important; }

/* --- Status do Backend --- */
#backend-status {
    position: fixed; top: 10px; right: 15px; font-size: 0.9em; color: #495057; font-family: var(--font-sans);
    background: rgba(255, 255, 255, 0.9); padding: 4px 10px; border-radius: 5px; border: 1px solid #dee2e6; z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1); backdrop-filter: blur(3px);
}

/* --- Sidebar --- */
.stSidebar > div:first-child {
    background: #ffffff; border-right: 1px solid #dee2e6; padding-top: 1rem;
}
.stSidebar .stMarkdown h3 {
    color: var(--light-primary); text-shadow: none; margin-top: 10px; margin-bottom: 4px; font-size: 1.2em; font-weight: bold;
}
.stSidebar .stMarkdown, .stSidebar .stSelectbox label, .stSidebar .stCheckbox label { color: #495057; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stCheckbox {
     margin-bottom: 0.8rem;
}
.stSidebar .stButton { margin-top: 0.5rem; }
.nash-profile-details { font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #495057; }
.stSelectbox > div { border-radius: 6px; border-color: #ced4da; background-color: var(--light-input-bg); }
.stSelectbox div[data-baseweb="select"] > div { background-color: var(--light-input-bg); border-color: #ced4da !important; }
.stSelectbox div[role="listbox"] ul { background-color: var(--light-input-bg); }
.stSelectbox div[role="option"] { color: var(--light-text); }
.stSelectbox div[role="option"]:hover { background-color: #e9ecef; }

/* --- Sinais (Sidebar) --- */
.sidebar-sign {
     font-family: var(--font-sans); font-weight: bold; padding: 6px 12px; margin: 9px auto;
     border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: #e9ecef;
     border: 1px solid #ced4da; letter-spacing: 0.5px; box-shadow: none; user-select: none;
     animation: none !important; text-shadow: none !important;
}
.sign-panic { color: #dc3545; border-color: #f1ae B5; background-color: #f8d7da; font-size: 1em; } /* Alerta mais visível */
.sign-42 { color: #198754; border-color: #a3cfbb; background-color: #d1e7dd; font-size: 1.5em; padding: 4px 15px; } /* Verde mais visível */


/* --- Indicador de Loading (st.spinner) --- */
.stSpinner > div { border-top-color: var(--light-primary) !important; border-left-color: var(--light-primary) !important; } /* Cor do spinner */

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 15px; }
    #visor { flex-direction: column; align-items: center; gap: 10px; padding: 15px; text-align: center; }
    .nash-avatar-emoji { font-size: 3rem; margin-bottom: 5px; }
    .visor-content { align-items: center; }
    .nash-holo { font-size: 1.6em; }
    .nash-enterprise-tag { font-size: 0.85em; }
    .nash-ascii { font-size: 0.8em; line-height: 1.3; }
    .visor-analytics { font-size: 0.85em; }
    .stChatMessage { padding: 0.6rem 0.8rem; margin-bottom: 0.75rem; }
    .stCodeBlock code { font-size: 0.85em; }
    #backend-status { font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }
    .stChatInputContainer { padding: 0.5rem 0.25rem; }
    .stChatInputContainer textarea { font-size: 0.95em; }
    .stSidebar > div:first-child { padding-top: 0.5rem; }
    .stSidebar .stMarkdown h3 { font-size: 1.1em; }
}
</style>
"""

THEMES = {
    "Cyberpunk": CYBERPUNK_CSS,
    "Light Mode": LIGHT_MODE_CSS,
}

# --- Funções Auxiliares ---

def check_backend_status(force_check=False):
    """Verifica o status do backend com cache simples."""
    now = datetime.now()
    if not force_check and st.session_state.get("last_backend_check") and \
       (now - st.session_state.last_backend_check) < timedelta(seconds=60):
        return st.session_state.backend_status

    status = "VERIFICANDO..."
    status_code = None
    try:
        # Usar um endpoint leve como /pingnet se disponível, senão /
        ping_url = f"{BACKEND_URL}/pingnet"
        try:
            r = requests.get(ping_url, timeout=REQUEST_TIMEOUT[0])
            status_code = r.status_code
        except requests.exceptions.RequestException:
            # Tentar o endpoint raiz como fallback
            r = requests.get(BACKEND_URL, timeout=REQUEST_TIMEOUT[0])
            status_code = r.status_code

        if status_code == 200:
            status = "ONLINE ⚡"
        else:
            status = f"AVISO {status_code} <0xF0><0x9F><0xAA><0x96>" # Código com erro + ícone robô
    except requests.exceptions.Timeout:
        status = "TIMEOUT ⏳"
    except requests.exceptions.ConnectionError:
        status = "OFFLINE 👾"
    except Exception as e:
        print(f"Erro inesperado ao checar backend: {e}")
        status = "ERRO ⁉️"

    st.session_state.backend_status = status
    st.session_state.last_backend_check = now
    return status

def escape_html_tags(text: str) -> str:
    """Escapa caracteres HTML para exibição segura."""
    if not isinstance(text, str):
        text = str(text)
    return html.escape(text, quote=True)

def scroll_to_bottom_js():
    """Retorna código JS para rolar a janela para o fim."""
    # Este JS tenta rolar o contêiner principal do Streamlit. Pode precisar de ajuste.
    js = """
    <script>
        function scrollToBottom() {
            const mainContainer = window.parent.document.querySelector('.main > div');
            if (mainContainer) {
                // Use scrollIntoView on a dummy element at the end if direct scrollHeight doesn't work well
                // let scrollTarget = window.parent.document.getElementById('scroll-target');
                // if (!scrollTarget) {
                //     scrollTarget = window.parent.document.createElement('div');
                //     scrollTarget.id = 'scroll-target';
                //     mainContainer.appendChild(scrollTarget);
                // }
                // scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'end' });

                // Simpler approach: Scroll the window itself
                 window.parent.document.documentElement.scrollTop = window.parent.document.documentElement.scrollHeight;
            }
        }
        // Run after a short delay to allow elements to render
        // setTimeout(scrollToBottom, 150); // Ajuste o delay se necessário
        // Run immediately - Streamlit reruns might handle timing adequately
        scrollToBottom();
    </script>
    """
    return js

def apply_theme():
    """Aplica o CSS do tema selecionado."""
    theme_name = st.session_state.get("selected_theme", "Cyberpunk")
    css = THEMES.get(theme_name, CYBERPUNK_CSS)
    st.markdown(css, unsafe_allow_html=True)

# --- Inicialização do Estado da Sessão ---
def init_session_state():
    """Inicializa as variáveis do estado da sessão se não existirem."""
    defaults = {
        "start_time": datetime.now(),
        "history": [], # Renomeado de nash_history para simplicidade
        "eli_msg_count": 0,
        "nash_msg_count": 0,
        "is_authenticated": False, # Renomeado de ok
        "backend_status": "N/A",
        "last_backend_check": None,
        "waiting_for_nash": False,
        "uploaded_file_info": None, # Guarda dict {'name': ..., 'type': ...}
        "selected_theme": "Cyberpunk",
        "login_error": None,
        "auto_scroll": True # Nova opção
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# --- Renderização do Visor ---
def render_visor():
    """Renderiza o componente do visor superior."""
    status = check_backend_status()
    uptime_delta = datetime.now() - st.session_state.start_time
    uptime_str = str(timedelta(seconds=int(uptime_delta.total_seconds())))
    theme_name = st.session_state.selected_theme
    avatar_emoji = "👨‍🚀"

    # ASCII art sutil, adaptado para clareza
    ascii_art = f"""
Nash Core Systems::..
----------------------
Status   : {('OPERATIONAL' if status.startswith('ONLINE') else 'DEGRADED') if st.session_state.is_authenticated else 'LOCKED'}
Logic    : ACTIVE
Auth     : {'GRANTED' if st.session_state.is_authenticated else 'PENDING'}
Session  : {uptime_str}
    """.strip()
    safe_ascii_art = escape_html_tags(ascii_art)

    motivations = [
        "Ready to interface, Commander.", "Calculating optimal sarcasm levels...",
        "Just compiling the meaning of life. Be right back.", "Remember: I run on caffeine and pure logic.",
        "Engaging neural net... Stand by for brilliance (or bugs).", "Let's make some digital waves.",
        "Probability of awesome: High.", "Query received. Processing..."
    ]
    random_motivation = escape_html_tags(random.choice(motivations))

    visor_html = f"""
    <div id="visor">
        <span class="nash-avatar-emoji">{avatar_emoji}</span>
        <div class="visor-content">
            <span class="nash-holo">Nash Copilot</span>
            <span class="nash-enterprise-tag">:: Eli Digital Command Interface</span>
            <div class="nash-ascii">{safe_ascii_art}</div>
            <div class="visor-analytics" title="Session Statistics">
                Cmds: <b>{st.session_state.eli_msg_count}</b> | Resps: <b>{st.session_state.nash_msg_count}</b><br>
                <i>"{random_motivation}"</i>
            </div>
        </div>
    </div>
    """
    st.markdown(visor_html, unsafe_allow_html=True)

# --- Lógica de Login ---
def handle_login():
    """Gerencia a tela e o processo de login."""
    st.markdown("### Authorization Required")
    if st.session_state.login_error:
        st.error(st.session_state.login_error)

    password = st.text_input(
        "Enter Command Authorization Code:",
        type="password",
        key="login_password_input",
        label_visibility="collapsed",
        placeholder="Authorization Code..."
    )

    if st.button("Authenticate 🛰️", key="login_button", use_container_width=True, disabled=st.session_state.waiting_for_nash):
        if not password:
            st.session_state.login_error = "Authorization code cannot be empty."
            st.rerun()

        st.session_state.waiting_for_nash = True
        st.session_state.login_error = None # Clear previous error
        st.rerun() # Rerun to show spinner and process

    # Process login attempt after rerun
    if st.session_state.waiting_for_nash and not st.session_state.is_authenticated:
        login_success = False
        try:
            with st.spinner("Authenticating with Mothership..."):
                r = requests.post(f"{BACKEND_URL}/login", json={"password": password}, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200 and r.json().get("success"):
                    st.session_state.is_authenticated = True
                    login_success = True
                    st.session_state.login_error = None
                    st.toast("Authentication Successful! Protocols unlocked.", icon="✅")
                    # Não precisa de st.balloons() em interface clean ;)
                else:
                    error_msg = r.json().get("msg", f"Authentication Failed (Status: {r.status_code})")
                    st.session_state.login_error = escape_html_tags(error_msg)

        except requests.exceptions.RequestException as e:
            st.session_state.login_error = f"Network error during authentication: {e}"
        except Exception as e:
            st.session_state.login_error = f"Unexpected error during authentication: {e}"
        finally:
            st.session_state.waiting_for_nash = False
            if login_success:
                # Limpar senha do widget após sucesso (requer rerun)
                # A forma mais segura é usar st.empty() e reconstruir a UI, mas rerun funciona
                time.sleep(0.5) # Pequena pausa
                st.rerun()
            else:
                st.rerun() # Rerun para mostrar erro

    # Se não autenticado, parar aqui
    if not st.session_state.is_authenticated:
        st.stop()

# --- Lógica de Upload ---
def handle_file_upload(upload_status_placeholder):
    """Gerencia o upload de arquivos na sidebar."""
    uploaded_file = st.file_uploader(
        "📎 Attach Data Link (Optional)",
        type=[ "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg", # Imagens
               "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml", # Texto/Código
               "mp3", "wav", "ogg", "mp4", "mov", "avi"], # Mídia (se backend suportar)
        key="file_uploader_widget",
        label_visibility="visible",
        help="Upload a file for Nash to analyze with your next command."
    )

    if uploaded_file is not None:
        # Verificar se é um arquivo novo para evitar re-upload desnecessário
        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        previous_file_id = st.session_state.get("uploaded_file_id")

        if current_file_id != previous_file_id:
            st.session_state.uploaded_file_info = None # Resetar info antiga
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                with upload_status_placeholder, st.spinner(f"Transmitting '{escape_html_tags(uploaded_file.name)}'..."):
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT) # Timeout maior para uploads

                if r.status_code == 200:
                    # Armazenar info do arquivo no estado para anexar ao próximo prompt
                    st.session_state.uploaded_file_info = {
                        "name": uploaded_file.name,
                        "type": uploaded_file.type,
                        "backend_ref": r.json().get("filename") # Referência do backend se houver
                    }
                    st.session_state.uploaded_file_id = current_file_id # Marcar como enviado
                    upload_status_placeholder.success(f"🛰️ '{escape_html_tags(uploaded_file.name)}' linked!")
                else:
                    upload_status_placeholder.error(f"Upload Failed ({r.status_code}): {escape_html_tags(r.text)}")
                    st.session_state.uploaded_file_info = None
                    st.session_state.uploaded_file_id = None

            except requests.exceptions.Timeout:
                upload_status_placeholder.error("Upload Timeout. File may be too large or network unstable.")
                st.session_state.uploaded_file_info = None
                st.session_state.uploaded_file_id = None
            except requests.exceptions.RequestException as e:
                 upload_status_placeholder.error(f"Network Error during upload: {e}")
                 st.session_state.uploaded_file_info = None
                 st.session_state.uploaded_file_id = None
            except Exception as e:
                upload_status_placeholder.error(f"Unexpected upload error: {e}")
                st.session_state.uploaded_file_info = None
                st.session_state.uploaded_file_id = None
        # else: # Mesmo arquivo, já foi processado
             # upload_status_placeholder.info(f"📎 Ready: `{escape_html_tags(uploaded_file.name)}`")

    elif uploaded_file is None and st.session_state.uploaded_file_info:
        # Se o uploader foi limpo pelo usuário, limpar o estado
        st.session_state.uploaded_file_info = None
        st.session_state.uploaded_file_id = None
        # upload_status_placeholder.empty() # Descomente se quiser limpar a msg de sucesso/info

    # Mostrar info do arquivo pronto para ser anexado
    if st.session_state.uploaded_file_info:
         upload_status_placeholder.info(f"📎 Linked: `{escape_html_tags(st.session_state.uploaded_file_info['name'])}`")

# --- Renderização da Sidebar ---
def render_sidebar():
    """Renderiza a sidebar com controles e informações."""
    with st.sidebar:
        st.markdown("### 🎨 Interface Theme")
        theme_options = list(THEMES.keys())
        current_theme_index = theme_options.index(st.session_state.selected_theme) if st.session_state.selected_theme in theme_options else 0
        selected_theme_name = st.selectbox(
            "Select UI Theme:",
            options=theme_options,
            key="selected_theme_widget",
            index=current_theme_index,
            label_visibility="collapsed"
        )
        if selected_theme_name != st.session_state.selected_theme:
             st.session_state.selected_theme = selected_theme_name
             st.rerun()
        add_vertical_space(1)

        st.markdown("### ✨ Cockpit Signals")
        st.markdown(f"""<div class="sidebar-sign sign-panic" title="Visual Reminder">{SIGN_PANIC_TEXT}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="sidebar-sign sign-42" title="The Answer.">{SIGN_42_TEXT}</div>""", unsafe_allow_html=True)
        add_vertical_space(1)

        st.markdown("### 📡 Data Uplink")
        upload_status_placeholder = st.empty() # Placeholder para mensagens de status do upload
        handle_file_upload(upload_status_placeholder)
        add_vertical_space(1)


        st.markdown("### ⚙️ Controls")
        st.checkbox("Auto-Scroll Chat", key="auto_scroll", help="Automatically scroll to the latest message.")
        add_vertical_space(1)

        if st.button("🗑️ Clear Session Log", key="clear_chat_btn", help="Delete all messages from this session.", use_container_width=True, type="secondary"):
             st.session_state.history = []
             st.session_state.eli_msg_count = 0
             st.session_state.nash_msg_count = 0
             st.session_state.uploaded_file_info = None # Limpar info de arquivo
             st.session_state.uploaded_file_id = None
             st.toast("🧹 Session log cleared!", icon="✨")
             time.sleep(0.5) # Pequena pausa para toast
             st.rerun()
        add_vertical_space(2)

        st.markdown("### 🧠 Nash Core Profile")
        status = st.session_state.backend_status
        profile_html = f"""
        <div class="nash-profile-details">
            Designation: <b>Nash</b><br>
            Class: Digital Copilot AI<br>
            Memory: Vectorized (Pinecone)<br>
            Backend: <span title="Last check: {st.session_state.last_backend_check}">{status}</span><br>
            Authentication: <b>{'GRANTED' if st.session_state.is_authenticated else 'REQUIRED'}</b>
        </div>
        """
        st.markdown(profile_html, unsafe_allow_html=True)

# --- Renderização do Histórico ---
def render_history(chat_container):
    """Renderiza o histórico de mensagens no container fornecido."""
    with chat_container:
        if not st.session_state.history:
             st.markdown("> *Command console awaiting input... Engage when ready.*")
             return # Sai se não há histórico

        for i, message in enumerate(st.session_state.history):
            role = message["role"] # "user" or "assistant"
            content = message["content"]
            avatar = "🧑‍🚀" if role == "user" else "👨‍🚀" # Eli | Nash
            with st.chat_message(role, avatar=avatar):
                # Renderiza o conteúdo como Markdown (Streamlit lida com code blocks etc.)
                st.markdown(content, unsafe_allow_html=False) # False é mais seguro

    # Aplica auto-scroll se habilitado e não estiver esperando resposta
    if st.session_state.auto_scroll and not st.session_state.waiting_for_nash:
        st.components.v1.html(scroll_to_bottom_js(), height=0, scrolling=False)


# --- Envio de Prompt e Comunicação com Backend ---
def handle_chat_input(prompt: str):
    """Processa o input do usuário, envia ao backend e atualiza o histórico."""
    if not prompt:
        return # Não faz nada se o prompt estiver vazio

    # Adiciona mensagem do usuário ao histórico
    st.session_state.history.append({"role": "user", "content": prompt})
    st.session_state.eli_msg_count += 1

    # Prepara payload para backend
    payload = {"prompt": prompt, "session_id": "eli"} # Usando "eli" como ID fixo por enquanto

    # Anexa informação do arquivo se houver
    if st.session_state.uploaded_file_info:
        # Enviar apenas metadados; backend já deve ter o arquivo pelo /upload
        payload["attachment_info"] = {
            "filename": st.session_state.uploaded_file_info["name"],
            "type": st.session_state.uploaded_file_info["type"]
        }
        # Limpa info do arquivo após anexar ao prompt (para não anexar de novo)
        st.session_state.uploaded_file_info = None
        st.session_state.uploaded_file_id = None


    # Marca que está esperando e reroda para mostrar mensagem do usuário + spinner
    st.session_state.waiting_for_nash = True
    st.rerun()

# --- Lógica Principal pós-rerun para buscar resposta ---
def fetch_nash_response():
    """Chamado após rerun se waiting_for_nash for True. Busca resposta do backend."""
    if not st.session_state.waiting_for_nash:
        return # Só executa se estiver esperando

    last_user_message = next((msg for msg in reversed(st.session_state.history) if msg["role"] == "user"), None)
    if not last_user_message:
        st.session_state.waiting_for_nash = False
        return # Não deveria acontecer, mas evita erro

    # Reconstruir payload (importante se o state foi modificado)
    payload = {"prompt": last_user_message["content"], "session_id": "eli"}
    # A informação do anexo já foi limpa, então não precisa reenviar aqui.

    response_content = ""
    try:
        # Exibe spinner DENTRO da mensagem de "pensando" do Nash
        with st.chat_message("assistant", avatar="👨‍🚀"):
            with st.spinner("Nash is processing..."):
                req = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=REQUEST_TIMEOUT)

                if req.status_code == 200:
                    response_content = req.json().get("response", "[Nash returned an empty response.]")
                    st.session_state.nash_msg_count += 1
                else:
                    try: error_payload = req.json().get("error", req.text)
                    except ValueError: error_payload = req.text
                    response_content = f"**[Backend Error {req.status_code}]**\n```\n{escape_html_tags(str(error_payload)[:200])}\n```" # Limita tamanho
                    st.session_state.nash_msg_count += 1 # Conta erro como resposta

    except requests.exceptions.Timeout:
        response_content = "[Request Timeout] Nash took too long to respond. Try again later."
        st.session_state.nash_msg_count += 1
    except requests.exceptions.RequestException as e:
        response_content = f"[Network Error] Could not reach Nash's core.\n```\n{escape_html_tags(str(e))}\n```"
        st.session_state.nash_msg_count += 1
    except Exception as e:
        response_content = f"[Client Error] An unexpected issue occurred.\n```\n{escape_html_tags(str(e))}\n```"
        st.session_state.nash_msg_count += 1
    finally:
        st.session_state.history.append({"role": "assistant", "content": response_content})
        st.session_state.waiting_for_nash = False
        # Rerun final para exibir a resposta do Nash
        st.rerun()


# --- Função Principal da Aplicação ---
def main():
    st.set_page_config(page_title="Nash Copilot", page_icon="👨‍🚀", layout="wide")
    init_session_state()
    apply_theme()

    # Status flutuante (atualizado no início)
    current_backend_status = check_backend_status()
    st.markdown(f"<div id='backend-status' title='Nash Backend Status'>Backend: {current_backend_status}</div>", unsafe_allow_html=True)

    # Renderiza Sidebar
    render_sidebar()

    # Lógica de Autenticação
    if not st.session_state.is_authenticated:
        handle_login()
        st.stop() # Para aqui se não autenticado

    # Área Principal (Visor + Chat)
    render_visor()

    # Container para o histórico de chat
    chat_container = st.container()
    render_history(chat_container) # Renderiza o histórico atual

    # Input de Chat (Usando st.chat_input)
    if prompt := st.chat_input("Enter command for Nash...", key="chat_input_widget", disabled=st.session_state.waiting_for_nash):
        handle_chat_input(prompt)

    # Se estiver esperando resposta do Nash, chama a função para buscar
    if st.session_state.waiting_for_nash:
        fetch_nash_response()

# --- Execução ---
if __name__ == "__main__":
    main()

# --- END OF FILE nash_ui.py (Refatorado) ---