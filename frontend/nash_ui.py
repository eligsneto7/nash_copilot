# nash_ui_v6_ptbr_layout_contrast.py
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

########### --- ESTILO V6 --- #############
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;700&family=Orbitron:wght@400;700&display=swap');

@keyframes blink-neon {{
  0%, 100% {{ opacity: 1; text-shadow: 0 0 7px #ff07e6, 0 0 15px #ff07e6, 0 0 20px #ff07e6; }}
  50% {{ opacity: 0.7; text-shadow: 0 0 5px #ff07e6a0, 0 0 10px #ff07e6a0; }}
}}

body {{
    /* Mantém o fundo do body com gradiente radial */
    background: radial-gradient(ellipse at center, #1a1a2a 0%, #0d0d1a 70%), linear-gradient(145deg, #0d0d1a 70%, #1f1f3d 100%);
    background-attachment: fixed;
    color: #c8d3ff !important; /* Leve ajuste na cor base */
    font-family: 'Fira Mono', 'Consolas', monospace;
    min-height: 100vh !important;
    overflow-x: hidden;
}}

body:before {{
    /* Mantém a chuva hacker sutil */
    content: '';
    background-image: url('https://i.ibb.co/tbq0Qk4/retro-rain.gif');
    opacity: .12;
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;
    pointer-events: none;
    background-size: cover;
}}

section.main > div {{
    /* --- NOVO: Fundo da área principal com gradiente escuro --- */
    background: linear-gradient(170deg, #0f111a 0%, #1c202f 100%) !important;
    border-radius: 15px;
    border: 1px solid #0aebff40; /* Borda ciano mantida */
    box-shadow: 0 0 20px #0aebff15, inset 0 0 15px rgba(0,0,0,0.4); /* Sombra interna levemente mais forte */
}}

#visor {{
    /* Estilos do visor mantidos */
    background:
        linear-gradient(135deg, #101225f5 80%, #ff07e6e0 140%),
        rgba(5, 5, 15, 0.95);
    border-radius: 15px;
    margin-bottom: 20px; margin-top: -10px;
    border: 2.5px solid #ff07e680;
    box-shadow: 0 0 28px #e600c670, inset 0 0 12px #101225cc;
    padding: 18px 26px 14px 30px;
    display: flex; align-items: center;
    gap: 25px;
}}

.nash-avatar-emoji {{
    /* Estilos do avatar mantidos */
    font-size: 65px;
    filter: drop-shadow(0 0 12px #0affa0);
    margin-right: 15px;
    line-height: 1;
}}

.nash-holo, .nash-enterprise-tag, .nash-ascii, .nash-ascii b {{
    /* Estilos do título e ascii mantidos */
    font-family: 'Orbitron', 'Fira Mono', monospace;
    /* ... outros estilos ... */
}}
.nash-holo {{ font-size: 2.1em; color: #0affa0; text-shadow: 0 0 15px #0affa0a0, 0 0 5px #ffffff60; margin-bottom: 3px; user-select: none; }}
.nash-enterprise-tag {{ font-size: 0.9em; color: #ff07e6b0; font-family: 'Fira Mono', monospace; }}
.nash-ascii {{ font-family: 'Fira Mono', monospace; color: #0affa0c0; letter-spacing: 0.5px; line-height: 110%; font-size: 0.95em; text-shadow: 0 0 8px #0affa050; margin-top: -5px; margin-bottom: 5px; }}
.nash-ascii b {{ color: #ff07e6; font-weight: bold; }}


.stButton>button {{
    /* Estilos dos botões mantidos */
    color: #e0e8ff; background: #181c30; border-radius: 8px; border: 2px solid #0affa090; font-weight: bold; transition: all 0.3s ease; box-shadow: 0 0 8px #0affa030;
}}
.stButton>button:hover {{ background: #202540; border-color: #0affa0; box-shadow: 0 0 15px #0affa070; color: #ffffff; }}
.stButton>button:active {{ background: #101225; }}

/* --- Input Area Contrast Review --- */
.stTextArea textarea {{
    /* Fundo escuro e cor de texto clara já ok */
    background: #101225 !important;
    color: #c8d3ff !important; /* Mesma cor base do body */
    border: 1px solid #0affa050 !important;
    border-radius: 5px !important;
    box-shadow: inset 0 0 8px #00000050;
}}
.stTextArea textarea:focus {{
    border-color: #0affa0 !important;
    box-shadow: 0 0 10px #0affa050;
}}
::-webkit-input-placeholder {{ color: #0affa0; opacity: 0.6; }} /* Placeholder ciano mantido */
/* ... outros placeholders ... */
::-moz-placeholder {{ color: #0affa0; opacity: 0.6; }}
:-ms-input-placeholder {{ color: #0affa0; opacity: 0.6; }}
:-moz-placeholder {{ color: #0affa0; opacity: 0.6; }}


.stFileUploader {{
    /* Estilos do uploader mantidos */
    background: #101225 !important; border: 1px dashed #0affa070 !important; border-radius: 8px; padding: 15px;
}}
.stFileUploader label {{
    color: #0affa0 !important;
}}

/* --- Chat History Contrast Review --- */
#nash-history {{
    /* Fundo escuro do histórico mantido */
    background: #0a0c13cc; /* Um pouco mais escuro e menos transparente */
    border-radius: 10px;
    padding: 18px 16px 8px 15px;
    margin-top: 20px;
    border: 1px solid #0affa050;
    background-image: repeating-linear-gradient(90deg, rgba(0, 200, 255, 0.01) 0px, rgba(0, 200, 255, 0.02) 1px, transparent 1px, transparent 8px); /* Padrão levemente ajustado */
    box-shadow: inset 0 0 12px #00000090, 0 0 10px #0aebff15; /* Sombra interna mais escura */
}}
#nash-history h3 {{
    /* Header do histórico mantido */
    color: #ff07e6; text-shadow: 0 0 8px #ff07e680; border-bottom: 1px solid #ff07e650; padding-bottom: 5px; margin-bottom: 15px;
}}

.avatar-nash, .avatar-eli {{
    /* Estilos dos avatares mantidos */
    font-weight:bold; filter: drop-shadow(0 0 5px); /* Glow vem da cor */
}}
.avatar-nash {{ color:#0affa0; /* Cyan */ }}
.avatar-eli {{ color:#ff07e6; /* Magenta */ }}

/* --- NOVO: Melhoria de contraste nas mensagens --- */
.message-nash, .message-eli {{
    display: inline-block; /* Para o fundo e padding funcionarem bem */
    padding: 2px 5px; /* Pequeno padding interno */
    border-radius: 3px;
    background-color: rgba(255, 255, 255, 0.02); /* Fundo quase invisível para separação */
    margin-top: 3px; /* Espaço entre avatar e texto */
}}
.message-nash {{ color: #e0ffff; /* Light Cyan - um pouco mais brilhante */ }}
.message-eli {{ color: #ffe4f1; /* Lavender Blush - rosa/lavanda claro */ }}

#nash-history hr {{
    /* Divisor mantido */
    margin: 12px 0; border: none; border-top: 1px solid #ffffff1a;
}}

#backend-status {{
    /* Estilos do status mantidos */
    position: fixed; top: 10px; right: 20px; font-size: 1.0em; color: #ff07e6; font-family: 'Fira Mono', monospace; background: rgba(15, 15, 25, 0.8); padding: 3px 8px; border-radius: 5px; border: 1px solid #ff07e650; z-index: 1000;
}}

.visor-analytics {{
    /* Estilos do visor analytics mantidos */
    color:#ff07e6; font-size: 0.95em; padding: 0.3em 1.2em; background: rgba(10, 10, 25, 0.7); border-radius: 8px; border: 1px solid #ff07e660; margin-top: 10px; line-height: 1.4;
}}
.visor-analytics b {{ color: #ffffff; }}
.visor-analytics i {{ color: #c8d3ff; opacity: 0.8; }}

/* Sidebar styling */
.stSidebar > div:first-child {{
    /* Estilos da sidebar mantidos */
    background: linear-gradient(180deg, #101225 0%, #181c30 100%); border-right: 1px solid #0affa030;
}}
.stSidebar .stMarkdown h3 {{
    /* Header da sidebar mantido */
    color: #ff07e6; text-shadow: 0 0 6px #ff07e660;
}}
.stSidebar .stMarkdown {{
    color: #c8d3ff; /* Cor base ajustada */
}}
/* Sem stInfo agora */

/* --- Estilos para Sinais HTML Neon (mantidos) --- */
.sidebar-sign {{
    font-family: 'Orbitron', 'Fira Mono', monospace; font-weight: bold; padding: 8px 15px; margin: 15px auto; border-radius: 5px; text-align: center; display: block; width: fit-content; background-color: rgba(0, 0, 10, 0.4); border: 1px solid; letter-spacing: 1px; box-shadow: inset 0 0 8px rgba(0,0,0,0.5);
}}
.sign-panic {{ color: #ff07e6; border-color: #ff07e680; animation: blink-neon 1.5s infinite; font-size: 1.1em; }}
.sign-42 {{ color: #0affa0; border-color: #0affa080; text-shadow: 0 0 5px #0affa0, 0 0 12px #0affa0, 0 0 18px #0affa0; font-size: 1.8em; padding: 5px 20px; }}

</style>
""", unsafe_allow_html=True) # Fim do st.markdown CSS


# --- Lógica para Limpar o Prompt (mantida) ---
if st.session_state.clear_prompt_on_next_run:
    st.session_state.nash_prompt = ""
    st.session_state.clear_prompt_on_next_run = False


############# --- STATUS DO BACKEND --- #############
# (Código inalterado)
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
# (Código inalterado)
visor_avatar_tag = '<span class="nash-avatar-emoji">👨‍🚀</span>'
motivations = [ "Iniciando módulo de sarcasmo... Aguarde.", "A realidade é complicada. Código é limpo. Geralmente.", "Buscando trilhões de pontos de dados por uma piada decente...", "Lembre-se: Sou um copiloto, não um milagreiro. Na maior parte do tempo.", "Engajando rede neural... ou talvez só pegando um café.", "Vibrações de Blade Runner detectadas. Ajustando iluminação ambiente.", "Minha lógica é inegável. Minha paciência não.", "Vamos navegar pelo cosmos digital juntos, Eli.", "Compilando... Por favor, aguarde. Ou não. Vou terminar de qualquer jeito.", "A resposta é 42, mas qual era a pergunta mesmo?", "Probabilidade de sucesso: Calculando... Não entre em pânico." ]
if "start_time" not in st.session_state: st.session_state.start_time = datetime.now()
if "nash_history" not in st.session_state: st.session_state.nash_history = []
if "eli_msg_count" not in st.session_state: st.session_state.eli_msg_count = 0
if "nash_msg_count" not in st.session_state: st.session_state.nash_msg_count = 0
uptime_delta = datetime.now() - st.session_state.start_time; uptime_minutes = uptime_delta.seconds // 60; uptime_seconds = uptime_delta.seconds % 60
visor_text = f"""<div id="visor">{visor_avatar_tag}<div> <span class="nash-holo">Nash Copilot</span><span class="nash-enterprise-tag"> :: Ponte da Eli Enterprise</span> <div class="nash-ascii"> > Status: <b>Operacional</b> | Humor: Sarcástico<br> > Temp. Núcleo: <b>Nominal</b> | Matriz Lógica: Ativa<br> > Missão: <b>Auxiliar Eli</b> | Diretriz: Ter Sucesso<br> </div> <div class="visor-analytics"> Cmds Eli: <b>{st.session_state.eli_msg_count}</b> | Resps Nash: <b>{st.session_state.nash_msg_count}</b><br> Tempo de Sessão: <b>{uptime_minutes}m {uptime_seconds}s</b><br> <i>{random.choice(motivations)}</i> </div></div></div>"""
st.markdown(visor_text, unsafe_allow_html=True)

########### --- MENSAGEM ANIMADA DE EMBARQUE ------------
# (Código inalterado)
if "nash_welcome" not in st.session_state: st.session_state.nash_welcome = True
if st.session_state.nash_welcome:
    st.markdown("> *Sistemas Nash online. Sarcasmo calibrado. Bem-vindo de volta ao cockpit, Eli.* 🚀")
    time.sleep(1.1); st.session_state.nash_welcome = False; st.rerun()

########### --- LOGIN DE SEGURANÇA ------------------------
# (Código inalterado)
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
    # 1. Sinais do Cockpit (Primeiro item)
    st.markdown("### ✨ Sinais do Cockpit")
    st.markdown(f"""<div class="sidebar-sign sign-panic">{sign_panic_text}</div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="sidebar-sign sign-42">{sign_42_text}</div>""", unsafe_allow_html=True)

    st.markdown("---") # Divisor

    # 2. Uplink de Dados (Simplificado)
    st.markdown("### 📡 Uplink de Dados")
    uploaded = st.file_uploader(
        "📎 Anexar Arquivo", # Rótulo simplificado
        type=[ # Mantém a funcionalidade de tipos, mas não exibe na label
            "jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff", "svg",
            "py", "txt", "md", "json", "csv", "pdf", "log", "sh", "yaml", "toml"
        ],
        key="file_uploader",
        label_visibility="visible" # Garante que o rótulo (simplificado) apareça
    )
    if uploaded is not None:
        files = {"file": (uploaded.name, uploaded.getvalue())}
        try:
            r = requests.post(f"{backend_url}/upload", files=files, timeout=15)
            if r.status_code == 200: st.success(f"Arquivo '{uploaded.name}' transmitido!") # Mensagem mais curta
            else: st.error(f"Erro na transmissão ({r.status_code}).")
        except requests.exceptions.RequestException as e: st.error(f"Erro de rede: {e}")
        except Exception as e: st.error(f"Erro inesperado no upload: {e}")

    st.markdown("---") # Divisor

    # 3. Perfil Nash (Último item)
    st.markdown("### 🧠 Perfil Núcleo Nash")
    st.markdown(
        """
        Designação: **Nash**
        Classe: IA Copiloto Digital
        Memória: Vetorizada
        Recurso: Sarcasmo™
        Status: **Leal a Eli**
        """ # Texto levemente encurtado
        )

    # Bloco "Sugestões de Comando" foi REMOVIDO.

########### --- ÁREA PRINCIPAL DE CHAT ---------------------
# (Código inalterado)
st.markdown("### 🎙️ Console de Comando — Nash AI")
prompt = st.text_area("Insira comando ou consulta para Nash:", key="nash_prompt", height=100, placeholder="Digite 'engage!' para uma surpresa ou insira seu comando...")

############ --- EFEITO DE TYPING NAS RESPOSTAS -----------
# (Código inalterado)
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
# (Código inalterado, incluindo a correção para limpar o prompt)
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
# (Código inalterado)
last_prompt = st.session_state.nash_history[-1][1] if st.session_state.nash_history and st.session_state.nash_history[-1][0] == "Eli" else ""
if last_prompt and "data" in last_prompt.lower() and any(substr in last_prompt.lower() for substr in ["hoje", "agora", "hora"]):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z"); st.info(f"🕒 Data Estelar Atual (Cliente): {now}")
if last_prompt and "limpar console" in last_prompt.lower():
    st.session_state.nash_history = []; st.info("Histórico do console limpo."); time.sleep(1); st.rerun()
if last_prompt and "auto destruir" in last_prompt.lower():
    st.warning("🚨 Sequência de auto-destruição iniciada... Brincadeirinha."); st.snow()

######### --- EXIBIR HISTÓRICO DE CHAT ---------------------
# (Código inalterado)
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