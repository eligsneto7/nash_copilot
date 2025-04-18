# nash_ui_v7_mobile_contrast_features_fix2.py
import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import random
import re # Importado para limpar markdown em tooltips

# --- Constantes ---
BACKEND_URL = "https://nashcopilot-production.up.railway.app"
REQUEST_TIMEOUT = (5, 65) # (connect timeout, read timeout)

# --- Textos Customizáveis para os Sinais (Mantido) ---
sign_panic_text = "NÃO ENTRE EM PÂNICO"
sign_42_text = "42"
# ------------------------------------------

# --- Inicialização do Estado da Sessão (Refatorado e com Novas Chaves) ---
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
    return text

# --- ESTILO V7 --- #
# (Ajustes finos em cores, contraste, adicionado scanlines e animação de loading)
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

/* --- Animações --- */
@keyframes blink-neon {{
  0%, 100% {{ opacity: 1; text-shadow: 0 0 7px #ff07e6, 0 0 15px #ff07e6, 0 0 20px #ff07e6; }}
  50% {{ opacity: 0.7; text-shadow: 0 0 5px #ff07e6a0, 0 0 10px #ff07e6a0; }}
}}
@keyframes subtle-pulse {{
  0%, 100% {{ opacity: 0.9; }}
  50% {{ opacity: 1; }}
}}
@keyframes scanline {{
  0% {{ background-position: 0 0; }}
  100% {{ background-position: 0 100%; }}
}}
@keyframes thinking-pulse {{
    0% {{ background-color: #0affa030; box-shadow: 0 0 8px #0affa030; }}
    50% {{ background-color: #0affa060; box-shadow: 0 0 15px #0affa070; }}
    100% {{ background-color: #0affa030; box-shadow: 0 0 8px #0affa030; }}
}}

/* --- Body e Geral --- */
body {{
    background: radial-gradient(ellipse at center, #10121f 0%, #0b0c14 70%), linear-gradient(145deg, #0b0c14 70%, #181a29 100%);
    background-attachment: fixed;
    color: #d0d8ff !important; /* Cor base ligeiramente mais clara */
    font-family: 'Fira Mono', 'Consolas', monospace;
    min-height: 100vh !important;
    overflow-x: hidden;
}}
body:before {{
    content: '';
    background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
    opacity: .1; /* Ainda mais sutil */
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
    pointer-events: none; background-size: cover;
}}

/* --- Área Principal --- */
section.main > div {{
    background: linear-gradient(170deg, #0f111a 0%, #1c202f 100%) !important;
    border-radius: 15px;
    border: 1px solid #0aebff30; /* Borda ciano mais sutil */
    box-shadow: 0 0 25px #0aebff10, inset 0 0 20px rgba(0,0,0,0.5);
    /* NOVO: Margem inferior para evitar que o conteúdo cole no fim da tela */
    margin-bottom: 2rem;
}}

/* --- Visor Holográfico --- */
#visor {{
    background:
        linear-gradient(135deg, rgba(16, 18, 37, 0.97) 80%, rgba(255, 7, 230, 0.85) 140%),
        rgba(5, 5, 15, 0.96);
    border-radius: 15px; margin-bottom: 20px; margin-top: -10px;
    border: 2.5px solid #ff07e660; /* Borda magenta mais sutil */
    box-shadow: 0 0 30px #e600c650, inset 0 0 15px #101225e0; /* Sombra ajustada */
    padding: 18px 26px 14px 30px;
    display: flex; align-items: center; gap: 25px;
}}
.nash-avatar-emoji {{
    font-size: 65px; filter: drop-shadow(0 0 15px #0affa0a0); /* Glow mais suave */
    margin-right: 15px; line-height: 1; animation: subtle-pulse 3s infinite ease-in-out;
}}
.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b {{
    font-family: 'Orbitron', 'Fira Mono', monospace; user-select: none;
}}
.nash-holo {{ font-size: 2.1em; color: #0affa0; text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; margin-bottom: 3px; }}
.nash-enterprise-tag {{ font-size: 0.9em; color: #ff07e6b0; font-family: 'Fira Mono', monospace; }}
.nash-ascii {{ font-family: 'Fira Mono', monospace; color: #0affa0d0; /* Ligeiramente mais brilhante */ letter-spacing: 0.5px; line-height: 115%; font-size: 0.95em; text-shadow: 0 0 8px #0affa040; margin-top: -5px; margin-bottom: 5px; }}
.nash-ascii b {{ color: #ff07e6; font-weight: bold; }}

.visor-analytics {{
    color:#ff07e6; font-size: 0.95em; padding: 0.4em 1.3em;
    background: rgba(10, 10, 25, 0.75); /* Fundo ligeiramente mais opaco */
    border-radius: 8px; border: 1px solid #ff07e650; /* Borda mais sutil */
    margin-top: 10px; line-height: 1.45;
}}
.visor-analytics b {{ color: #ffffff; }}
.visor-analytics i {{ color: #c8d3ff; opacity: 0.85; }} /* Texto da motivação mais visível */

/* --- Botões --- */
.stButton>button {{
    color: #e0e8ff; background: #1f243d; /* Fundo ligeiramente diferente */
    border-radius: 8px; border: 2px solid #0affa070; /* Borda mais sutil */
    font-weight: bold; transition: all 0.3s ease;
    box-shadow: 0 0 10px #0affa020; /* Sombra mais suave */
    padding: 0.4rem 0.8rem; /* Ajuste padding */
}}
.stButton>button:hover {{
    background: #2a3050; border-color: #0affa0;
    box-shadow: 0 0 18px #0affa060; color: #ffffff;
}}
.stButton>button:active {{ background: #15182a; }}
/* Estilo específico para botão de limpar chat */
.stButton.clear-button>button {{
    border-color: #ff07e670; color: #ffc0e8;
    box-shadow: 0 0 10px #ff07e620;
}}
.stButton.clear-button>button:hover {{
    border-color: #ff07e6; background: #3d1f35;
    box-shadow: 0 0 18px #ff07e660; color: #ffffff;
}}

/* --- Área de Input --- */
.stTextArea textarea {{
    background: #101225 !important;
    color: #d8e0ff !important; /* Texto de input mais claro */
    border: 1px solid #0affa040 !important; /* Borda mais sutil */
    border-radius: 5px !important;
    box-shadow: inset 0 0 10px #00000060;
    font-size: 1.05em; /* Ligeiramente maior */
    padding: 10px 12px;
}}
.stTextArea textarea:focus {{
    border-color: #0affa0 !important;
    box-shadow: 0 0 12px #0affa040;
}}
/* Placeholder com contraste melhorado */
::-webkit-input-placeholder {{ color: #0affa0 !important; opacity: 0.5 !important; }}
::-moz-placeholder {{ color: #0affa0 !important; opacity: 0.5 !important; }}
:-ms-input-placeholder {{ color: #0affa0 !important; opacity: 0.5 !important; }}
:-moz-placeholder {{ color: #0affa0 !important; opacity: 0.5 !important; }}

/* --- File Uploader (Sidebar) --- */
.stFileUploader {{
    background: #101225cc !important; /* Fundo semi-transparente */
    border: 1px dashed #0affa050 !important; /* Borda mais sutil */
    border-radius: 8px; padding: 15px; margin-top: 5px; /* Menos margem superior */
}}
.stFileUploader label {{ color: #0affa0b0 !important; font-size: 0.95em; }} /* Cor da label mais suave */
.stFileUploader small {{ color: #0affa070 !important; font-size: 0.8em; }} /* Cor do texto de ajuda mais suave */
/* Esconder o botão de upload padrão (mantém a área clicável) */
.stFileUploader button {{ display: none !important; }}

/* --- Histórico de Chat --- */
#nash-history {{
    background: #0c0e1acc; /* Fundo escuro consistente */
    border-radius: 10px;
    padding: 18px 16px 8px 15px; margin-top: 25px;
    border: 1px solid #0affa030; /* Borda mais sutil */
    /* NOVO: Efeito Scanline Sutil */
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 4px,
        rgba(0, 255, 255, 0.02) 5px, /* Linha ciano muito sutil */
        rgba(0, 255, 255, 0.02) 6px,
        transparent 7px,
        transparent 10px
    ), repeating-linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.01) 0px,
        rgba(255, 255, 255, 0.02) 1px,
        transparent 1px,
        transparent 8px
    );
    /* animation: scanline 30s linear infinite; -- Desativado por padrão, pode ser muito distrativo */
    box-shadow: inset 0 0 15px #000000a0, 0 0 15px #0aebff10; /* Sombra ajustada */
}}
#nash-history h3 {{
    color: #ff07e6; text-shadow: 0 0 10px #ff07e670;
    border-bottom: 1px solid #ff07e640; padding-bottom: 5px; margin-bottom: 18px;
}}

/* --- Avatares e Mensagens no Chat --- */
.avatar-nash, .avatar-eli {{
    font-weight:bold; filter: drop-shadow(0 0 6px); /* Glow vem da cor */
    display: block; /* Garante que fique acima da mensagem */
    margin-bottom: 4px;
}}
.avatar-nash {{ color:#0affa0; }}
.avatar-eli {{ color:#ff07e6; }}

/* --- MELHORIA DE CONTRASTE NAS MENSAGENS --- */
.message-nash, .message-eli {{
    display: inline-block;
    padding: 5px 10px; /* Padding aumentado */
    border-radius: 5px;
    background-color: rgba(255, 255, 255, 0.04); /* Fundo sutilmente mais visível */
    margin-top: 0; /* Removido, avatar já tem margin-bottom */
    line-height: 1.5; /* Melhor legibilidade */
    /* NOVO: Sombra sutil para destacar do fundo */
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}}
.message-nash {{
    color: #c0f0f0; /* Ciano menos saturado, mais claro */
    border-left: 3px solid #0affa070; /* Borda lateral para identificação */
}}
.message-eli {{
    color: #ffd8f4; /* Rosa/Lavanda mais claro */
    border-left: 3px solid #ff07e670; /* Borda lateral para identificação */
}}
/* Ajuste para links dentro das mensagens */
.message-nash a, .message-eli a {{
    color: #87cefa; /* LightSkyBlue para links */
    text-decoration: underline;
    text-decoration-style: dashed;
    text-underline-offset: 3px;
}}
.message-nash a:hover, .message-eli a:hover {{
    color: #ffffff;
    text-decoration: underline;
    text-decoration-style: solid;
}}

#nash-history hr {{
    margin: 15px 0; border: none; border-top: 1px solid #ffffff15; /* Divisor mais sutil */
}}

/* --- Status do Backend (Topo Direito) --- */
#backend-status {{
    position: fixed; top: 10px; right: 15px; font-size: 0.9em; /* Ligeiramente menor */
    color: #ff07e6; font-family: 'Fira Mono', monospace;
    background: rgba(15, 15, 25, 0.85); padding: 4px 10px;
    border-radius: 5px; border: 1px solid #ff07e640; /* Borda mais sutil */
    z-index: 1000;
}}

/* --- Sidebar --- */
.stSidebar > div:first-child {{
    background: linear-gradient(180deg, #101225f0 0%, #181c30f0 100%); /* Leve transparência */
    border-right: 1px solid #0affa020; /* Borda mais sutil */
    backdrop-filter: blur(5px); /* Efeito de vidro fosco (se suportado) */
}}
.stSidebar .stMarkdown h3 {{
    color: #ff07e6; text-shadow: 0 0 8px #ff07e650; /* Sombra ajustada */
    margin-top: 10px; /* Espaçamento */
    margin-bottom: 8px;
}}
.stSidebar .stMarkdown {{ color: #c8d3ff; }}
/* NOVO: Melhorar espaçamento na Sidebar */
.stSidebar .stMarkdown > *, .stSidebar .stFileUploader, .stSidebar .stButton {{
    margin-bottom: 1rem; /* Adiciona espaço abaixo dos elementos */
}}
.stSidebar .stButton {{ margin-top: 0.5rem; }} /* Ajuste para botão */

/* --- Sinais Neon (Sidebar) --- */
.sidebar-sign {{
    font-family: 'Orbitron', 'Fira Mono', monospace; font-weight: bold;
    padding: 8px 15px; margin: 15px auto; border-radius: 5px; text-align: center;
    display: block; width: fit-content; background-color: rgba(0, 0, 10, 0.5);
    border: 1px solid; letter-spacing: 1px; box-shadow: inset 0 0 10px rgba(0,0,0,0.6);
}}
.sign-panic {{
    color: #ff07e6; border-color: #ff07e660; /* Borda mais sutil */
    animation: blink-neon 1.5s infinite; font-size: 1.1em;
}}
.sign-42 {{
    color: #0affa0; border-color: #0affa060; /* Borda mais sutil */
    text-shadow: 0 0 6px #0affa0, 0 0 14px #0affa0, 0 0 20px #0affa0;
    font-size: 1.8em; padding: 5px 20px;
}}

/* --- Indicador de Loading --- */
.loading-indicator {{
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 10px;
    margin-top: 10px;
    border-radius: 5px;
    background-color: #0affa030; /* Fundo ciano sutil */
    border: 1px solid #0affa050;
    color: #e0ffff; /* Texto ciano claro */
    font-family: 'Fira Mono', monospace;
    box-shadow: 0 0 8px #0affa030;
    animation: thinking-pulse 1.5s infinite ease-in-out;
}}
.loading-indicator::before {{
    content: '🧠'; /* Ícone cérebro */
    margin-right: 10px;
    font-size: 1.2em;
    animation: spin 2s linear infinite; /* Animação de rotação */
}}
@keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}

/* --- Mobile Responsiveness (Ajustes Gerais) --- */
@media (max-width: 768px) {{
    body {{ font-size: 14px; }} /* Reduz tamanho base da fonte */
    #visor {{ flex-direction: column; align-items: flex-start; gap: 15px; padding: 15px; }}
    .nash-avatar-emoji {{ font-size: 50px; margin-right: 0; margin-bottom: 10px; }}
    .nash-holo {{ font-size: 1.8em; }}
    .nash-enterprise-tag {{ font-size: 0.8em; }}
    .nash-ascii {{ font-size: 0.85em; }}
    .visor-analytics {{ font-size: 0.9em; padding: 0.3em 1em; }}
    .stTextArea textarea {{ font-size: 1em; }}
    #nash-history {{ padding: 12px 10px 5px 10px; }}
    .message-nash, .message-eli {{ padding: 4px 8px; }}
    #backend-status {{ font-size: 0.8em; padding: 3px 7px; top: 5px; right: 10px; }}

    /* O comportamento padrão do Streamlit (menu hambúrguer) é mantido. */
}}

</style>
""", unsafe_allow_html=True)
# --- Fim do CSS ---

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

# --- CORREÇÃO ANTERIOR: Pré-formatar o ascii_art ---
formatted_ascii_art = ascii_art.replace('<', '<').replace('>', '>').replace('\n', '<br>')
# -----------------------------------------

# --- CORREÇÃO ATUAL: Removido comentário HTML de dentro da f-string ---
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

# --- Login de Segurança (Com fluxo de loading) ---
if not st.session_state.ok:
    st.markdown("### Acesso à Ponte Requerido")
    # Placeholder para o input de senha para poder limpá-lo após sucesso
    pw_placeholder = st.empty()
    pw = pw_placeholder.text_input(
        "Insira o Código de Autorização de Comando:",
        type="password",
        key="login_pw" # Chave para manter o valor entre reruns durante a autenticação
    )

    # Placeholder para o botão, para que possamos controlá-lo
    button_placeholder = st.empty()
    if button_placeholder.button("Autenticar 🛰️", key="login_btn", disabled=st.session_state.waiting_for_nash): # Desabilitado durante espera
        if not pw:
            st.warning("O código de autorização não pode estar vazio.")
            st.session_state.waiting_for_nash = False # Garante que não está esperando se o pw estiver vazio
        else:
            st.session_state.waiting_for_nash = True # Ativa flag de espera
            # Limpa o botão para não aparecer duplicado no rerun
            button_placeholder.empty()
            # Rerun para mostrar o loading indicator (que aparecerá abaixo)
            st.rerun()

    # Se a flag waiting_for_nash foi ativada pelo clique no botão
    if st.session_state.waiting_for_nash:
        loading_placeholder_login = st.empty()
        loading_placeholder_login.markdown("<div class='loading-indicator'>Autenticando com a Nave Mãe...</div>", unsafe_allow_html=True)
        try:
            r = requests.post(f"{BACKEND_URL}/login", json={"password": pw}, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and r.json().get("success"):
                st.session_state.ok = True
                st.session_state.waiting_for_nash = False
                st.session_state.login_pw = "" # Limpa a senha do estado após sucesso
                pw_placeholder.empty() # Limpa o widget de input visualmente
                loading_placeholder_login.empty() # Limpa o loading
                button_placeholder.empty() # Limpa o botão (opcional, mas consistente)
                st.success("Autenticação bem-sucedida. Protocolos Nash desbloqueados.")
                st.balloons()
                time.sleep(1.5)
                st.rerun() # Rerun final para carregar a interface principal
            else:
                st.session_state.waiting_for_nash = False # Falha, desliga espera
                loading_placeholder_login.empty() # Limpa loading
                st.error(f"Falha na autenticação. Acesso negado. (Status: {r.status_code})")
                # Botão reaparecerá no próximo ciclo ou se o usuário interagir

        except requests.exceptions.RequestException as e:
            st.session_state.waiting_for_nash = False
            loading_placeholder_login.empty()
            st.error(f"Erro de rede durante a autenticação: {e}")
        except Exception as e:
            st.session_state.waiting_for_nash = False
            loading_placeholder_login.empty()
            st.error(f"Ocorreu um erro inesperado: {e}")

    # Garante que o script pare aqui se não estiver logado e não estiver no meio de uma tentativa de login bem-sucedida
    if not st.session_state.ok:
        st.stop()


# --- Sidebar Reorganizada e Refinada --- #
with st.sidebar:
    # 1. Sinais do Cockpit (Mantido no Topo)
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic" title="Lembrete Visual">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42" title="A Resposta.">{sign_42_text}</div>""", unsafe_allow_html=True)

    st.markdown("---", unsafe_allow_html=True)

    # 2. Uplink de Dados (Mais "Clean")
    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo ao Próximo Comando", # Rótulo claro e conciso
        type=[ # Tipos mantidos para validação
            "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
            "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml",
            "mp3", "wav", "ogg", # Adicionado áudio básico
            "mp4", "mov", "avi"  # Adicionado vídeo básico (cuidado com tamanho!)
        ],
        key="file_uploader",
        label_visibility="visible", # Garante visibilidade do rótulo
        help="Faça o upload de um arquivo que Nash possa analisar junto com seu próximo comando." # Tooltip
    )

    upload_status_placeholder = st.empty() # Placeholder para mensagens de status do upload
    if uploaded is not None:
        # Processar upload apenas se for um arquivo novo ou diferente do que já foi confirmado
        if st.session_state.uploaded_file_info != uploaded.name:
            files = {"file": (uploaded.name, uploaded.getvalue())}
            try:
                # Usar um spinner enquanto faz o upload
                with st.spinner(f"Transmitindo '{uploaded.name}' para a órbita de Nash..."):
                    r = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=REQUEST_TIMEOUT) # Timeout maior para upload
                if r.status_code == 200:
                    st.session_state.uploaded_file_info = uploaded.name # Guarda nome do arquivo ok
                    upload_status_placeholder.success(f"🛰️ '{uploaded.name}' recebido!")
                else:
                    st.session_state.uploaded_file_info = None # Falha no upload
                    upload_status_placeholder.error(f"Falha na transmissão ({r.status_code}). Tente novamente.")
            except requests.exceptions.Timeout:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error("Timeout durante o upload. O arquivo pode ser muito grande ou a conexão instável.")
            except requests.exceptions.RequestException as e:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error(f"Erro de rede no upload: {e}")
            except Exception as e:
                st.session_state.uploaded_file_info = None
                upload_status_placeholder.error(f"Erro inesperado no upload: {e}")
        # else: # O arquivo é o mesmo já enviado, não precisa fazer nada, apenas mostrar o status abaixo
           # pass
    elif uploaded is None and st.session_state.uploaded_file_info:
         # Se o usuário removeu o arquivo (uploaded is None), limpar o status
         st.session_state.uploaded_file_info = None
         upload_status_placeholder.info("Nenhum arquivo anexado.") # Mensagem opcional

    # Mostrar qual arquivo está anexado (se houver) - fora do bloco if uploaded
    if st.session_state.uploaded_file_info:
        # Garante que a mensagem de sucesso/info não seja sobrescrita imediatamente por outra
        current_status_message = upload_status_placeholder.markdown(f"Arquivo pronto: `{st.session_state.uploaded_file_info}`")


    st.markdown("---", unsafe_allow_html=True)

    # 3. Controles da Sessão (NOVO)
    st.markdown("### ⚙️ Controles")
    if st.button("🗑️ Limpar Log da Sessão", key="clear_chat_btn", help="Apaga todo o histórico de mensagens desta sessão.", use_container_width=True):
        st.session_state.nash_history = []
        st.session_state.eli_msg_count = 0
        st.session_state.nash_msg_count = 0
        st.toast("🧹 Log da sessão limpo!", icon="✨")
        # Rerun para atualizar a exibição do histórico imediatamente
        st.rerun()

    st.markdown("---", unsafe_allow_html=True) # Divisor final

    # 4. Perfil Nash (Movido para o final)
    st.markdown("### 🧠 Perfil Núcleo Nash")
    # Tooltip adicionado para "Recurso"
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
    "Insira comando ou consulta para Nash:",
    key="nash_prompt", # Mantém a key para o state management do Streamlit
    height=110, # Ligeiramente maior
    placeholder="Digite seu comando aqui, Capitão... Anexou um arquivo? Nash o verá.",
    # O valor será gerenciado pelo Streamlit baseado na key e reruns
)

# --- Indicador de Loading para Resposta do Nash ---
loading_placeholder_main = st.empty()
if st.session_state.waiting_for_nash:
    loading_placeholder_main.markdown("<div class='loading-indicator'>Nash está processando seu comando...</div>", unsafe_allow_html=True)

# --- Efeito de Typing nas Respostas (Ajustado para usar placeholder corretamente) ---
def nash_typing(msg, target_placeholder):
    """Renderiza a mensagem de Nash com efeito de digitação no placeholder fornecido."""
    full_render = ""
    lines = msg.split('\n')
    try:
        for line_index, line in enumerate(lines):
            line_output = ""
            for char_index, char in enumerate(line):
                line_output += char
                # O cursor pisca apenas no final da linha atual
                cursor = "█" # Usando bloco cheio para melhor visibilidade
                # Escapa HTML dentro da mensagem para evitar renderização indesejada
                safe_line_output = line_output.replace('<', '<').replace('>', '>')
                safe_full_render = full_render.replace('<', '<').replace('>', '>')

                current_render = safe_full_render + safe_line_output + cursor
                # Renderiza no placeholder específico
                target_placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{current_render}</span>", unsafe_allow_html=True)
                # Delay dinâmico: mais rápido para espaços, mais lento para pontuação
                delay = 0.005 if char == ' ' else (0.05 if char in ['.', ',', '!', '?'] else 0.018)
                time.sleep(delay)

            # Adiciona a linha completa (com quebra de linha) ao render final ANTES de escapar
            full_render += line + "\n"
            safe_full_render = full_render.replace('<', '<').replace('>', '>')

            # Renderiza sem cursor antes de ir para a próxima linha ou finalizar
            target_placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{safe_full_render}</span>", unsafe_allow_html=True)
            if line_index < len(lines) - 1: time.sleep(0.1) # Pequena pausa entre linhas

        # Render final sem cursor e com HTML escapado
        safe_msg = msg.replace('<', '<').replace('>', '>')
        target_placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{safe_msg}</span>", unsafe_allow_html=True)
    except Exception as e:
        # Fallback para renderização simples em caso de erro no typing
        safe_msg = msg.replace('<', '<').replace('>', '>')
        target_placeholder.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>[Erro no efeito typing, exibindo direto] {safe_msg}</span>", unsafe_allow_html=True)
        print(f"Erro durante nash_typing: {e}") # Log do erro

# --- Enviar Mensagem para Backend (Com Loading State) ---
# O botão fica desabilitado enquanto espera Nash
# Usamos um placeholder para o botão para poder controlá-lo
transmit_button_placeholder = st.empty()
if transmit_button_placeholder.button("Transmitir para Nash 🚀", key="chat_btn", disabled=st.session_state.waiting_for_nash):
    # Verifica se o prompt não está vazio diretamente do session_state ou do widget
    current_prompt = st.session_state.get("nash_prompt", "")
    if current_prompt:
        st.session_state.nash_history.append(("Eli", current_prompt))
        st.session_state.eli_msg_count += 1
        st.session_state.waiting_for_nash = True # Ativa o loading
        st.session_state.clear_prompt_on_next_run = True # Sinaliza para limpar

        # Limpa o placeholder de loading da área principal ANTES de enviar o rerun
        loading_placeholder_main.empty()
        # Limpa o botão para evitar duplicatas visuais rápidas
        transmit_button_placeholder.empty()
        # Limpa também o prompt visualmente antes do rerun (embora o rerun vá fazer isso)
        # st.session_state.nash_prompt = "" # Descomentar se necessário

        st.rerun() # Rerun para mostrar histórico atualizado e loading indicator

    else:
        st.warning("Não posso transmitir um comando vazio, Eli.")
        st.session_state.waiting_for_nash = False # Garante que não fique em loading

# --- Lógica de Comunicação com Backend (Executada após o rerun do botão 'Transmitir') ---
if st.session_state.waiting_for_nash and st.session_state.ok:
    # Pega o último prompt enviado por Eli (que acabou de ser adicionado ao histórico)
    last_eli_prompt = ""
    if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli":
         last_eli_prompt = st.session_state.nash_history[-1][1]

    if last_eli_prompt: # Garante que temos um prompt para enviar
        try:
            # Envia o prompt para o backend
            req = requests.post(
                f"{BACKEND_URL}/chat",
                json={"prompt": last_eli_prompt,"session_id": "eli"}, # session_id mantido
                timeout=REQUEST_TIMEOUT # Usa timeout definido (maior para leitura)
            )

            # Processa a resposta
            if req.status_code == 200:
                resp = req.json().get("response", "Nash parece estar sem palavras. Verifique os logs do backend.")
                st.session_state.nash_history.append(("Nash", resp))
                st.session_state.nash_msg_count += 1
            else:
                error_msg = f"[Erro {req.status_code}: {req.text[:100] + ('...' if len(req.text) > 100 else '')}]" # Limita tamanho da msg de erro
                st.session_state.nash_history.append(("Nash", error_msg))
                st.session_state.nash_msg_count += 1
                # Mostra erro na UI também, fora do histórico
                st.error(f"Erro ao comunicar com Nash. Status: {req.status_code}.")

        except requests.exceptions.Timeout:
            st.session_state.nash_history.append(("Nash", "[Erro: Timeout na resposta de Nash]"))
            st.session_state.nash_msg_count += 1
            st.error("Requisição para Nash expirou (timeout). Tente novamente ou simplifique o comando.")
        except requests.exceptions.RequestException as e:
            st.session_state.nash_history.append(("Nash", f"[Erro de Rede: {e}]"))
            st.session_state.nash_msg_count += 1
            st.error(f"Erro de rede ao contactar Nash: {e}")
        except Exception as e:
            st.session_state.nash_history.append(("Nash", f"[Erro Inesperado no Cliente: {e}]"))
            st.session_state.nash_msg_count += 1
            st.error(f"Ocorreu um erro inesperado: {e}")
        finally:
            # Independentemente do resultado, desliga o loading
            st.session_state.waiting_for_nash = False
            # A flag clear_prompt_on_next_run está True, então o próximo rerun limpará o input.
            # Rerun para mostrar a resposta/erro e limpar o prompt
            st.rerun()
    else:
        # Caso raro: chegou aqui esperando, mas não achou o último prompt de Eli
        st.warning("Erro interno: Não foi possível encontrar o último comando para enviar.")
        st.session_state.waiting_for_nash = False
        st.rerun()


# --- Easter Eggs e Comandos Especiais (Cliente) ---
# Verifica o último comando de Eli APENAS se não estiver esperando resposta E houver histórico
if not st.session_state.waiting_for_nash and st.session_state.nash_history:
    last_entry = st.session_state.nash_history[-1]
    # Processa comandos especiais que foram enviados por Eli, mas APENAS se a última mensagem NÃO for de Nash
    # Isso evita reprocessar comandos como "data estelar" depois que Nash já respondeu.
    if last_entry[0] == 'Eli':
        last_prompt = last_entry[1].lower()
        # Flag para evitar múltiplos reruns se vários comandos especiais ocorrerem
        should_rerun_after_special_command = False

        if "data estelar" in last_prompt or ("data" in last_prompt and any(sub in last_prompt for sub in ["hoje", "agora", "hora"])):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
            st.toast(f"🕒 Data Estelar (Cliente): {now}", icon="🕰️") # Usando toast para info rápida

        # Comando Auto-Destruir (Mantido como exemplo)
        if "auto destruir" in last_prompt or "autodestruir" in last_prompt:
            st.warning("🚨 Sequência de auto-destruição iniciada... Brincadeirinha, Capitão. Por enquanto.")
            st.snow()
            # Não precisa de rerun para a neve


# --- Exibir Histórico de Chat (Com Typing na Última Mensagem de Nash) ---
if st.session_state.nash_history:
    st.markdown('<div id="nash-history">', unsafe_allow_html=True)
    st.markdown("### ⏳ Log da Sessão")

    # Usar um container para o histórico permite limpar e recriar facilmente, se necessário
    history_container = st.container()

    with history_container:
        last_message_index = len(st.session_state.nash_history) - 1
        for i, (who, msg) in enumerate(st.session_state.nash_history):
            # Escapar HTML nas mensagens para exibição segura
            safe_msg = msg.replace('<', '<').replace('>', '>')

            if who == "Nash":
                # Se for a última mensagem E de Nash E não estamos mais esperando resposta
                if i == last_message_index and not st.session_state.waiting_for_nash:
                     # Cria um placeholder *específico* para a última mensagem de Nash para o typing
                     nash_response_placeholder = st.empty()
                     nash_typing(msg, nash_response_placeholder) # Passa o placeholder para a função
                else:
                     # Renderiza mensagens anteriores de Nash ou se ainda estiver esperando (mostra estático)
                     st.markdown(f"<span class='avatar-nash'>👨‍🚀 Nash:</span><br><span class='message-nash'>{safe_msg}</span>", unsafe_allow_html=True)
            else: # Mensagem de Eli
                st.markdown(f"<span class='avatar-eli'>🧑‍🚀 Eli:</span><br><span class='message-eli'>{safe_msg}</span>", unsafe_allow_html=True)

            # Adiciona divisor, exceto após a última mensagem
            if i < last_message_index:
                st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif not st.session_state.waiting_for_nash: # Mostra apenas se não houver histórico E não estiver carregando
    st.markdown("> *Console aguardando o primeiro comando... A vastidão do espaço digital espera por suas ordens.*")