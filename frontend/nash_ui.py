# --- START OF FILE nash_ui.py ---

import streamlit as st
import requests
import time
import random
import re
import html
from datetime import datetime, timedelta

# --- Constantes ---
BACKEND_URL = "https://nashcopilot-production.up.railway.app" # Certifique-se que está correto
REQUEST_TIMEOUT = (5, 90) # Aumentado o read timeout para 90s
MAX_PROMPT_DISPLAY_LEN = 50 # Para o indicador de loading

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
    padding-bottom: 5rem; /* Add padding to bottom to prevent overlap with input */
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
/* Botão Regenerar */
.stButton.regenerate-button>button {
    border-color: #87cefa70; color: #add8e6; box-shadow: 0 0 8px #87cefa20;
    padding: 0.2rem 0.5rem; font-size: 0.8em; margin-left: 10px;
}
.stButton.regenerate-button>button:hover {
    border-color: #87cefa; background: #1f3d4d; box-shadow: 0 0 15px #87cefa60; color: #ffffff;
}

/* --- Área de Input e Contador --- */
.stTextArea textarea {
    background: #101225 !important; color: #d8e0ff !important; border: 1px solid #0affa040 !important;
    border-radius: 5px !important; box-shadow: inset 0 0 10px #00000060; font-size: 1.05em; padding: 10px 12px;
}
.stTextArea textarea:focus { border-color: #0affa0 !important; box-shadow: 0 0 12px #0affa040; }
::-webkit-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
::-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-ms-input-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
:-moz-placeholder { color: #0affa0 !important; opacity: 0.5 !important; }
.char-counter { font-size: 0.85em; color: #0affa0a0; text-align: right; margin-top: -8px; margin-right: 5px; }


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
    color: #ff07e6; text-shadow: none; border-bottom: 1px solid #ff07e640; padding-bottom: 5px; margin-bottom: 18px;
}

/* --- Avatares e Mensagens no Chat --- */
.avatar-container { display: flex; flex-direction: column; align-items: center; }
.avatar-name { font-size: 0.9em; margin-top: -5px; display: block; }
.message-timestamp { font-size: 0.75em; color: #9aabb3; opacity: 0.7; margin-top: 3px; display: block; }

.avatar-nash, .avatar-eli {
    font-weight:bold; filter: drop-shadow(0 0 6px); display: block; margin-bottom: 4px;
    font-size: 1.2em; /* Tamanho do emoji/icon */
}
.avatar-nash { color:#0affa0; }
.avatar-eli { color:#ff07e6; }

.message-container { display: flex; align-items: flex-start; } /* Align button with text */

.message-nash {
    color: #e0e8ff; /* COR PADRÃO: Texto claro de alto contraste */
    border-left: 3px solid #0affa070;
    display: inline-block; padding: 5px 10px; border-radius: 5px;
    background-color: rgba(10, 255, 160, 0.08); /* FUNDO NOVO: Leve brilho verde */
    margin-top: 0; line-height: 1.5; text-shadow: none;
    white-space: pre-wrap;
    word-wrap: break-word;
    flex-grow: 1; /* Allow message text to take available space */
}
.message-eli {
    color: #e0e8ff; /* COR PADRÃO: Texto claro de alto contraste */
    border-left: 3px solid #ff07e670;
    display: inline-block; padding: 5px 10px; border-radius: 5px;
    background-color: rgba(255, 7, 230, 0.08); /* FUNDO NOVO: Leve brilho rosa */
    margin-top: 0; line-height: 1.5; text-shadow: none;
    white-space: pre-wrap;
    word-wrap: break-word;
    flex-grow: 1;
}
.message-nash a, .message-eli a {
    color: #87cefa; /* Link color */
    text-decoration: underline; text-decoration-style: dashed; text-underline-offset: 3px;
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
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stDownloadButton { /* Added DownloadButton */
    margin-bottom: 0.35rem;
}
.stSidebar .stButton, .stSidebar .stDownloadButton { margin-top: 0.5rem; } /* Added DownloadButton */
/* Style Download Button like others */
.stDownloadButton>button {
    color: #e0e8ff; background: #1f243d; border-radius: 8px; border: 2px solid #0affa070;
    font-weight: bold; transition: all 0.3s ease; box-shadow: 0 0 10px #0affa020; padding: 0.4rem 0.8rem;
    width: 100%; /* Make it full width */
}
.stDownloadButton>button:hover { background: #2a3050; border-color: #0affa0; box-shadow: 0 0 18px #0affa060; color: #ffffff; }

.nash-profile-details {
    font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #c8d3ff;
}

/* --- Sinais Neon --- */
.sidebar-sign {
    font-family: 'Orbitron', 'Fira Mono', monospace; font-weight: bold; padding: 8px 15px; margin: 9px auto;
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
.loading-indicator span { /* Style the prompt text */
    opacity: 0.8;
    margin-left: 5px;
    font-style: italic;
}

/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 14px; }
    section.main > div { padding-bottom: 6rem; } /* More padding on mobile */
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
    /* Ensure chat columns have less gap on mobile */
    .st-emotion-cache-ocqkz7 { gap: 0.3rem !important; } /* Adjust based on Streamlit version/class */
    .avatar-name { font-size: 0.8em; }
    .message-timestamp { font-size: 0.7em; }
    .stButton.regenerate-button>button { font-size: 0.75em; padding: 0.15rem 0.4rem; margin-left: 5px; }
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
    padding-bottom: 5rem; /* Add padding to bottom to prevent overlap with input */
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
/* Botão Regenerar */
.stButton.regenerate-button>button {
    border-color: #adb5bd; color: #495057; background: #f8f9fa; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    padding: 0.2rem 0.5rem; font-size: 0.8em; margin-left: 10px; border-width: 1px;
}
.stButton.regenerate-button>button:hover {
    border-color: #6c757d; background: #e9ecef; color: #212529;
}

/* --- Área de Input e Contador --- */
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
.char-counter { font-size: 0.85em; color: #6c757d; text-align: right; margin-top: -8px; margin-right: 5px; }

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
.avatar-container { display: flex; flex-direction: column; align-items: center; }
.avatar-name { font-size: 0.9em; margin-top: -5px; display: block; }
.message-timestamp { font-size: 0.75em; color: #6c757d; opacity: 0.8; margin-top: 3px; display: block; }

.avatar-nash, .avatar-eli {
    font-weight:bold; filter: none; display: block; margin-bottom: 4px;
    font-size: 1.2em; /* Tamanho do emoji/icon */
}
.avatar-nash { color:#0a58ca; }
.avatar-eli { color:#d63384; } /* Cor do nome Eli mantida */

.message-container { display: flex; align-items: flex-start; }

.message-nash {
    color: #212529; /* COR PADRÃO: Texto escuro de alto contraste */
    background-color: #e9ecef; /* FUNDO NOVO: Cinza claro padrão (ligeiramente mais escuro) */
    display: inline-block; padding: 6px 12px; border-radius: 15px;
    margin-top: 0; line-height: 1.5; text-shadow: none; border-left: none;
    white-space: pre-wrap;
    word-wrap: break-word;
    flex-grow: 1;
}
.message-eli {
    color: #212529; /* COR PADRÃO: Texto escuro de alto contraste */
    background-color: #f8f0fc; /* FUNDO NOVO: Roxo bem claro para distinção */
    display: inline-block; padding: 6px 12px; border-radius: 15px;
    margin-top: 0; line-height: 1.5; text-shadow: none; border-left: none;
    white-space: pre-wrap;
    word-wrap: break-word;
    flex-grow: 1;
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
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton, .stSidebar .stSelectbox, .stSidebar .stDownloadButton { /* Added DownloadButton */
     margin-bottom: 0.8rem;
}
.stSidebar .stButton, .stSidebar .stDownloadButton { margin-top: 0.5rem; } /* Added DownloadButton */
/* Style Download Button like others */
.stDownloadButton>button {
    color: #ffffff; background: #0d6efd; border-radius: 5px; border: 1px solid #0d6efd;
    font-weight: normal; transition: all 0.2s ease; box-shadow: 0 1px 2px rgba(0,0,0,0.1); padding: 0.35rem 0.75rem;
    font-family: 'Roboto', sans-serif;
    width: 100%; /* Make it full width */
}
.stDownloadButton>button:hover { background: #0b5ed7; border-color: #0a58ca; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #ffffff; }


.nash-profile-details {
    font-size: 0.9em; line-height: 1.4; margin-top: -5px; color: #495057;
}

/* --- Sinais (Sidebar) --- */
.sidebar-sign {
     font-family: 'Roboto', sans-serif; font-weight: bold; padding: 6px 12px; margin: 9px auto;
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
.loading-indicator span { /* Style the prompt text */
    opacity: 0.8;
    margin-left: 5px;
    font-style: italic;
}


/* --- Mobile Responsiveness --- */
@media (max-width: 768px) {
    body { font-size: 15px; }
    section.main > div { padding-bottom: 6rem; } /* More padding on mobile */
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
    /* Ensure chat columns have less gap on mobile */
    .st-emotion-cache-ocqkz7 { gap: 0.3rem !important; } /* Adjust based on Streamlit version/class */
    .avatar-name { font-size: 0.8em; }
    .message-timestamp { font-size: 0.7em; }
    .stButton.regenerate-button>button { font-size: 0.75em; padding: 0.15rem 0.4rem; margin-left: 5px; }
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
    "nash_history": [],           # Stores tuples of (who, message_text, timestamp)
    "eli_msg_count": 0,
    "nash_msg_count": 0,
    "nash_welcome": True,
    "ok": False,                  # Login status
    "backend_status": "VERIFICANDO...",
    "last_backend_check": datetime.min,
    "waiting_for_nash": False,    # Flag to disable input/buttons during backend call
    "uploaded_file_info": None,   # Stores name of successfully uploaded file
    "selected_theme": "Cyberpunk",
    "scroll_to_bottom": False,    # Flag to trigger JS scroll
    "prompt_to_regenerate": None, # Stores the prompt when user clicks regenerate
    "current_prompt": ""          # Store current text input value
}

# Initialize missing keys
for key, default_value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

# Backward compatibility for history format (if upgrading from previous state)
if st.session_state.nash_history and len(st.session_state.nash_history[0]) == 2:
    st.toast("Atualizando formato do histórico...", icon="⏳")
    st.session_state.nash_history = [
        (who, msg, st.session_state.start_time) # Add a default timestamp
        for who, msg in st.session_state.nash_history
    ]
    time.sleep(1) # Allow toast to show

# -----------------------------------------------------------------------

# --- Funções Auxiliares ---
def check_backend_status(force_check=False):
    """Verifica o status do backend com cache."""
    now = datetime.now()
    # Cache status for 60 seconds unless forced
    if not force_check and (now - st.session_state.last_backend_check) < timedelta(seconds=60):
        return st.session_state.backend_status
    try:
        # Check root or a dedicated health endpoint like /health
        r = requests.get(f"{BACKEND_URL}/", timeout=REQUEST_TIMEOUT[0]) # connect timeout only
        status = "ONLINE ⚡" if r.status_code == 200 else f"AVISO {r.status_code}"
    except requests.exceptions.Timeout: status = "TIMEOUT ⏳"
    except requests.exceptions.ConnectionError: status = "OFFLINE 👾"
    except Exception as e:
        print(f"Backend Check Error: {e}") # Log unexpected errors
        status = "ERRO ⁉️"
    st.session_state.backend_status = status
    st.session_state.last_backend_check = now
    return status

def clean_markdown(text):
    """Remove formatação básica e escapa aspas para tooltips."""
    text = re.sub(r'[\*_`]', '', text) # Remove *, _, `
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text) # Remove links but keep text
    text = text.replace('"', '"') # Escape quotes for HTML attributes
    return text

def escape_html(text: str) -> str:
    """Escapa caracteres HTML antes de injetar no Streamlit."""
    if not isinstance(text, str):
        text = str(text)
    # Escape &, <, > by default. quote=False prevents escaping "
    return html.escape(text, quote=False)

def format_history_for_export(history):
    """Formats chat history for text/markdown export."""
    lines = ["# Log da Sessão Nash Copilot\n\n"]
    for who, msg, ts in history:
        timestamp_str = ts.strftime('%Y-%m-%d %H:%M:%S')
        prefix = f"[{timestamp_str}] {who}:"
        # Indent message content for readability
        formatted_msg = "\n".join(["  " + line for line in msg.splitlines()])
        lines.append(f"{prefix}\n{formatted_msg}\n")
    return "\n".join(lines)

# --- Aplica o Tema Selecionado ---
selected_theme_css = THEMES.get(st.session_state.selected_theme, CYBERPUNK_CSS)
st.markdown(selected_theme_css, unsafe_allow_html=True)

# --- Lógica para Limpar o Prompt (Executada no início do script) ---
# This is now implicitly handled by setting st.session_state.current_prompt = ""
# after a successful transmission, if needed. Let's remove the explicit flag.
# The `value=st.session_state.current_prompt` in text_area handles it.

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
# Format uptime nicely (HH:MM:SS)
uptime_str = str(timedelta(seconds=int(uptime_delta.total_seconds())))
ascii_art = f"""
> Status: <b>{ ('Operacional' if current_backend_status.startswith('ONLINE') else 'Parcial') if st.session_state.ok else 'Bloqueado'}</b> | Humor: Sarcástico IV
> Temp. Núcleo: <b>Nominal</b> | Matriz Lógica: Ativa
> Missão: <b>Dominar o Universo</b> | Diretriz: Sobreviver
""".strip()
safe_ascii_art = escape_html(ascii_art)
# Re-apply <b> tags after escaping other HTML
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
    # Use session state to preserve input value across reruns during login attempt
    pw_value = st.session_state.get("login_pw_input_value", "")
    pw = pw_placeholder.text_input(
        "Insira o Código de Autorização de Comando:",
        type="password",
        key="login_pw_widget", # Consistent key
        value=pw_value,
        on_change=lambda: st.session_state.update(login_pw_input_value=st.session_state.login_pw_widget) # Update state on change
    )

    button_placeholder = st.empty()
    if button_placeholder.button("Autenticar 🛰️", key="login_btn", disabled=st.session_state.waiting_for_nash):
        current_input_pw = st.session_state.login_pw_input_value # Use the value from session state
        if not current_input_pw:
            st.warning("O código de autorização não pode estar vazio.")
            st.session_state.waiting_for_nash = False # Ensure not stuck waiting
        else:
            st.session_state.waiting_for_nash = True
            # Store the password to be verified in session state so it survives the rerun
            st.session_state.login_pw_to_verify = current_input_pw
            button_placeholder.empty() # Clear button immediately
            st.rerun() # Rerun to show loading and process login

    # This block runs *after* the rerun triggered by the button click
    if st.session_state.waiting_for_nash and "login_pw_to_verify" in st.session_state:
        loading_placeholder_login = st.empty()
        loading_placeholder_login.markdown("<div class='loading-indicator'>Autenticando com a Nave Mãe...</div>", unsafe_allow_html=True)
        login_pw_to_check = st.session_state.login_pw_to_verify
        login_success = False
        try:
            r = requests.post(f"{BACKEND_URL}/login", json={"password": login_pw_to_check}, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and r.json().get("success"):
                st.session_state.ok = True
                login_success = True
                st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                st.balloons()
                # Clean up login state variables
                if "login_pw_input_value" in st.session_state: del st.session_state.login_pw_input_value
                if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
                pw_placeholder.empty()
                button_placeholder.empty() # Ensure button placeholder is cleared if rerun happens later
                loading_placeholder_login.empty()
            else:
                 # Try to get error detail from backend response
                 try:
                     error_detail = r.json().get("error", f"Status {r.status_code}")
                 except (ValueError, requests.exceptions.JSONDecodeError):
                     error_detail = f"Status {r.status_code}, Resposta não-JSON: {r.text[:100]}"
                 st.error(f"Falha na autenticação: {escape_html(error_detail)}")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro de rede durante a autenticação: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado na autenticação: {e}")
        finally:
            st.session_state.waiting_for_nash = False
            # Clean up verification password regardless of success/failure if not already done
            if "login_pw_to_verify" in st.session_state: del st.session_state.login_pw_to_verify
            loading_placeholder_login.empty() # Ensure loading is cleared
            if login_success:
                time.sleep(1.5) # Brief pause before clearing screen
                st.rerun() # Rerun to show the main chat interface

    # If still not ok after attempts, stop execution for this run
    if not st.session_state.ok:
        st.stop()


# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🎨 Aparência")
    theme_options = list(THEMES.keys())
    current_theme_index = theme_options.index(st.session_state.selected_theme) if st.session_state.selected_theme in theme_options else 0
    selected_theme_name = st.selectbox(
        "Escolha o tema da interface:",
        options=theme_options,
        key="selected_theme_widget",
        index=current_theme_index,
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
        type=[ # Expanded list
            "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
            "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml", "html", "css", "js",
            "mp3", "wav", "ogg", "flac",
            "mp4", "mov", "avi", "mkv",
            "doc", "docx", "xls", "xlsx", "ppt", "pptx", "rtf"
            ],
        key="file_uploader", # Keep key consistent
        label_visibility="visible",
        help="Faça o upload de um arquivo que Nash possa analisar junto com seu próximo comando."
    )
    upload_status_placeholder = st.empty()

    # Handle file upload logic
    if uploaded is not None:
        # Check if it's a new file or the same file re-uploaded
        if st.session_state.uploaded_file_info != uploaded.name:
            files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
            try:
                with upload_status_placeholder, st.spinner(f"Transmitindo '{escape_html(uploaded.name)}'..."):
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT)
                if r.status_code == 200:
                    st.session_state.uploaded_file_info = uploaded.name # Store only name for simplicity
                    upload_status_placeholder.success(f"🛰️ '{escape_html(uploaded.name)}' recebido! Será incluído no próximo comando.")
                else:
                    st.session_state.uploaded_file_info = None
                    upload_status_placeholder.error(f"Falha no upload ({r.status_code}): {escape_html(r.text)}")
            except requests.exceptions.Timeout:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error("Timeout durante o upload.")
            except requests.exceptions.RequestException as e:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error(f"Erro de rede no upload: {e}")
            except Exception as e:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error(f"Erro inesperado no upload: {e}")

    # If uploader is cleared (no file selected), reset state
    elif uploaded is None and st.session_state.uploaded_file_info:
         st.session_state.uploaded_file_info = None
         upload_status_placeholder.empty() # Clear any previous message

    # If a file was successfully uploaded previously and is still the active one
    if st.session_state.uploaded_file_info and uploaded is not None and uploaded.name == st.session_state.uploaded_file_info:
         upload_status_placeholder.info(f"Pronto para anexar: `{escape_html(st.session_state.uploaded_file_info)}`")


    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### ⚙️ Controles")
    if st.button("🗑️ Limpar Log da Sessão", key="clear_chat_btn", help="Apaga todo o histórico de mensagens desta sessão.", use_container_width=True):
         st.session_state.nash_history = []
         st.session_state.eli_msg_count = 0
         st.session_state.nash_msg_count = 0
         st.session_state.uploaded_file_info = None # Clear uploaded file info on session clear
         st.session_state.current_prompt = "" # Clear prompt area too
         st.toast("🧹 Log da sessão limpo!", icon="✨")
         st.rerun()

    # --- Export Button ---
    if st.session_state.nash_history:
        export_data = format_history_for_export(st.session_state.nash_history)
        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="📄 Exportar Chat (.md)",
            data=export_data,
            file_name=f"nash_chatlog_{current_time_str}.md",
            mime="text/markdown",
            use_container_width=True,
            help="Baixar o histórico completo desta sessão como um arquivo Markdown."
        )

    st.markdown("---", unsafe_allow_html=True)

    st.markdown("### 🧠 Perfil Núcleo Nash")
    tooltip_recurso = clean_markdown("Nash tem acesso a uma vasta gama de dados e APIs para auxiliar nas suas tarefas.")
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

# Use a container for the input area + button for better layout control if needed
input_area = st.container()
with input_area:
    # Update session state variable directly when text_area changes
    st.text_area(
        "Insira comando ou consulta para Nash:",
        key="nash_prompt_widget", # Unique key for the widget
        height=110,
        placeholder="Digite seu comando aqui, Capitão...",
        value=st.session_state.current_prompt, # Bind value to session state
        on_change=lambda: st.session_state.update(current_prompt=st.session_state.nash_prompt_widget) # Update state on change
    )
    # Display character count
    char_count = len(st.session_state.current_prompt)
    st.markdown(f"<div class='char-counter'>{char_count} caracteres</div>", unsafe_allow_html=True)

    # --- Enviar Mensagem Button ---
    if st.button("Transmitir para Nash 🚀", key="chat_btn", disabled=st.session_state.waiting_for_nash or not st.session_state.ok):
        prompt_to_send = st.session_state.current_prompt
        if prompt_to_send:
            # Add message to history with timestamp
            st.session_state.nash_history.append(("Eli", prompt_to_send, datetime.now()))
            st.session_state.eli_msg_count += 1
            st.session_state.waiting_for_nash = True
            st.session_state.current_prompt = "" # Clear input area AFTER getting value
            st.session_state.scroll_to_bottom = True # Signal to scroll
            st.session_state.prompt_to_regenerate = None # Clear regenerate flag if user sends new prompt
            st.rerun() # Rerun starts new cycle
        else:
            st.warning("Não posso transmitir um comando vazio, Eli.")
            st.session_state.waiting_for_nash = False


# --- Lógica de Comunicação com Backend ---
prompt_for_backend = None
is_regenerating = False

if st.session_state.waiting_for_nash and st.session_state.ok:
    # Check if we are regenerating
    if st.session_state.prompt_to_regenerate:
        prompt_for_backend = st.session_state.prompt_to_regenerate
        is_regenerating = True
        st.session_state.prompt_to_regenerate = None # Consume the flag
    # Otherwise, get the last Eli prompt from history
    elif st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli":
         prompt_for_backend = st.session_state.nash_history[-1][1]
    else:
        # Should not happen if button logic is correct, but handle defensively
        st.warning("Erro interno: Não foi possível encontrar o último comando de Eli.")
        st.session_state.waiting_for_nash = False
        st.rerun() # Rerun to clear state

    # --- Display Loading Indicator (Improved) ---
    loading_placeholder_main = st.empty()
    if prompt_for_backend:
        truncated_prompt = prompt_for_backend[:MAX_PROMPT_DISPLAY_LEN]
        if len(prompt_for_backend) > MAX_PROMPT_DISPLAY_LEN:
            truncated_prompt += "..."
        loading_text = f"Nash está processando: <span>'{escape_html(truncated_prompt)}'</span>"
        loading_placeholder_main.markdown(f"<div class='loading-indicator'>{loading_text}</div>", unsafe_allow_html=True)

    # --- Call Backend ---
    if prompt_for_backend:
        try:
            payload = {"prompt": prompt_for_backend, "session_id": "eli"} # Assuming session_id is static
            # Include file info if present (even during regeneration if relevant)
            if st.session_state.uploaded_file_info:
                payload["attachment_info"] = {"filename": st.session_state.uploaded_file_info}

            req = requests.post(f"{BACKEND_URL}/chat", json=payload, timeout=REQUEST_TIMEOUT)

            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras…")
                # Add Nash's response with timestamp
                st.session_state.nash_history.append(("Nash", resp, datetime.now()))
                st.session_state.nash_msg_count += 1
            else:
                # Try to get detailed error message
                try:
                    error_payload = req.json().get("error", req.text)
                except (ValueError, requests.exceptions.JSONDecodeError): # If response is not JSON
                    error_payload = req.text
                error_msg = f"[Erro {req.status_code} do Backend: {escape_html(str(error_payload)[:150])}]" # Limit length
                st.session_state.nash_history.append(("Nash", error_msg, datetime.now())) # Still log error as Nash msg
                st.session_state.nash_msg_count += 1
                st.error(f"Erro ao comunicar com Nash — código {req.status_code}.")

        except requests.exceptions.Timeout:
            error_msg = "[Erro Cliente: Timeout na resposta de Nash]"
            st.session_state.nash_history.append(("Nash", error_msg, datetime.now()))
            st.session_state.nash_msg_count += 1
            st.error("Requisição para Nash expirou (timeout).")
        except requests.exceptions.RequestException as e:
            error_msg = f"[Erro Cliente: Rede - {escape_html(str(e))}]"
            st.session_state.nash_history.append(("Nash", error_msg, datetime.now()))
            st.session_state.nash_msg_count += 1
            st.error(f"Erro de rede ao contactar Nash: {e}")
        except Exception as e:
            error_msg = f"[Erro Cliente: Inesperado - {escape_html(str(e))}]"
            st.session_state.nash_history.append(("Nash", error_msg, datetime.now()))
            st.session_state.nash_msg_count += 1
            st.error(f"Ocorreu um erro inesperado na comunicação local: {e}")
        finally:
            st.session_state.waiting_for_nash = False
            # Clear file only after successful processing associated with a prompt
            if not is_regenerating: # Don't clear file on regenerate unless you re-upload
                 st.session_state.uploaded_file_info = None
            st.session_state.scroll_to_bottom = True # Signal to scroll
            loading_placeholder_main.empty() # Clear loading indicator
            st.rerun() # Rerun to display Nash's response

# --- Efeito de Typing ---
# (Keep the nash_typing function as defined in the previous response - it's needed for history display)
def nash_typing(plain_text, target_placeholder, message_class):
    """Renderiza texto simples com efeito de digitação, escapando HTML corretamente."""
    full_render = ""
    lines = plain_text.split('\n')
    try:
        for line_index, line in enumerate(lines):
            line_output = ""
            processed_line = line.strip() # Process lines for typing
            if not processed_line and line_index < len(lines) - 1: # Handle empty lines
                full_render += "\n"
                # Render the state including the blank line immediately
                full_render_escaped = escape_html(full_render)
                target_placeholder.markdown(f"<span class='{message_class}' style='white-space: pre-wrap;'>{full_render_escaped}</span>", unsafe_allow_html=True)
                time.sleep(0.1) # Small pause for blank lines
                continue

            for char_index, char in enumerate(processed_line):
                line_output += char
                cursor = "█" # Keep cursor visible during typing
                current_render_escaped = escape_html(full_render + line_output) + cursor
                target_placeholder.markdown(f"<span class='{message_class}' style='white-space: pre-wrap;'>{current_render_escaped}</span>", unsafe_allow_html=True)
                delay = 0.005 if char == ' ' else (0.04 if char in ['.', ',', '!', '?'] else 0.015)
                time.sleep(delay)

            full_render += processed_line + ("\n" if line_index < len(lines) - 1 else "")
            full_render_escaped = escape_html(full_render) # Render without cursor after line is done
            target_placeholder.markdown(f"<span class='{message_class}' style='white-space: pre-wrap;'>{full_render_escaped}</span>", unsafe_allow_html=True)
            if line and line_index < len(lines) - 1: time.sleep(0.08) # Pause between non-empty lines

    except Exception as e:
        safe_msg = escape_html(plain_text) # Fallback display
        target_placeholder.markdown(f"<span class='{message_class}' style='white-space: pre-wrap;'>[Erro typing] {safe_msg}</span>", unsafe_allow_html=True)
        print(f"Erro durante nash_typing: {e}")


# --- Exibir Histórico de Chat ---
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")
    history_container = st.container() # Use a container for the history block

    with history_container:
        last_message_index = len(st.session_state.nash_history) - 1
        # Iterate through history (who, msg, timestamp)
        for i, (who, msg, ts) in enumerate(st.session_state.nash_history):
            avatar_class = "avatar-nash" if who == "Nash" else "avatar-eli"
            message_class = "message-nash" if who == "Nash" else "message-eli"
            avatar_icon = "👨‍🚀" if who == "Nash" else "🧑‍🚀" # Eli gets a different emoji
            timestamp_str = ts.strftime('%H:%M:%S') # Format timestamp HH:MM:SS

            col1, col2 = st.columns([1, 15], gap="small")

            # Column 1: Avatar, Name, Timestamp
            with col1:
                 st.markdown(f"<div class='avatar-container'>", unsafe_allow_html=True)
                 st.markdown(f"<span class='{avatar_class}'>{avatar_icon}</span>", unsafe_allow_html=True)
                 st.markdown(f"<span class='avatar-name {avatar_class}'>{who}:</span>", unsafe_allow_html=True)
                 st.markdown(f"<span class='message-timestamp'>{timestamp_str}</span>", unsafe_allow_html=True)
                 st.markdown(f"</div>", unsafe_allow_html=True)

            # Column 2: Message Content and Regenerate Button
            with col2:
                is_last_message = (i == last_message_index)
                apply_typing = (who == "Nash" and is_last_message and not st.session_state.waiting_for_nash and not st.session_state.prompt_to_regenerate)

                # Use a container to allow placing button next to the message content
                msg_content_container = st.container()
                with msg_content_container:
                    # Regex to find ```lang\ncode\n``` or ```code``` blocks
                    code_pattern = re.compile(r"```(\w+)?\s*\n(.*?)\n```|```(.*?)```", re.DOTALL)
                    last_end = 0
                    message_parts = [] # Store parts to render sequentially

                    # 1. Split message into text and code parts
                    for match in code_pattern.finditer(msg):
                        start, end = match.span()
                        text_before = msg[last_end:start]
                        if text_before: message_parts.append({"type": "text", "content": text_before})
                        lang = match.group(1); code = match.group(2)
                        if code is None: code = match.group(3); lang = None
                        if code is not None: message_parts.append({"type": "code", "content": str(code), "lang": lang})
                        last_end = end
                    text_after = msg[last_end:]
                    if text_after: message_parts.append({"type": "text", "content": text_after})

                    # 2. Render the parts sequentially
                    # Wrap message content in a div to align button next to it
                    st.markdown("<div class='message-container'>", unsafe_allow_html=True)
                    for part_idx, part in enumerate(message_parts):
                        if part["type"] == "text":
                            content = part["content"]
                            if content.strip(): # Only render if not just whitespace
                                if apply_typing:
                                    typing_placeholder = st.empty()
                                    nash_typing(content, typing_placeholder, message_class)
                                else:
                                    st.markdown(f"<span class='{message_class}' style='white-space: pre-wrap;'>{escape_html(content)}</span>", unsafe_allow_html=True)
                            # Render whitespace for structure if it exists and isn't the only content
                            elif content and len(message_parts) > 1:
                                st.markdown(f"<span class='{message_class}' style='white-space: pre-wrap; display: block; min-height: 1em;'></span>", unsafe_allow_html=True)
                        elif part["type"] == "code":
                            st.code(part["content"], language=part["lang"].lower() if part["lang"] else None)

                    # --- Regenerate Button Logic ---
                    if who == "Nash" and is_last_message and not st.session_state.waiting_for_nash:
                        # Find the previous Eli prompt to regenerate from
                        eli_prompt_to_regen = None
                        if i > 0 and st.session_state.nash_history[i-1][0] == "Eli":
                            eli_prompt_to_regen = st.session_state.nash_history[i-1][1]

                        if eli_prompt_to_regen:
                             # Use a unique key based on the message index
                             regen_button_key = f"regen_{i}"
                             if st.button("🔄", key=regen_button_key, help="Regenerar esta resposta", type="secondary"):
                                 st.session_state.prompt_to_regenerate = eli_prompt_to_regen
                                 st.session_state.waiting_for_nash = True
                                 st.session_state.scroll_to_bottom = True
                                 # Clear the current Nash message that is being regenerated? Optional.
                                 # st.session_state.nash_history.pop()
                                 st.rerun()

                    st.markdown("</div>", unsafe_allow_html=True) # Close message-container div

            # Add a separator between messages
            if i < last_message_index:
                st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # Close nash-history div

# Display initial message if history is empty and logged in
elif not st.session_state.waiting_for_nash and st.session_state.ok:
    st.markdown("> *Console aguardando o primeiro comando...*")


# --- Easter Eggs (Keep as is or modify) ---
# (Included from previous version, check if still relevant/desired)
# if not st.session_state.waiting_for_nash and st.session_state.nash_history:
#    last_entry = st.session_state.nash_history[-1]
#    if last_entry[0] == 'Eli':
#        last_prompt = last_entry[1].lower()
#        if "data estelar" in last_prompt or ("data" in last_prompt and any(sub in last_prompt for sub in ["hoje", "agora", "hora"])):
#            # ... (toast logic) ...
#        if "auto destruir" in last_prompt or "autodestruir" in last_prompt:
#            # ... (snow logic) ...


# --- Auto-Scroll Logic ---
# Must be placed at the very end of the script execution
if st.session_state.get("scroll_to_bottom", False):
    # JavaScript to scroll the main chat container to the bottom
    # Using time.time() helps ensure the script runs reliably on reruns
    js = f"""
    <script>
        function scroll(dummy_var_to_force_reexecution){{
            // Target the main block container of Streamlit's structure
            var main_block = window.parent.document.querySelector('section.main > div.block-container');
            if (main_block) {{
                window.scrollTo(0, main_block.scrollHeight);
            }} else {{
                // Fallback for older/different Streamlit versions
                window.scrollTo(0, window.parent.document.body.scrollHeight);
            }}
        }}
        // Use setTimeout to ensure rendering is complete before scrolling
        setTimeout(scroll, 150, {time.time()});
    </script>
    """
    st.components.v1.html(js, height=0, scrolling=False)
    st.session_state.scroll_to_bottom = False # Reset the flag

# --- END OF FILE nash_ui.py ---