import streamlit as st
import requests, time, random, re, html   # ← acrescentamos “html”
from datetime import datetime, timedelta

# --- Constantes ---
BACKEND_URL = "https://nashcopilot-production.up.railway.app"
REQUEST_TIMEOUT = (5, 65) # (connect timeout, read timeout)

# --- Textos Customizáveis para os Sinais (Mantido) ---
sign_panic_text = "NÃO ENTRE EM PÂNICO"
sign_42_text = "42"
# ------------------------------------------

# --- Definições de Temas CSS ---

# Tema Padrão (Cyberpunk)
CYBERPUNK_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

/* --- Animações --- */
@keyframes blink-neon {
  0%, 100% { opacity: 1; text-shadow: 0 0 7px #ff07e6, 0 0 15px #ff07e6, 0 0 20px #ff07e6; }
  50% { opacity: 0.7; text-shadow: 0 0 5px #ff07e6a0, 0 0 10px #ff07e6a0; }
}
@keyframes subtle-pulse {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 1; }
}
@keyframes scanline {
  0% { background-position: 0 0; }
  100% { background-position: 0 100%; }
}
@keyframes thinking-pulse {
    0% { background-color: #0affa030; box-shadow: 0 0 8px #0affa030; }
    50% { background-color: #0affa060; box-shadow: 0 0 15px #0affa070; }
    100% { background-color: #0affa030; box-shadow: 0 0 8px #0affa030; }
}
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Body e Geral --- */
body {
    background: radial-gradient(ellipse at center, #10121f 0%, #0b0c14 70%), linear-gradient(145deg, #0b0c14 70%, #181a29 100%);
    background-attachment: fixed;
    color: #d0d8ff !important;
    font-family: 'Fira Mono', 'Consolas', monospace;
    min-height: 100vh !important;
    overflow-x: hidden;
}
body:before {
    content: ''; background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
    opacity: .1; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
    pointer-events: none; background-size: cover;
}

/* --- Área Principal --- */
section.main > div {
    background: linear-gradient(170deg, #0f111a 0%, #1c202f 100%) !important;
    border-radius: 15px; border: 1px solid #0aebff30;
    box-shadow: 0 0 25px #0aebff10, inset 0 0 20px rgba(0,0,0,0.5);
    margin-bottom: 2rem;
}

/* --- Visor Holográfico --- */
#visor {
    background: linear-gradient(135deg, rgba(16, 18, 37, 0.97) 80%, rgba(255, 7, 230, 0.85) 140%), rgba(5, 5, 15, 0.96);
    border-radius: 15px; margin-bottom: 20px; margin-top: -10px; border: 2.5px solid #ff07e660;
    box-shadow: 0 0 30px #e600c650, inset 0 0 15px #101225e0; padding: 18px 26px 14px 30px;
    display: flex; align-items: center; gap: 25px;
}
.nash-avatar-emoji {
    font-size: 65px; filter: drop-shadow(0 0 15px #0affa0a0); margin-right: 15px; line-height: 1; animation: subtle-pulse 3s infinite ease-in-out;
}
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b {
    font-family: 'Orbitron', 'Fira Mono', monospace; user-select: none;
}
.nash-holo { font-size: 2.1em; color: #0affa0; text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; margin-bottom: 3px; }
.nash-enterprise-tag { font-size: 0.9em; color: #ff07e6b0; font-family: 'Fira Mono', monospace; }
.nash-ascii { font-family: 'Fira Mono', monospace; color: #0affa0d0; letter-spacing: 0.5px; line-height: 115%; font-size: 0.95em; text-shadow: 0 0 8px #0affa040; margin-top: -5px; margin-bottom: 5px; }
.nash-ascii b { color: #ff07e6; font-weight: bold; }
.visor-analytics {
    color:#ff07e6; font-size: 0.95em; padding: 0.4em 1.3em; background: rgba(10, 10, 25, 0.75);
    border-radius: 8px; border: 1px solid #ff07e650; margin-top: 10px; line-height: 1.45;
}
.visor-analytics b { color: #ffffff; }
.visor-analytics i { color: #c8d3ff; opacity: 0.85; }

/* --- Botões --- */
.stButton>button {
    color: #e0e8ff; background: #1f243d; border-radius: 8px; border: 2px solid #0affa070;
    font-weight: bold; transition: all 0.3s ease; box-shadow: 0 0 10px #0affa020; padding: 0.4rem 0.8rem;
}
.stButton>button:hover { background: #2a3050; border-color: #0affa0; box-shadow: 0 0 18px #0affa060; color: #ffffff; }
.stButton>button:active { background: #15182a; }
.stButton.clear-button>button { border-color: #ff07e670; color: #ffc0e8; box-shadow: 0 0 10px #ff07e620; }
.stButton.clear-button>button:hover { border-color: #ff07e6; background: #3d1f35; box-shadow: 0 0 18px #ff07e660; color: #ffffff; }

/* --- Área de Input --- */
.stTextArea textarea {
    background: #101225 !important; color: #d8e0ff !important; border: 1px solid #0affa040 !important;
    border-radius: 5px !important; box-shadow: inset 0 0 10px #00000060; font-size: 1.05em; padding: 10px 12px;
}
.stTextArea textarea:focus { border-color: #0affa0 !important; box-shadow: 0 0 12px #0affa040; }
::-webkit-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
::-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-ms-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }

/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: #101225cc !important; border: 1px dashed #0affa050 !important; border-radius: 8px; padding: 12px; margin-top: 5px;
}
.stFileUploader label { color: #0affa0b0 !important; font-size: 0.95em; }
.stFileUploader small { color: #0affa070 !important; font-size: 0.8em; }
.stFileUploader button { display: none !important; }

/* --- Histórico de Chat --- */
#nash-history {
    background: #0c0e1acc; border-radius: 10px; padding: 18px 16px 8px 15px; margin-top: 25px;
    border: 1px solid #0affa030;
    background-image: repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(0, 255, 255, 0.02) 5px, rgba(0, 255, 255, 0.02) 6px, transparent 7px, transparent 10px), repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.01) 0px, rgba(255, 255, 255, 0.02) 1px, transparent 1px, transparent 8px);
    box-shadow: inset 0 0 15px #000000a0, 0 0 15px #0aebff10;
}
#nash-history h3 {
    color: #ff07e6; text-shadow: 0 0 10px #ff07e670; border-bottom: 1px solid #ff07e640; padding-bottom: 5px; margin-bottom: 18px;
}

/* --- Avatares e Mensagens no Chat --- */
.avatar-nash, .avatar-eli {
    font-weight:bold; filter: drop-shadow(0 0 6px); display: block; margin-bottom: 4px;
    font-size: 0.9em; /* Ajuste para nome não ficar tão grande */
}
.avatar-nash { color:#0affa0; }
.avatar-eli { color:#ff07e6; }
.message-nash {
    color: #b0e0e6; border-left: 3px solid #0affa070;
    display: inline-block; padding: 5px 10px; border-radius: 5px; background-color: rgba(255, 255, 255, 0.04);
    margin-top: 0; line-height: 1.5; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
.message-eli {
    color: #ffc0e8; border-left: 3px solid #ff07e670;
    display: inline-block; padding: 5px 10px; border-radius: 5px; background-color: rgba(255, 255, 255, 0.04);
    margin-top: 0; line-height: 1.5; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
.message-nash a, .message-eli a {
    color: #87cefa; text-decoration: underline; text-decoration-style: dashed; text-underline-offset: 3px;
}
.message-nash a:hover, .message-eli a:hover { color: #ffffff; text-decoration-style: solid; }

/* --- Estilos para st.code --- */
.stCodeBlock {
    border: 1px solid #0affa050; border-radius: 5px; background-color: rgba(10, 12, 25, 0.8) !important; margin: 10px 0;
}
.stCodeBlock code {
    color: #e0e8ff; background-color: transparent !important; font-family: 'Fira Mono', monospace;
    font-size: 0.95em; white-space: pre-wrap !important; word-wrap: break-word !important;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: #1f243d !important; border: 1px solid #0affa070 !important; color: #e0e8ff !important;
    opacity: 0.7; transition: opacity 0.3s ease;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover {
    opacity: 1; background-color: #2a3050 !important; border-color: #0affa0 !important;
}

#nash-history hr { margin: 15px 0; border: none; border-top: 1px solid #ffffff15; }

/* --- Status do Backend --- */
#backend-status {
    position: fixed; top: 10px; right: 15px; font-size: 0.9em; color: #ff07e6; font-family: 'Fira Mono', monospace;
    background: rgba(15, 15, 25, 0.85); padding: 4px 10px; border-radius: 5px; border: 1px solid #ff07e640; z-index: 1000;
}

/* --- Sidebar --- */
.stSidebar > div:first-child {
    background: linear-gradient(180deg, #101225f0 0%, #181c30f0 100%); border-right: 1px solid #0affa020; backdrop-filter: blur(5px);
}
.stSidebar .stMarkdown h3 {
    color: #ff07e6; text-shadow: 0 0 8px #ff07e650; margin-top: 10px; margin-bottom: 4px;
}
.stSidebar .stMarkdown { color: #c8d3ff; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox {
    margin-bottom: 0.8rem;
}
.stSidebar .stButton { margin-top: 0.5rem; }
.nash-profile-details {
    font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #c8d3ff;
}

/* --- Sinais Neon --- */
.sidebar-sign {
    font-family: 'Orbitron', 'Fira Mono', monospace; font-weight: bold; padding: 8px 15px; margin: 15px auto;
    border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: rgba(0, 0, 10, 0.5);
    border: 1px solid; letter-spacing: 1px; box-shadow: inset 0 0 10px rgba(0,0,0,0.6);
}
.sign-panic {
    color: #ff07e6; border-color: #ff07e660; animation: blink-neon 1.5s infinite; font-size: 1.1em;
}
.sign-42 {
    color: #0affa0; border-color: #0affa060; text-shadow: 0 0 6px #0affa0, 0 0 14px #0affa0, 0 0 20px #0affa0;
    font-size: 1.8em; padding: 5px 20px;
}

/* --- Indicador de Loading --- */
.loading-indicator {
    display: flex; align-items: center; justify-content: center; padding: 10px; margin-top: 10px; border-radius: 5px;
    background-color: #0affa030; border: 1px solid #0affa050; color: #e0ffff; font-family: 'Fira Mono', monospace;
    box-shadow: 0 0 8px #0affa030; animation: thinking-pulse 1.5s infinite ease-in-out;
}
.loading-indicator::before {
    content: '🧠'; margin-right: 10px; font-size: 1.2em; animation: spin 2s linear infinite;
}

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 14px; }
    #visor { flex-direction: column; align-items: flex-start; gap: 15px; padding: 15px; }
    .nash-avatar-emoji { font-size: 50px; margin-right: 0; margin-bottom: 10px; }
    .nash-holo { font-size: 1.8em; }
    .nash-enterprise-tag { font-size: 0.8em; }
    .nash-ascii { font-size: 0.85em; }
    .visor-analytics { font-size: 0.9em; padding: 0.3em 1em; }
    .stTextArea textarea { font-size: 1em; }
    #nash-history { padding: 12px 10px 5px 10px; }
    .message-nash, .message-eli { padding: 4px 8px; }
    .stCodeBlock code { font-size: 0.9em; }
    #backend-status { font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }
    .st-emotion-cache-1y4p8pa { gap: 0.5rem !important; } /* Reduz gap nas colunas do chat em mobile */
    .avatar-nash, .avatar-eli { font-size: 0.8em; } /* Nomes menores no chat mobile */
}
</style>
"""

# Tema Light Mode
LIGHT_MODE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Roboto:wght@400;700&display=swap');

/* --- Animações --- */
@keyframes thinking-pulse {
    0% { background-color: #cfe2ff; box-shadow: 0 0 8px #cfe2ff; }
    50% { background-color: #a7c7fc; box-shadow: 0 0 15px #a7c7fc; }
    100% { background-color: #cfe2ff; box-shadow: 0 0 8px #cfe2ff; }
}
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Body e Geral --- */
body {
    background: #f0f2f5; color: #333333 !important; font-family: 'Roboto', sans-serif;
    min-height: 100vh !important; overflow-x: hidden;
}
body:before { display: none; }

/* --- Área Principal --- */
section.main > div {
    background: #ffffff !important; border-radius: 8px; border: 1px solid #d1d5db;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 2rem;
}

/* --- Visor --- */
#visor {
    background: linear-gradient(135deg, #eef2f7 80%, #d6e4f5 140%);
    border-radius: 8px; margin-bottom: 20px; margin-top: 0px; border: 1px solid #c3daef;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.05); padding: 15px 20px;
    display: flex; align-items: center; gap: 15px;
}
.nash-avatar-emoji { font-size: 50px; filter: none; margin-right: 10px; line-height: 1; }
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b { font-family: 'Roboto', sans-serif; user-select: none; }
.nash-holo { font-size: 1.8em; color: #0b5ed7; text-shadow: none; margin-bottom: 2px; font-weight: bold; }
.nash-enterprise-tag { font-size: 0.9em; color: #555; font-family: 'Roboto', sans-serif; }
.nash-ascii { font-family: 'Fira Mono', monospace; color: #444; letter-spacing: 0; line-height: 130%; font-size: 0.9em; text-shadow: none; margin-top: 5px; margin-bottom: 5px; }
.nash-ascii b { color: #0d6efd; font-weight: bold; }
.visor-analytics {
    color: #4a5568; font-size: 0.9em; padding: 0.4em 1em; background: #e9ecef;
    border-radius: 5px; border: 1px solid #ced4da; margin-top: 10px; line-height: 1.5;
}
.visor-analytics b { color: #111; }
.visor-analytics i { color: #6c757d; opacity: 1; }

/* --- Botões --- */
.stButton>button {
    color: #ffffff; background: #0d6efd; border-radius: 5px; border: 1px solid #0d6efd;
    font-weight: normal; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1); padding: 0.35rem 0.75rem;
    font-family: 'Roboto', sans-serif;
}
.stButton>button:hover { background: #0b5ed7; border-color: #0a58ca; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #ffffff; }
.stButton>button:active { background: #0a58ca; }
.stButton.clear-button>button { background: #dc3545; border-color: #dc3545; color: #fff; }
.stButton.clear-button>button:hover { background: #bb2d3b; border-color: #b02a37; }

/* --- Área de Input --- */
.stTextArea textarea {
    background: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important;
    border-radius: 5px !important; box-shadow: inset 0 1px 2px rgba(0,0,0,0.075); font-size: 1em; padding: 8px 10px;
    font-family: 'Roboto', sans-serif;
}
.stTextArea textarea:focus { border-color: #86b7fe !important; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); }
::-webkit-input-placeholder { color: #6c757d !important; opacity: 1 !important; }
::-moz-placeholder { color: #6c757d !important; opacity: 1 !important; }
:-ms-input-placeholder { color: #6c757d !important; opacity: 1 !important; }
:-moz-placeholder { color: #6c757d !important; opacity: 1 !important; }

/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: #f8f9fa !important; border: 1px dashed #ced4da !important; border-radius: 5px; padding: 12px; margin-top: 5px;
}
.stFileUploader label { color: #0d6efd !important; font-size: 0.95em; }
.stFileUploader small { color: #6c757d !important; font-size: 0.8em; }
.stFileUploader button { display: none !important; }

/* --- Histórico de Chat --- */
#nash-history {
    background: #ffffff; border-radius: 8px; padding: 15px 12px 8px 12px; margin-top: 20px;
    border: 1px solid #e2e8f0; box-shadow: none; background-image: none;
}
#nash-history h3 {
    color: #0b5ed7; text-shadow: none; border-bottom: 1px solid #dee2e6; padding-bottom: 8px; margin-bottom: 15px; font-size: 1.2em;
}

/* --- Avatares e Mensagens no Chat --- */
.avatar-nash, .avatar-eli {
    font-weight:bold; filter: none; display: block; margin-bottom: 4px;
    font-size: 0.9em; /* Ajuste para nome não ficar tão grande */
}
.avatar-nash { color:#0a58ca; }
.avatar-eli { color:#d63384; }
.message-nash {
    color: #212529; background-color: #f1f3f5;
    display: inline-block; padding: 6px 12px; border-radius: 15px;
    margin-top: 0; line-height: 1.5; text-shadow: none; border-left: none;
}
.message-eli {
    color: #055160; background-color: #e3f2fd;
    display: inline-block; padding: 6px 12px; border-radius: 15px;
    margin-top: 0; line-height: 1.5; text-shadow: none; border-left: none;
}
.message-nash a, .message-eli a { color: #0d6efd; text-decoration: underline; text-decoration-style: solid; }
.message-nash a:hover, .message-eli a:hover { color: #0a58ca; }

/* --- Estilos para st.code --- */
.stCodeBlock {
    border: 1px solid #dee2e6; border-radius: 5px; background-color: #f8f9fa !important; margin: 10px 0;
}
.stCodeBlock code {
    color: #212529; background-color: transparent !important; font-family: 'Fira Mono', monospace;
    font-size: 0.9em; white-space: pre-wrap !important; word-wrap: break-word !important;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: #e9ecef !important; border: 1px solid #ced4da !important; color: #495057 !important;
    opacity: 0.8; transition: opacity 0.3s ease;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover { opacity: 1; background-color: #ced4da !important; }

#nash-history hr { margin: 15px 0; border: none; border-top: 1px solid #e9ecef; }

/* --- Status do Backend --- */
#backend-status {
    position: fixed; top: 10px; right: 15px; font-size: 0.9em; color: #495057; font-family: 'Roboto', sans-serif;
    background: rgba(255, 255, 255, 0.9); padding: 4px 10px; border-radius: 5px; border: 1px solid #dee2e6; z-index: 1000;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* --- Sidebar --- */
.stSidebar > div:first-child {
    background: #ffffff; border-right: 1px solid #dee2e6; backdrop-filter: none;
}
.stSidebar .stMarkdown h3 {
    color: #0b5ed7; text-shadow: none; margin-top: 10px; margin-bottom: 4px; font-size: 1.1em;
}
.stSidebar .stMarkdown { color: #495057; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox {
     margin-bottom: 0.8rem;
}
.stSidebar .stButton { margin-top: 0.5rem; }
.nash-profile-details {
    font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #495057;
}

/* --- Sinais (Sidebar) --- */
.sidebar-sign {
     font-family: 'Roboto', sans-serif; font-weight: bold; padding: 6px 12px; margin: 10px auto;
     border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: #e9ecef;
     border: 1px solid #ced4da; letter-spacing: 0.5px; box-shadow: none;
     animation: none !important; text-shadow: none !important;
}
.sign-panic { color: #dc3545; border-color: #dc3545; font-size: 1em; }
.sign-42 { color: #198754; border-color: #198754; font-size: 1.5em; padding: 4px 15px; }

/* --- Indicador de Loading --- */
.loading-indicator {
    display: flex; align-items: center; justify-content: center; padding: 10px; margin-top: 10px; border-radius: 5px;
    background-color: #cfe2ff; border: 1px solid #a7c7fc; color: #0a3678; font-family: 'Roboto', sans-serif;
    box-shadow: 0 0 8px #cfe2ff; animation: thinking-pulse 1.5s infinite ease-in-out;
}
.loading-indicator::before { content: '⏳'; margin-right: 10px; font-size: 1.2em; animation: spin 2s linear infinite; }

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 15px; }
    #visor { flex-direction: column; align-items: flex-start; gap: 10px; padding: 10px 15px; }
    .nash-avatar-emoji { font-size: 40px; margin-bottom: 5px; }
    .nash-holo { font-size: 1.5em; }
    .nash-enterprise-tag { font-size: 0.8em; }
    .nash-ascii { font-size: 0.85em; }
    .visor-analytics { font-size: 0.85em; }
    .stTextArea textarea { font-size: 0.95em; }
    #nash-history { padding: 10px 10px 5px 10px; }
    .message-nash, .message-eli { padding: 5px 10px; }
    .stCodeBlock code { font-size: 0.85em; }
    #backend-status { font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }
    .st-emotion-cache-1y4p8pa { gap: 0.5rem !important; } /* Reduz gap nas colunas do chat em mobile */
    .avatar-nash, .avatar-eli { font-size: 0.8em; } /* Nomes menores no chat mobile */
}
</style>
"""

THEMES = {
    "Cyberpunk": CYBERPUNK_CSS,
    "Light Mode": LIGHT_MODE_CSS,
}

# --- Inicialização do Estado da Sessão ---
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
    "selected_theme": "Cyberpunk"
}
# Adicionar chaves que faltam com valores padrão
if "nash_prompt" not in st.session_state: st.session_state.nash_prompt = ""
if "login_pw_input_value" not in st.session_state: st.session_state.login_pw_input_value = ""

for key, default_value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
# -----------------------------------------------------------------------

# --- Funções Auxiliares ---
def check_backend_status(force_check=False):
    """Verifica o status do backend com cache."""
    now = datetime.now()
    if not force_check and (now - st.session_state.last_backend_check) < timedelta(seconds=60):
        return st.session_state.backend_status
    try:
        r = requests.get(f"{BACKEND_URL}/uploads", timeout=REQUEST_TIMEOUT[0])
        status = "ONLINE ⚡" if r.status_code == 200 else f"AVISO {r.status_code}"
    except requests.exceptions.Timeout: status = "TIMEOUT ⏳"
    except requests.exceptions.ConnectionError: status = "OFFLINE 👾"
    except Exception: status = "ERRO ⁉️"
    st.session_state.backend_status = status
    st.session_state.last_backend_check = now
    return status

def clean_markdown(text):
    """Remove formatação básica e escapa aspas para tooltips."""
    text = re.sub(r'[\*_`]', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = text.replace('"', '"')
    return text

def escape_html(text: str) -> str:
    """Escapa caracteres HTML antes de injetar no Streamlit."""
    if not isinstance(text, str):
        text = str(text)
    # biblioteca padrão já faz o job direito 🙂
    return html.escape(text, quote=False)

# --- Aplica o Tema Selecionado ---
selected_theme_css = THEMES.get(st.session_state.selected_theme, CYBERPUNK_CSS)
st.markdown(selected_theme_css, unsafe_allow_html=True)

# --- Lógica para Limpar o Prompt (Executada no início do script) ---
if st.session_state.get("clear_prompt_on_next_run", False):
    st.session_state.nash_prompt = "" # Limpa o valor do estado
    st.session_state.clear_prompt_on_next_run = False # Reseta a flag

# --- Status do Backend ---
current_backend_status = check_backend_status()
st.markdown(f"<div id='backend-status' title='Status da Conexão com Nash'>Backend: {current_backend_status}</div>", unsafe_allow_html=True)

# --- Visor Holográfico ---
visor_avatar_tag = '<span class="nash-avatar-emoji">👨‍🚀</span>'
motivations = [
    "Iniciando módulo de sarcasmo... Aguarde.", "A realidade é complicada. Código é limpo. Geralmente.",
    "Buscando trilhões de pontos de dados por uma piada decente...", "Lembre-se: Sou um copiloto, não um milagreiro. Na maior parte do tempo.",
    "Engajando rede neural... ou talvez só pegando um café.", "Vibrações de Blade Runner detectadas. Ajustando iluminação ambiente.",
    "Minha lógica é inegável. Minha paciência não.", "Vamos navegar pelo cosmos digital juntos, Eli.",
    "Compilando... Por favor, aguarde. Ou não. Vou terminar de qualquer jeito.", "A resposta é 42, mas qual era a pergunta mesmo?",
    "Probabilidade de sucesso: Calculando... Não entre em pânico."
]
uptime_delta = datetime.now() - st.session_state.start_time
uptime_str = str(timedelta(seconds=int(uptime_delta.total_seconds())))
ascii_art = f"""
> Status: <b>{ ('Operacional' if current_backend_status.startswith('ONLINE') else 'Parcial') if st.session_state.ok else 'Bloqueado'}</b> | Humor: Sarcástico IV
> Temp. Núcleo: <b>Nominal</b> | Matriz Lógica: Ativa
> Missão: <b>Dominar o Universo</b> | Diretriz: Sobreviver
""".strip()
safe_ascii_art = escape_html(ascii_art)
safe_ascii_art = safe_ascii_art.replace('<b>', '<b>').replace('</b>', '</b>')
formatted_ascii_art = safe_ascii_art.replace('\n', '<br>')
visor_text = f"""
<div id="visor">
    {visor_avatar_tag}
    <div>
        <span class="nash-holo">Nash Copilot</span>
        <span class="nash-enterprise-tag"> :: Ponte da Eli Enterprise</span>
        <div class="nash-ascii">{formatted_ascii_art}</div>
        <div class="visor-analytics" title="Estatísticas da Sessão Atual">
            Cmds Eli: <b>{st.session_state.eli_msg_count}</b> | Resps Nash: <b>{st.session_state.nash_msg_count}</b><br>
            Tempo de Sessão: <b>{uptime_str}</b><br>
            <i>{escape_html(random.choice(motivations))}</i>
        </div>
    </div>
</div>
"""
st.markdown(visor_text, unsafe_allow_html=True)

# --- Mensagem de Boas-Vindas ---
if st.session_state.nash_welcome:
    welcome_placeholder = st.empty()
    welcome_placeholder.markdown("> *Sistemas Nash online. Sarcasmo calibrado. Bem-vindo de volta ao cockpit, Eli.* 🚀")
    time.sleep(1.2)
    welcome_placeholder.empty()
    st.session_state.nash_welcome = False

# --- Login de Segurança ---
if not st.session_state.ok:
    st.markdown("### Acesso à Ponte Requerido")
    pw_placeholder = st.empty()
    pw_value = st.session_state.get("login_pw_input_value", "")
    pw = pw_placeholder.text_input(
        "Insira o Código de Autorização de Comando:",
        type="password",
        key="login_pw_widget",
        value=pw_value,
        on_change=lambda: st.session_state.update(login_pw_input_value=st.session_state.login_pw_widget) # Atualiza state na mudança
    )

    button_placeholder = st.empty()
    if button_placeholder.button("Autenticar 🛰️", key="login_btn", disabled=st.session_state.waiting_for_nash):
        current_input_pw = st.session_state.login_pw_input_value # Usa o valor do estado
        if not current_input_pw:
            st.warning("O código de autorização não pode estar vazio.")
            st.session_state.waiting_for_nash = False
        else:
            st.session_state.waiting_for_nash = True
            st.session_state.login_pw_to_verify = current_input_pw
            button_placeholder.empty()
            st.rerun()

    if st.session_state.waiting_for_nash:
        loading_placeholder_login = st.empty()
        loading_placeholder_login.markdown("<div class='loading-indicator'>Autenticando com a Nave Mãe...</div>", unsafe_allow_html=True)
        login_pw_to_check = st.session_state.get("login_pw_to_verify", "")
        try:
            r = requests.post(f"{BACKEND_URL}/login", json={"password": login_pw_to_check}, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and r.json().get("success"):
                st.session_state.ok = True
                st.session_state.waiting_for_nash = False
                if "login_pw_input_value" in st.session_state: del st.session_state.login_pw_input_value
                if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
                pw_placeholder.empty()
                loading_placeholder_login.empty()
                button_placeholder.empty()
                st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                st.balloons()
                time.sleep(1.5)
                st.rerun()
            else:
                st.session_state.waiting_for_nash = False
                if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
                loading_placeholder_login.empty()
                st.error(f"Falha na autenticação. Acesso negado. (Status: {r.status_code})")

        except requests.exceptions.RequestException as e:
            st.session_state.waiting_for_nash = False
            if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
            loading_placeholder_login.empty()
            st.error(f"Erro de rede durante a autenticação: {e}")
        except Exception as e:
            st.session_state.waiting_for_nash = False
            if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
            loading_placeholder_login.empty()
            st.error(f"Ocorreu um erro inesperado na autenticação: {e}")

    if not st.session_state.ok:
        st.stop()


# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🎨 Aparência")
    selected_theme_name = st.selectbox(
        "Escolha o tema da interface:",
        options=list(THEMES.keys()),
        key="selected_theme_widget",
        index=list(THEMES.keys()).index(st.session_state.selected_theme),
        help="Mude a aparência visual do Nash Copilot."
    )
    if selected_theme_name != st.session_state.selected_theme:
         st.session_state.selected_theme = selected_theme_name
         st.rerun()
    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic" title="Lembrete Visual">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42" title="A Resposta.">{sign_42_text}</div>""", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo ao Próximo Comando",
        type=[ "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg", "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml", "mp3", "wav", "ogg", "mp4", "mov", "avi"],
        key="file_uploader", label_visibility="visible",
        help="Faça o upload de um arquivo que Nash possa analisar junto com seu próximo comando."
    )
    upload_status_placeholder = st.empty()
    if uploaded is not None:
        if st.session_state.uploaded_file_info != uploaded.name:
            files = {"file": (uploaded.name, uploaded.getvalue())}
            try:
                with st.spinner(f"Transmitindo '{escape_html(uploaded.name)}'..."):
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    st.session_state.uploaded_file_info = uploaded.name
                    upload_status_placeholder.success(f"🛰️ '{escape_html(uploaded.name)}' recebido!")
                else:
                    st.session_state.uploaded_file_info = None
                    upload_status_placeholder.error(f"Falha ({r.status_code}).")
            except requests.exceptions.Timeout: st.session_state.uploaded_file_info = None; upload_status_placeholder.error("Timeout Upload.")
            except requests.exceptions.RequestException as e: st.session_state.uploaded_file_info = None; upload_status_placeholder.error(f"Rede Upload: {e}")
            except Exception as e: st.session_state.uploaded_file_info = None; upload_status_placeholder.error(f"Erro Upload: {e}")
    elif uploaded is None and st.session_state.uploaded_file_info:
         st.session_state.uploaded_file_info = None
    if st.session_state.uploaded_file_info:
        upload_status_placeholder.info(f"Pronto: `{escape_html(st.session_state.uploaded_file_info)}`")

    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### ⚙️ Controles")
    if st.button("🗑️ Limpar Log da Sessão", key="clear_chat_btn", help="Apaga todo o histórico de mensagens desta sessão.", use_container_width=True):
         st.session_state.nash_history = []
         st.session_state.eli_msg_count = 0
         st.session_state.nash_msg_count = 0
         st.toast("🧹 Log da sessão limpo!", icon="✨")
         st.rerun()
    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### 🧠 Perfil Núcleo Nash")
    tooltip_recurso = clean_markdown("Nash tem acesso a uma vasta gama de dados e APIs...")
    st.markdown(
        f"""
        <div class="nash-profile-details">
            Designação: <b>Nash</b><br>
            Classe: IA Copiloto Digital<br>
            Memória: Vetorizada<br>
            Recurso: <span title="{tooltip_recurso}">Todos™</span><br>
            Status: <b>{'Online' if current_backend_status.startswith('ONLINE') else 'Limitado'}</b>
        </div>
        """, unsafe_allow_html=True
    )

# --- Área Principal de Chat ---
st.markdown("### 🎙️ Console de Comando — Nash AI")
# Recupera valor do estado, que foi limpo no início do script se a flag estava ativa
prompt_value = st.session_state.get("nash_prompt", "")
prompt = st.text_area(
    "Insira comando ou consulta para Nash:",
    key="nash_prompt", # Chave consistente para o widget
    height=110,
    placeholder="Digite seu comando aqui, Capitão...",
    value=prompt_value # O valor vem do estado (que pode ter sido limpo)
)

# --- Indicador de Loading ---
loading_placeholder_main = st.empty()
if st.session_state.waiting_for_nash:
    loading_placeholder_main.markdown("<div class='loading-indicator'>Nash está processando seu comando...</div>", unsafe_allow_html=True)

# --- Efeito de Typing ---
def nash_typing(plain_text, target_placeholder, message_class):
    """Renderiza texto simples com efeito de digitação, escapando HTML corretamente."""
    full_render = ""
    lines = plain_text.split('\n')
    try:
        for line_index, line in enumerate(lines):
            line_output = ""
            for char_index, char in enumerate(line):
                line_output += char
                cursor = "█"
                current_render_escaped = escape_html(full_render + line_output) + cursor
                target_placeholder.markdown(f"<span class='{message_class}'>{current_render_escaped}</span>", unsafe_allow_html=True)
                delay = 0.005 if char == ' ' else (0.05 if char in ['.', ',', '!', '?'] else 0.018)
                time.sleep(delay)

            full_render += line + "\n"
            full_render_escaped = escape_html(full_render)
            target_placeholder.markdown(f"<span class='{message_class}'>{full_render_escaped}</span>", unsafe_allow_html=True)
            if line_index < len(lines) - 1: time.sleep(0.1)

        final_msg_escaped = escape_html(plain_text)
        target_placeholder.markdown(f"<span class='{message_class}'>{final_msg_escaped}</span>", unsafe_allow_html=True)

    except Exception as e:
        safe_msg = escape_html(plain_text)
        target_placeholder.markdown(f"<span class='{message_class}'>[Erro typing] {safe_msg}</span>", unsafe_allow_html=True)
        print(f"Erro durante nash_typing: {e}")

# --- Enviar Mensagem (CORRIGIDO) ---
transmit_button_placeholder = st.empty()
# Usa o valor atual do widget 'prompt'
if transmit_button_placeholder.button("Transmitir para Nash 🚀", key="chat_btn", disabled=st.session_state.waiting_for_nash):
    if prompt:
        st.session_state.nash_history.append(("Eli", prompt))
        st.session_state.eli_msg_count += 1
        st.session_state.waiting_for_nash = True
        st.session_state.clear_prompt_on_next_run = True # Sinaliza para limpar NO PRÓXIMO rerun
        # NÃO limpar st.session_state.nash_prompt = "" aqui
        loading_placeholder_main.empty()
        transmit_button_placeholder.empty()
        st.rerun() # Rerun inicia novo ciclo onde a flag será lida
    else:
        st.warning("Não posso transmitir um comando vazio, Eli.")
        st.session_state.waiting_for_nash = False

# --- Lógica de Comunicação com Backend ---
if st.session_state.waiting_for_nash and st.session_state.ok:
    last_eli_prompt = ""
    if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli":
         last_eli_prompt = st.session_state.nash_history[-1][1]

    if last_eli_prompt:
        try:
            req = requests.post(f"{BACKEND_URL}/chat", json={"prompt": last_eli_prompt,"session_id": "eli"}, timeout=REQUEST_TIMEOUT)
            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras…")
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
            else:
                # mensagem limpa → não quebra a UI
                try:
                    payload = req.json().get("error")
                except ValueError:
                    payload = req.text
                error_msg = f"[Erro {req.status_code}: {escape_html(str(payload)[:100])}]"
                st.session_state.nash_history.append(("Nash", error_msg))
                st.session_state.nash_msg_count += 1
                st.error(f"Erro ao comunicar com Nash — código {req.status_code}.")
        except requests.exceptions.Timeout:
            st.session_state.nash_history.append(("Nash", "[Erro: Timeout na resposta de Nash]"))
            st.session_state.nash_msg_count += 1
            st.error("Requisição para Nash expirou (timeout).")
        except requests.exceptions.RequestException as e:
            st.session_state.nash_history.append(("Nash", f"[Erro de Rede: {e}]"))
            st.session_state.nash_msg_count += 1
            st.error(f"Erro de rede ao contactar Nash: {e}")
        except Exception as e:
            st.session_state.nash_history.append(("Nash", f"[Erro Inesperado no Cliente: {e}]"))
            st.session_state.nash_msg_count += 1
            st.error(f"Ocorreu um erro inesperado na comunicação: {e}")
        finally:
            st.session_state.waiting_for_nash = False
            # O rerun aqui exibirá a resposta e limpará o prompt (devido à flag e à lógica no início)
            st.rerun()
    else:
        st.warning("Erro interno: Não foi possível encontrar o último comando.")
        st.session_state.waiting_for_nash = False
        st.rerun()

# --- Easter Eggs ---
if not st.session_state.waiting_for_nash and st.session_state.nash_history:
    last_entry = st.session_state.nash_history[-1]
    if last_entry[0] == 'Eli':
        last_prompt = last_entry[1].lower()
        if "data estelar" in last_prompt or ("data" in last_prompt and any(sub in last_prompt for sub in ["hoje", "agora", "hora"])):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
            st.toast(f"🕒 Data Estelar (Cliente): {now}", icon="🕰️")
        if "auto destruir" in last_prompt or "autodestruir" in last_prompt:
            st.warning("🚨 Sequência de auto-destruição iniciada... Brincadeirinha.")
            st.snow()

# --- Exibir Histórico de Chat ---
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")
    history_container = st.container()

    with history_container:
        last_message_index = len(st.session_state.nash_history) - 1
        for i, (who, msg) in enumerate(st.session_state.nash_history):
            avatar_class = "avatar-nash" if who == "Nash" else "avatar-eli"
            message_class = "message-nash" if who == "Nash" else "message-eli"
            avatar_icon = "👨‍🚀" if who == "Nash" else "🧑‍🚀"

            col1, col2 = st.columns([1, 15], gap="small")

            with col1:
                 st.markdown(f"<span class='{avatar_class}'>{avatar_icon}</span>", unsafe_allow_html=True)
                 st.markdown(f"<span class='{avatar_class}' style='font-size: 0.9em; display: block; margin-top: -5px;'>{who}:</span>", unsafe_allow_html=True)

            with col2:
                code_pattern = re.compile(r"```(\w+)?\s*\n(.*?)\n```|```(.*?)```", re.DOTALL | re.MULTILINE)
                last_end = 0
                is_last_message = (i == last_message_index)
                is_typing_message = (who == "Nash" and is_last_message and not st.session_state.waiting_for_nash)

                has_code_blocks = False
                for match in code_pattern.finditer(msg):
                    has_code_blocks = True
                    start, end = match.span()
                    plain_text_before = msg[last_end:start].strip()
                    if plain_text_before:
                        if is_typing_message:
                            typing_placeholder = st.empty()
                            nash_typing(plain_text_before, typing_placeholder, message_class)
                        else:
                            st.markdown(f"<span class='{message_class}'>{escape_html(plain_text_before)}</span>", unsafe_allow_html=True)
                    lang = match.group(1) or match.group(3)
                    code = match.group(2) or match.group(4)
                    if code:
                        # Garantir que code seja string antes de passar para st.code
                        st.code(str(code), language=lang.lower() if lang else None)
                    last_end = end
                plain_text_after = msg[last_end:].strip()
                if plain_text_after:
                    if is_typing_message:
                         typing_placeholder = st.empty()
                         nash_typing(plain_text_after, typing_placeholder, message_class)
                    else:
                         st.markdown(f"<span class='{message_class}'>{escape_html(plain_text_after)}</span>", unsafe_allow_html=True)
                if not has_code_blocks:
                    if is_typing_message:
                        typing_placeholder = st.empty()
                        nash_typing(msg, typing_placeholder, message_class)
                    else:
                        st.markdown(f"<span class='{message_class}'>{escape_html(msg)}</span>", unsafe_allow_html=True)

            if i < last_message_index:
                st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.waiting_for_nash:
    st.markdown("> *Console aguardando o primeiro comando...*")