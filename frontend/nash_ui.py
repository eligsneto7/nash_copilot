# nash_ui_v8_features_fixes.py
import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import random
import re # Importado para regex e limpeza

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
@keyframes blink-neon { /* ... (sem alterações) ... */
  0%, 100% { opacity: 1; text-shadow: 0 0 7px #ff07e6, 0 0 15px #ff07e6, 0 0 20px #ff07e6; }
  50% { opacity: 0.7; text-shadow: 0 0 5px #ff07e6a0, 0 0 10px #ff07e6a0; }
}
@keyframes subtle-pulse { /* ... (sem alterações) ... */
  0%, 100% { opacity: 0.9; }
  50% { opacity: 1; }
}
@keyframes scanline { /* ... (sem alterações) ... */
  0% { background-position: 0 0; }
  100% { background-position: 0 100%; }
}
@keyframes thinking-pulse { /* ... (sem alterações) ... */
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
#visor { /* ... (sem alterações) ... */
    background: linear-gradient(135deg, rgba(16, 18, 37, 0.97) 80%, rgba(255, 7, 230, 0.85) 140%), rgba(5, 5, 15, 0.96);
    border-radius: 15px; margin-bottom: 20px; margin-top: -10px; border: 2.5px solid #ff07e660;
    box-shadow: 0 0 30px #e600c650, inset 0 0 15px #101225e0; padding: 18px 26px 14px 30px;
    display: flex; align-items: center; gap: 25px;
}
.nash-avatar-emoji { /* ... (sem alterações) ... */
    font-size: 65px; filter: drop-shadow(0 0 15px #0affa0a0); margin-right: 15px; line-height: 1; animation: subtle-pulse 3s infinite ease-in-out;
}
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b { /* ... (sem alterações) ... */
    font-family: 'Orbitron', 'Fira Mono', monospace; user-select: none;
}
.nash-holo { font-size: 2.1em; color: #0affa0; text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; margin-bottom: 3px; }
.nash-enterprise-tag { font-size: 0.9em; color: #ff07e6b0; font-family: 'Fira Mono', monospace; }
.nash-ascii { font-family: 'Fira Mono', monospace; color: #0affa0d0; letter-spacing: 0.5px; line-height: 115%; font-size: 0.95em; text-shadow: 0 0 8px #0affa040; margin-top: -5px; margin-bottom: 5px; }
.nash-ascii b { color: #ff07e6; font-weight: bold; }
.visor-analytics { /* ... (sem alterações) ... */
    color:#ff07e6; font-size: 0.95em; padding: 0.4em 1.3em; background: rgba(10, 10, 25, 0.75);
    border-radius: 8px; border: 1px solid #ff07e650; margin-top: 10px; line-height: 1.45;
}
.visor-analytics b { color: #ffffff; }
.visor-analytics i { color: #c8d3ff; opacity: 0.85; }

/* --- Botões --- */
.stButton>button { /* ... (sem alterações) ... */
    color: #e0e8ff; background: #1f243d; border-radius: 8px; border: 2px solid #0affa070;
    font-weight: bold; transition: all 0.3s ease; box-shadow: 0 0 10px #0affa020; padding: 0.4rem 0.8rem;
}
.stButton>button:hover { background: #2a3050; border-color: #0affa0; box-shadow: 0 0 18px #0affa060; color: #ffffff; }
.stButton>button:active { background: #15182a; }
.stButton.clear-button>button { border-color: #ff07e670; color: #ffc0e8; box-shadow: 0 0 10px #ff07e620; }
.stButton.clear-button>button:hover { border-color: #ff07e6; background: #3d1f35; box-shadow: 0 0 18px #ff07e660; color: #ffffff; }

/* --- Área de Input --- */
.stTextArea textarea { /* ... (sem alterações) ... */
    background: #101225 !important; color: #d8e0ff !important; border: 1px solid #0affa040 !important;
    border-radius: 5px !important; box-shadow: inset 0 0 10px #00000060; font-size: 1.05em; padding: 10px 12px;
}
.stTextArea textarea:focus { border-color: #0affa0 !important; box-shadow: 0 0 12px #0affa040; }
::-webkit-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
::-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-ms-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }

/* --- File Uploader (Sidebar) --- */
.stFileUploader { /* ... (sem alterações) ... */
    background: #101225cc !important; border: 1px dashed #0affa050 !important; border-radius: 8px; padding: 15px; margin-top: 5px;
}
.stFileUploader label { color: #0affa0b0 !important; font-size: 0.95em; }
.stFileUploader small { color: #0affa070 !important; font-size: 0.8em; }
.stFileUploader button { display: none !important; }

/* --- Histórico de Chat --- */
#nash-history { /* ... (sem alterações, mantém scanlines) ... */
    background: #0c0e1acc; border-radius: 10px; padding: 18px 16px 8px 15px; margin-top: 25px;
    border: 1px solid #0affa030;
    background-image: repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(0, 255, 255, 0.02) 5px, rgba(0, 255, 255, 0.02) 6px, transparent 7px, transparent 10px), repeating-linear-gradient(90deg, rgba(255, 255, 255, 0.01) 0px, rgba(255, 255, 255, 0.02) 1px, transparent 1px, transparent 8px);
    box-shadow: inset 0 0 15px #000000a0, 0 0 15px #0aebff10;
}
#nash-history h3 { /* ... (sem alterações) ... */
    color: #ff07e6; text-shadow: 0 0 10px #ff07e670; border-bottom: 1px solid #ff07e640; padding-bottom: 5px; margin-bottom: 18px;
}

/* --- Avatares e Mensagens no Chat --- */
.avatar-nash, .avatar-eli { /* ... (sem alterações) ... */
    font-weight:bold; filter: drop-shadow(0 0 6px); display: block; margin-bottom: 4px;
}
.avatar-nash { color:#0affa0; }
.avatar-eli { color:#ff07e6; }
.message-nash, .message-eli { /* ... (sem alterações) ... */
    display: inline-block; padding: 5px 10px; border-radius: 5px; background-color: rgba(255, 255, 255, 0.04);
    margin-top: 0; line-height: 1.5; text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
.message-nash { color: #c0f0f0; border-left: 3px solid #0affa070; }
.message-eli { color: #ffd8f4; border-left: 3px solid #ff07e670; }
.message-nash a, .message-eli a { /* ... (sem alterações) ... */
    color: #87cefa; text-decoration: underline; text-decoration-style: dashed; text-underline-offset: 3px;
}
.message-nash a:hover, .message-eli a:hover { color: #ffffff; text-decoration-style: solid; }

/* --- NOVO: Estilos para st.code (integrar com tema) --- */
.stCodeBlock {
    border: 1px solid #0affa050;
    border-radius: 5px;
    background-color: rgba(10, 12, 25, 0.8) !important; /* Fundo escuro semi-transparente */
    margin: 10px 0;
}
.stCodeBlock code {
    color: #e0e8ff; /* Cor do código */
    background-color: transparent !important; /* Remove fundo interno do highlight.js */
    font-family: 'Fira Mono', monospace;
    font-size: 0.95em;
    white-space: pre-wrap !important; /* Garante quebra de linha */
    word-wrap: break-word !important;
}
/* Estilo do botão Copiar (interno do st.code) - Tentativa de ajuste */
.stCodeBlock div[data-testid="stCodeToolbar"] > button {
    background-color: #1f243d !important;
    border: 1px solid #0affa070 !important;
    color: #e0e8ff !important;
    opacity: 0.7;
    transition: opacity 0.3s ease;
}
.stCodeBlock div[data-testid="stCodeToolbar"] > button:hover {
    opacity: 1;
    background-color: #2a3050 !important;
    border-color: #0affa0 !important;
}

#nash-history hr { margin: 15px 0; border: none; border-top: 1px solid #ffffff15; }

/* --- Status do Backend (Topo Direito) --- */
#backend-status { /* ... (sem alterações) ... */
    position: fixed; top: 10px; right: 15px; font-size: 0.9em; color: #ff07e6; font-family: 'Fira Mono', monospace;
    background: rgba(15, 15, 25, 0.85); padding: 4px 10px; border-radius: 5px; border: 1px solid #ff07e640; z-index: 1000;
}

/* --- Sidebar --- */
.stSidebar > div:first-child { /* ... (sem alterações) ... */
    background: linear-gradient(180deg, #101225f0 0%, #181c30f0 100%); border-right: 1px solid #0affa020; backdrop-filter: blur(5px);
}
.stSidebar .stMarkdown h3 { /* ... (sem alterações) ... */
    color: #ff07e6; text-shadow: 0 0 8px #ff07e650; margin-top: 10px; margin-bottom: 8px;
}
.stSidebar .stMarkdown { color: #c8d3ff; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox { /* Adicionado stSelectbox */
    margin-bottom: 1rem;
}
.stSidebar .stButton { margin-top: 0.5rem; }

/* --- Sinais Neon (Sidebar) --- */
.sidebar-sign { /* ... (sem alterações) ... */
    font-family: 'Orbitron', 'Fira Mono', monospace; font-weight: bold; padding: 8px 15px; margin: 15px auto;
    border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: rgba(0, 0, 10, 0.5);
    border: 1px solid; letter-spacing: 1px; box-shadow: inset 0 0 10px rgba(0,0,0,0.6);
}
.sign-panic { /* ... (sem alterações) ... */
    color: #ff07e6; border-color: #ff07e660; animation: blink-neon 1.5s infinite; font-size: 1.1em;
}
.sign-42 { /* ... (sem alterações) ... */
    color: #0affa0; border-color: #0affa060; text-shadow: 0 0 6px #0affa0, 0 0 14px #0affa0, 0 0 20px #0affa0;
    font-size: 1.8em; padding: 5px 20px;
}

/* --- Indicador de Loading --- */
.loading-indicator { /* ... (sem alterações) ... */
    display: flex; align-items: center; justify-content: center; padding: 10px; margin-top: 10px; border-radius: 5px;
    background-color: #0affa030; border: 1px solid #0affa050; color: #e0ffff; font-family: 'Fira Mono', monospace;
    box-shadow: 0 0 8px #0affa030; animation: thinking-pulse 1.5s infinite ease-in-out;
}
.loading-indicator::before { /* ... (sem alterações) ... */
    content: '🧠'; margin-right: 10px; font-size: 1.2em; animation: spin 2s linear infinite;
}

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) { /* ... (sem alterações) ... */
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
    .stCodeBlock code { font-size: 0.9em; } /* Ajuste no código para mobile */
    #backend-status { font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }
}
</style>
"""

# Tema Light Mode (Exemplo Básico)
LIGHT_MODE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Roboto:wght@400;700&display=swap');

/* --- Animações (Manter simples) --- */
@keyframes thinking-pulse {
    0% { background-color: #cfe2ff; box-shadow: 0 0 8px #cfe2ff; }
    50% { background-color: #a7c7fc; box-shadow: 0 0 15px #a7c7fc; }
    100% { background-color: #cfe2ff; box-shadow: 0 0 8px #cfe2ff; }
}
@keyframes spin { 100% { transform: rotate(360deg); } }

/* --- Body e Geral --- */
body {
    background: #f0f2f5; /* Fundo claro */
    color: #333333 !important; /* Texto escuro */
    font-family: 'Roboto', sans-serif; /* Fonte mais padrão */
    min-height: 100vh !important; overflow-x: hidden;
}
body:before { display: none; } /* Remover chuva hacker */

/* --- Área Principal --- */
section.main > div {
    background: #ffffff !important; /* Fundo branco */
    border-radius: 8px; border: 1px solid #d1d5db; /* Borda cinza */
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 2rem;
}

/* --- Visor Holográfico (Simplificado) --- */
#visor {
    background: linear-gradient(135deg, #eef2f7 80%, #d6e4f5 140%);
    border-radius: 8px; margin-bottom: 20px; margin-top: 0px; border: 1px solid #c3daef;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.05); padding: 15px 20px;
    display: flex; align-items: center; gap: 15px;
}
.nash-avatar-emoji {
    font-size: 50px; filter: none; margin-right: 10px; line-height: 1;
}
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b {
    font-family: 'Roboto', sans-serif; user-select: none;
}
.nash-holo { font-size: 1.8em; color: #0b5ed7; /* Azul primário */ text-shadow: none; margin-bottom: 2px; font-weight: bold; }
.nash-enterprise-tag { font-size: 0.9em; color: #555; font-family: 'Roboto', sans-serif; }
.nash-ascii { font-family: 'Fira Mono', monospace; color: #444; letter-spacing: 0; line-height: 130%; font-size: 0.9em; text-shadow: none; margin-top: 5px; margin-bottom: 5px; }
.nash-ascii b { color: #0d6efd; font-weight: bold; } /* Azul link */
.visor-analytics {
    color: #4a5568; /* Cinza escuro */ font-size: 0.9em; padding: 0.4em 1em; background: #e9ecef; /* Cinza claro */
    border-radius: 5px; border: 1px solid #ced4da; margin-top: 10px; line-height: 1.5;
}
.visor-analytics b { color: #111; }
.visor-analytics i { color: #6c757d; opacity: 1; } /* Cinza secundário */

/* --- Botões --- */
.stButton>button {
    color: #ffffff; background: #0d6efd; /* Azul primário */ border-radius: 5px; border: 1px solid #0d6efd;
    font-weight: normal; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1); padding: 0.35rem 0.75rem;
    font-family: 'Roboto', sans-serif;
}
.stButton>button:hover { background: #0b5ed7; border-color: #0a58ca; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #ffffff; }
.stButton>button:active { background: #0a58ca; }
.stButton.clear-button>button { background: #dc3545; border-color: #dc3545; color: #fff; } /* Vermelho para limpar */
.stButton.clear-button>button:hover { background: #bb2d3b; border-color: #b02a37; }

/* --- Área de Input --- */
.stTextArea textarea {
    background: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important; /* Cinza padrão */
    border-radius: 5px !important; box-shadow: inset 0 1px 2px rgba(0,0,0,0.075); font-size: 1em; padding: 8px 10px;
    font-family: 'Roboto', sans-serif;
}
.stTextArea textarea:focus { border-color: #86b7fe !important; box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25); }
::-webkit-input-placeholder { color: #6c757d !important; opacity: 1 !important; } /* Placeholder cinza */
::-moz-placeholder { color: #6c757d !important; opacity: 1 !important; }
:-ms-input-placeholder { color: #6c757d !important; opacity: 1 !important; }
:-moz-placeholder { color: #6c757d !important; opacity: 1 !important; }

/* --- File Uploader (Sidebar) --- */
.stFileUploader {
    background: #f8f9fa !important; border: 1px dashed #ced4da !important; border-radius: 5px; padding: 15px; margin-top: 5px;
}
.stFileUploader label { color: #0d6efd !important; font-size: 0.95em; }
.stFileUploader small { color: #6c757d !important; font-size: 0.8em; }
.stFileUploader button { display: none !important; }

/* --- Histórico de Chat --- */
#nash-history {
    background: #ffffff; border-radius: 8px; padding: 15px 12px 8px 12px; margin-top: 20px;
    border: 1px solid #e2e8f0; box-shadow: none; background-image: none; /* Remover scanlines */
}
#nash-history h3 {
    color: #0b5ed7; text-shadow: none; border-bottom: 1px solid #dee2e6; padding-bottom: 8px; margin-bottom: 15px; font-size: 1.2em;
}

/* --- Avatares e Mensagens no Chat --- */
.avatar-nash, .avatar-eli {
    font-weight:bold; filter: none; display: block; margin-bottom: 4px;
}
.avatar-nash { color:#0a58ca; } /* Azul escuro */
.avatar-eli { color:#d63384; } /* Rosa Bootstrap */
.message-nash, .message-eli {
    display: inline-block; padding: 6px 12px; border-radius: 15px; background-color: #f1f3f5; /* Fundo cinza muito claro */
    margin-top: 0; line-height: 1.5; text-shadow: none; border-left: none; /* Remover borda lateral */
    color: #333; /* Texto principal escuro */
}
.message-eli { background-color: #e3f2fd; } /* Fundo azul claro para Eli */
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

#nash-history hr { margin: 15px 0; border: none; border-top: 1px solid #e9ecef; } /* Divisor claro */

/* --- Status do Backend (Topo Direito) --- */
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
    color: #0b5ed7; text-shadow: none; margin-top: 10px; margin-bottom: 8px; font-size: 1.1em;
}
.stSidebar .stMarkdown { color: #495057; }
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox { margin-bottom: 1rem; }
.stSidebar .stButton { margin-top: 0.5rem; }

/* --- Sinais Neon (Sidebar) -> Estilo Light --- */
.sidebar-sign {
     font-family: 'Roboto', sans-serif; font-weight: bold; padding: 6px 12px; margin: 10px auto;
     border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: #e9ecef;
     border: 1px solid #ced4da; letter-spacing: 0.5px; box-shadow: none;
     animation: none !important; /* Desliga animações */ text-shadow: none !important;
}
.sign-panic { color: #dc3545; border-color: #dc3545; font-size: 1em; } /* Vermelho */
.sign-42 { color: #198754; border-color: #198754; font-size: 1.5em; padding: 4px 15px; } /* Verde */

/* --- Indicador de Loading --- */
.loading-indicator {
    display: flex; align-items: center; justify-content: center; padding: 10px; margin-top: 10px; border-radius: 5px;
    background-color: #cfe2ff; border: 1px solid #a7c7fc; color: #0a3678; font-family: 'Roboto', sans-serif;
    box-shadow: 0 0 8px #cfe2ff; animation: thinking-pulse 1.5s infinite ease-in-out;
}
.loading-indicator::before { content: '⏳'; margin-right: 10px; font-size: 1.2em; animation: spin 2s linear infinite; }

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 15px; } /* Levemente maior para mobile light */
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
}
</style>
"""

# (Adicionar mais temas como TERMINAL_CSS aqui se desejar)
THEMES = {
    "Cyberpunk": CYBERPUNK_CSS,
    "Light Mode": LIGHT_MODE_CSS,
    # "Terminal": TERMINAL_CSS,
}

# --- Inicialização do Estado da Sessão (Adicionando chave de tema) ---
default_session_state = {
    "clear_prompt_on_next_run": False,
    "start_time": datetime.now(),
    "nash_history": [],
    "eli_msg_count": 0,
    "nash_msg_count": 0,
    "nash_welcome": True,
    "ok": False, # Flag de login
    "backend_status": "VERIFICANDO...",
    "last_backend_check": datetime.min,
    "waiting_for_nash": False, # Flag para loading indicator
    "uploaded_file_info": None, # Para feedback de upload
    "selected_theme": "Cyberpunk" # NOVO: Estado para o tema
}
for key, default_value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = default_value
# -----------------------------------------------------------------------

# --- Funções Auxiliares ---
def check_backend_status(force_check=False):
    """Verifica o status do backend, com cache simples para evitar spam."""
    now = datetime.now()
    if not force_check and (now - st.session_state.last_backend_check) < timedelta(seconds=60):
        return st.session_state.backend_status # Retorna status cacheado

    try:
        # Use um timeout curto para a verificação de status
        r = requests.get(f"{BACKEND_URL}/uploads", timeout=REQUEST_TIMEOUT[0])
        if r.status_code == 200: status = "ONLINE ⚡"
        else: status = f"AVISO {r.status_code}"
    except requests.exceptions.Timeout: status = "TIMEOUT ⏳"
    except requests.exceptions.ConnectionError: status = "OFFLINE 👾"
    except Exception: status = "ERRO ⁉️" # Simplificado

    st.session_state.backend_status = status
    st.session_state.last_backend_check = now
    return status

def clean_markdown(text):
    """Remove formatação markdown básica para tooltips."""
    text = re.sub(r'[\*_`]', '', text) # Remove *, _, `
    # Tenta remover links markdown [text](url) -> text (pode não pegar todos os casos)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # Escapar aspas para atributos HTML
    text = text.replace('"', '"')
    return text

# --- Aplica o Tema Selecionado ---
selected_theme_css = THEMES.get(st.session_state.selected_theme, CYBERPUNK_CSS) # Default para Cyberpunk
st.markdown(selected_theme_css, unsafe_allow_html=True)
# --- Fim da Aplicação do Tema ---


# --- Lógica para Limpar o Prompt ---
if st.session_state.clear_prompt_on_next_run:
    # A chave "nash_prompt" será limpa automaticamente pelo rerun se o widget for recriado
    st.session_state.clear_prompt_on_next_run = False

# --- Status do Backend (Chamada da Função) ---
current_backend_status = check_backend_status() # Usa a função com cache
st.markdown(f"<div id='backend-status' title='Status da Conexão com Nash'>Backend: {current_backend_status}</div>", unsafe_allow_html=True)

# --- Visor Holográfico+Avatar+Analytics (Atualizado com Analytics mais dinâmico) ---
visor_avatar_tag = '<span class="nash-avatar-emoji">👨‍🚀</span>'
motivations = [ # Mantido
    "Iniciando módulo de sarcasmo... Aguarde.", "A realidade é complicada. Código é limpo. Geralmente.",
    "Buscando trilhões de pontos de dados por uma piada decente...", "Lembre-se: Sou um copiloto, não um milagreiro. Na maior parte do tempo.",
    "Engajando rede neural... ou talvez só pegando um café.", "Vibrações de Blade Runner detectadas. Ajustando iluminação ambiente.",
    "Minha lógica é inegável. Minha paciência não.", "Vamos navegar pelo cosmos digital juntos, Eli.",
    "Compilando... Por favor, aguarde. Ou não. Vou terminar de qualquer jeito.", "A resposta é 42, mas qual era a pergunta mesmo?",
    "Probabilidade de sucesso: Calculando... Não entre em pânico."
]
# Cálculo do Uptime
uptime_delta = datetime.now() - st.session_state.start_time
uptime_str = str(timedelta(seconds=int(uptime_delta.total_seconds()))) # Formato H:MM:SS

# Texto ASCII (Pode ser randomizado ou mudar com status no futuro)
ascii_art = f"""
> Status: <b>{ ('Operacional' if current_backend_status.startswith('ONLINE') else 'Parcial') if st.session_state.ok else 'Bloqueado'}</b> | Humor: Sarcástico IV
> Temp. Núcleo: <b>Nominal</b> | Matriz Lógica: Ativa
> Missão: <b>Dominar o Universo</b> | Diretriz: Sobreviver
""".strip() # Usando .strip() para remover espaços extras

# Pré-formatar o ascii_art
formatted_ascii_art = ascii_art.replace('<', '<').replace('>', '>').replace('\n', '<br>')

# --- Definição do Visor ---
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
            <i>{random.choice(motivations)}</i>
        </div>
    </div>
</div>
"""
st.markdown(visor_text, unsafe_allow_html=True)


# --- Mensagem de Boas-Vindas Animada (Mantida) ---
if st.session_state.nash_welcome:
    welcome_placeholder = st.empty()
    welcome_placeholder.markdown("> *Sistemas Nash online. Sarcasmo calibrado. Bem-vindo de volta ao cockpit, Eli.* 🚀")
    time.sleep(1.2) # Ligeiramente mais longo
    welcome_placeholder.empty()
    st.session_state.nash_welcome = False
    # Não precisa de rerun aqui, a mensagem some sozinha.

# --- Login de Segurança (Com fluxo de loading e CORREÇÃO) ---
if not st.session_state.ok:
    st.markdown("### Acesso à Ponte Requerido")
    pw_placeholder = st.empty()
    pw = pw_placeholder.text_input(
        "Insira o Código de Autorização de Comando:",
        type="password",
        key="login_pw"
    )

    button_placeholder = st.empty()
    if button_placeholder.button("Autenticar 🛰️", key="login_btn", disabled=st.session_state.waiting_for_nash):
        if not pw:
            st.warning("O código de autorização não pode estar vazio.")
            st.session_state.waiting_for_nash = False
        else:
            st.session_state.waiting_for_nash = True
            button_placeholder.empty()
            st.rerun()

    if st.session_state.waiting_for_nash:
        loading_placeholder_login = st.empty()
        loading_placeholder_login.markdown("<div class='loading-indicator'>Autenticando com a Nave Mãe...</div>", unsafe_allow_html=True)
        try:
            r = requests.post(f"{BACKEND_URL}/login", json={"password": pw}, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and r.json().get("success"):
                st.session_state.ok = True
                st.session_state.waiting_for_nash = False
                # --- CORREÇÃO: REMOVIDA a linha abaixo ---
                # st.session_state.login_pw = ""
                pw_placeholder.empty()
                loading_placeholder_login.empty()
                button_placeholder.empty()
                st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                st.balloons()
                time.sleep(1.5)
                st.rerun()
            else:
                st.session_state.waiting_for_nash = False
                loading_placeholder_login.empty()
                st.error(f"Falha na autenticação. Acesso negado. (Status: {r.status_code})")

        except requests.exceptions.RequestException as e:
            st.session_state.waiting_for_nash = False
            loading_placeholder_login.empty()
            st.error(f"Erro de rede durante a autenticação: {e}")
        except Exception as e:
            st.session_state.waiting_for_nash = False
            loading_placeholder_login.empty()
            st.error(f"Ocorreu um erro inesperado: {e}")

    if not st.session_state.ok:
        st.stop()


# --- Sidebar Reorganizada e Refinada (Com Seletor de Tema) --- #
with st.sidebar:
    st.markdown("### 🎨 Aparência")
    # Seletor de Tema
    selected_theme = st.selectbox(
        "Escolha o tema da interface:",
        options=list(THEMES.keys()),
        key="selected_theme_widget", # Chave diferente do estado para evitar conflito
        index=list(THEMES.keys()).index(st.session_state.selected_theme), # Define o valor inicial
        help="Mude a aparência visual do Nash Copilot."
    )
    # Atualiza o estado se a seleção mudar (o widget já força rerun)
    if selected_theme != st.session_state.selected_theme:
         st.session_state.selected_theme = selected_theme
         st.rerun() # Força rerun para aplicar o novo CSS imediatamente

    st.markdown("---", unsafe_allow_html=True)

    # 1. Sinais do Cockpit
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic" title="Lembrete Visual">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42" title="A Resposta.">{sign_42_text}</div>""", unsafe_allow_html=True)

    st.markdown("---", unsafe_allow_html=True)

    # 2. Uplink de Dados
    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo ao Próximo Comando",
        type=[ "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg", "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml", "mp3", "wav", "ogg", "mp4", "mov", "avi"],
        key="file_uploader", label_visibility="visible",
        help="Faça o upload de um arquivo que Nash possa analisar junto com seu próximo comando."
    )
    # Lógica de Upload (sem alterações)
    upload_status_placeholder = st.empty()
    if uploaded is not None:
        if st.session_state.uploaded_file_info != uploaded.name:
            files = {"file": (uploaded.name, uploaded.getvalue())}
            try:
                with st.spinner(f"Transmitindo '{uploaded.name}'..."):
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    st.session_state.uploaded_file_info = uploaded.name
                    upload_status_placeholder.success(f"🛰️ '{uploaded.name}' recebido!")
                else:
                    st.session_state.uploaded_file_info = None
                    upload_status_placeholder.error(f"Falha ({r.status_code}).")
            except requests.exceptions.Timeout: st.session_state.uploaded_file_info = None; upload_status_placeholder.error("Timeout Upload.")
            except requests.exceptions.RequestException as e: st.session_state.uploaded_file_info = None; upload_status_placeholder.error(f"Rede Upload: {e}")
            except Exception as e: st.session_state.uploaded_file_info = None; upload_status_placeholder.error(f"Erro Upload: {e}")
    elif uploaded is None and st.session_state.uploaded_file_info:
         st.session_state.uploaded_file_info = None
         upload_status_placeholder.info("Nenhum arquivo anexado.")
    if st.session_state.uploaded_file_info:
        current_status_message = upload_status_placeholder.info(f"Pronto: `{st.session_state.uploaded_file_info}`")

    st.markdown("---", unsafe_allow_html=True)

    # 3. Controles da Sessão
    st.markdown("### ⚙️ Controles")
    # Adicionado CSS class para estilização específica do tema
    if st.button("🗑️ Limpar Log da Sessão", key="clear_chat_btn", help="Apaga todo o histórico de mensagens desta sessão.", use_container_width=True, type="secondary", args=None, kwargs={"class_name": "clear-button"}):
         st.session_state.nash_history = []
         st.session_state.eli_msg_count = 0
         st.session_state.nash_msg_count = 0
         st.toast("🧹 Log da sessão limpo!", icon="✨")
         st.rerun()

    st.markdown("---", unsafe_allow_html=True)

    # 4. Perfil Nash
    st.markdown("### 🧠 Perfil Núcleo Nash")
    tooltip_recurso = clean_markdown("Nash tem acesso a uma vasta gama de dados e APIs, incluindo busca na web, geração de imagens (DALL-E), análise de dados e mais, dependendo da configuração do backend.")
    st.markdown(
        f"""
        Designação: **Nash**
        Classe: IA Copiloto Digital
        Memória: Vetorizada
        Recurso: <span title="{tooltip_recurso}">Todos™</span>
        Status: **{'Online' if current_backend_status.startswith('ONLINE') else 'Limitado'}**
        """, unsafe_allow_html=True
        )

# --- Área Principal de Chat ---
st.markdown("### 🎙️ Console de Comando — Nash AI")
prompt = st.text_area(
    "Insira comando ou consulta para Nash:", key="nash_prompt", height=110,
    placeholder="Digite seu comando aqui, Capitão... Anexou um arquivo? Nash o verá.",
)

# --- Indicador de Loading para Resposta do Nash ---
loading_placeholder_main = st.empty()
if st.session_state.waiting_for_nash:
    loading_placeholder_main.markdown("<div class='loading-indicator'>Nash está processando seu comando...</div>", unsafe_allow_html=True)

# --- Efeito de Typing nas Respostas (Ajustado para não processar st.code) ---
def nash_typing(plain_text, target_placeholder, avatar_class, message_class):
    """Renderiza texto simples com efeito de digitação."""
    full_render = ""
    lines = plain_text.split('\n')
    try:
        for line_index, line in enumerate(lines):
            line_output = ""
            for char_index, char in enumerate(line):
                line_output += char
                cursor = "█"
                safe_line_output = line_output.replace('<', '<').replace('>', '>')
                safe_full_render = full_render.replace('<', '<').replace('>', '>')
                current_render = safe_full_render + safe_line_output + cursor
                target_placeholder.markdown(f"<span class='{avatar_class}'>{'👨‍🚀' if avatar_class=='avatar-nash' else '🧑‍🚀'} Nash:</span><br><span class='{message_class}'>{current_render}</span>", unsafe_allow_html=True)
                delay = 0.005 if char == ' ' else (0.05 if char in ['.', ',', '!', '?'] else 0.018)
                time.sleep(delay)

            full_render += line + "\n"
            safe_full_render = full_render.replace('<', '<').replace('>', '>')
            target_placeholder.markdown(f"<span class='{avatar_class}'>{'👨‍🚀' if avatar_class=='avatar-nash' else '🧑‍🚀'} Nash:</span><br><span class='{message_class}'>{safe_full_render}</span>", unsafe_allow_html=True)
            if line_index < len(lines) - 1: time.sleep(0.1)

        safe_msg = plain_text.replace('<', '<').replace('>', '>')
        target_placeholder.markdown(f"<span class='{avatar_class}'>{'👨‍🚀' if avatar_class=='avatar-nash' else '🧑‍🚀'} Nash:</span><br><span class='{message_class}'>{safe_msg}</span>", unsafe_allow_html=True)
    except Exception as e:
        safe_msg = plain_text.replace('<', '<').replace('>', '>')
        target_placeholder.markdown(f"<span class='{avatar_class}'>{'👨‍🚀' if avatar_class=='avatar-nash' else '🧑‍🚀'} Nash:</span><br><span class='{message_class}'>[Erro typing] {safe_msg}</span>", unsafe_allow_html=True)
        print(f"Erro durante nash_typing: {e}") # Log do erro

# --- Enviar Mensagem para Backend (Com Loading State) ---
transmit_button_placeholder = st.empty()
if transmit_button_placeholder.button("Transmitir para Nash 🚀", key="chat_btn", disabled=st.session_state.waiting_for_nash):
    current_prompt = st.session_state.get("nash_prompt", "")
    if current_prompt:
        st.session_state.nash_history.append(("Eli", current_prompt))
        st.session_state.eli_msg_count += 1
        st.session_state.waiting_for_nash = True
        st.session_state.clear_prompt_on_next_run = True
        loading_placeholder_main.empty()
        transmit_button_placeholder.empty()
        st.rerun()
    else:
        st.warning("Não posso transmitir um comando vazio, Eli.")
        st.session_state.waiting_for_nash = False

# --- Lógica de Comunicação com Backend (Executada após o rerun do botão 'Transmitir') ---
if st.session_state.waiting_for_nash and st.session_state.ok:
    last_eli_prompt = ""
    if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli":
         last_eli_prompt = st.session_state.nash_history[-1][1]

    if last_eli_prompt:
        try:
            req = requests.post(f"{BACKEND_URL}/chat", json={"prompt": last_eli_prompt,"session_id": "eli"}, timeout=REQUEST_TIMEOUT)
            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras...")
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
            else:
                error_msg = f"[Erro {req.status_code}: {req.text[:100]}...]"
                st.session_state.nash_history.append(("Nash", error_msg))
                st.session_state.nash_msg_count += 1
                st.error(f"Erro ao comunicar com Nash. Status: {req.status_code}.")
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
            st.error(f"Ocorreu um erro inesperado: {e}")
        finally:
            st.session_state.waiting_for_nash = False
            st.rerun() # Rerun para mostrar a resposta/erro e limpar o prompt
    else:
        st.warning("Erro interno: Não foi possível encontrar o último comando.")
        st.session_state.waiting_for_nash = False
        st.rerun()

# --- Easter Eggs e Comandos Especiais (Cliente) ---
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

# --- Exibir Histórico de Chat (Com Renderização de Código) ---
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

            # Renderizar avatar primeiro
            st.markdown(f"<span class='{avatar_class}'>{avatar_icon} {who}:</span>", unsafe_allow_html=True)

            # --- Lógica de Renderização: Texto e Código ---
            # Usar regex para encontrar blocos de código ```linguagem \n código ``` ou ``` código ```
            code_pattern = re.compile(r"```(\w+)?\s*\n(.*?)\n```|```(.*?)```", re.DOTALL | re.MULTILINE)
            last_end = 0
            is_last_message = (i == last_message_index)
            is_typing_message = (who == "Nash" and is_last_message and not st.session_state.waiting_for_nash)

            # Se for a última mensagem de Nash e não estiver esperando, preparar placeholder para typing
            typing_placeholder = st.empty() if is_typing_message else None
            message_content_placeholder = st.empty() # Placeholder geral para conteúdo não-typing

            has_code_blocks = False # Flag para saber se fazemos typing ou não

            for match in code_pattern.finditer(msg):
                has_code_blocks = True
                start, end = match.span()

                # 1. Renderizar texto ANTES do bloco de código
                plain_text_before = msg[last_end:start].strip()
                if plain_text_before:
                    safe_plain_text = plain_text_before.replace('<', '<').replace('>', '>')
                    if is_typing_message and typing_placeholder:
                         # Se for typing, renderizar texto antes com typing
                         nash_typing(plain_text_before, typing_placeholder, avatar_class, message_class)
                         typing_placeholder = st.empty() # Novo placeholder para o próximo segmento
                    else:
                         # Renderizar texto normal estático
                         message_content_placeholder.markdown(f"<span class='{message_class}'>{safe_plain_text}</span>", unsafe_allow_html=True)
                         message_content_placeholder = st.empty() # Novo placeholder

                # 2. Extrair e Renderizar o Bloco de Código
                lang = match.group(1) or match.group(3) # Linguagem (pode ser None)
                code = match.group(2) or match.group(4) # Código

                if code:
                    # Usar st.code para renderizar o bloco de código (já tem botão de copiar)
                    # Não usamos placeholder aqui, st.code é um elemento próprio
                    st.code(code, language=lang.lower() if lang else None)

                last_end = end

            # 3. Renderizar texto DEPOIS do último bloco de código (ou todo o texto se não houver blocos)
            plain_text_after = msg[last_end:].strip()
            if plain_text_after:
                 safe_plain_text = plain_text_after.replace('<', '<').replace('>', '>')
                 if is_typing_message and typing_placeholder:
                     nash_typing(plain_text_after, typing_placeholder, avatar_class, message_class)
                 else:
                     # Renderizar texto normal estático no placeholder atual
                     message_content_placeholder.markdown(f"<span class='{message_class}'>{safe_plain_text}</span>", unsafe_allow_html=True)

            # Se a mensagem inteira não tinha blocos de código E era para ser typing
            if not has_code_blocks and is_typing_message and typing_placeholder:
                 nash_typing(msg, typing_placeholder, avatar_class, message_class)
            elif not has_code_blocks and not is_typing_message:
                 # Renderiza a mensagem inteira que não tinha código e não era typing
                 safe_msg_full = msg.replace('<', '<').replace('>', '>')
                 message_content_placeholder.markdown(f"<span class='{message_class}'>{safe_msg_full}</span>", unsafe_allow_html=True)


            # Adiciona divisor
            if i < last_message_index:
                st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.waiting_for_nash: # Mostra apenas se não houver histórico E não estiver carregando
    st.markdown("> *Console aguardando o primeiro comando...*")