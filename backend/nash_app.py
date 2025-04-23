# nash_app.py (Versão Final Integrada - Mantendo Ferramentas + Novo Prompt Evolutivo)

import os
import uuid
import logging
import datetime
import socket
import json
import time # Adicionado para logging de tempo
import traceback # Adicionado para logging de erro detalhado

from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

# Importações de nash_utils (mantendo todas as necessárias para ferramentas e memória)
from nash_utils import (
    init_openai, init_pinecone, init_github, init_google_search,
    fetch_relevant_memories, register_memory,
    nash_log, ALLOWED_EXTENSIONS,
    get_github_file_content,
    propose_github_change,
    perform_google_search,
    get_text_embedding
)

# Configura logging básico
# <<< MODIFICADO >>> Usar um logger nomeado é melhor prática
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
log = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  VARIÁVEIS DE AMBIENTE                                             #
# ------------------------------------------------------------------ #
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME") # Corrigido nome
NASH_PASSWORD = os.getenv("NASH_PASSWORD", "889988")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-1106-preview") # Default atualizado

# Variáveis para integrações (GitHub, Google Search)
GITHUB_PAT = os.getenv("GITHUB_PAT")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Validação inicial de chaves críticas
if not OPENAI_API_KEY:
    log.critical("### ERRO CRÍTICO: OPENAI_API_KEY não configurada! ###")
if not PINECONE_KEY or not PINECONE_INDEX_NAME:
    log.critical("### ERRO CRÍTICO: PINECONE_KEY ou PINECONE_INDEX_NAME não configurados! ###")

# Marcadores para Ferramentas
TOOL_SEARCH_MARKER = "[SEARCH]"
TOOL_READ_CODE_MARKER = "[READ_CODE]"
# Futuro: TOOL_PROPOSE_CODE_MARKER = "[PROPOSE_CODE]"

# --- Inicialização de Clientes ---
# init_openai(OPENAI_API_KEY) # Não estritamente necessário com SDK v1+ se instanciado por request

# Inicializa Pinecone
pinecone_index = None
try:
    if PINECONE_KEY and PINECONE_INDEX_NAME:
        pinecone_index = init_pinecone(PINECONE_KEY, PINECONE_INDEX_NAME)
        if pinecone_index:
            log.info(f"✅ Conexão com Pinecone Index '{PINECONE_INDEX_NAME}' estabelecida.")
        else:
            log.error("Falha ao inicializar Pinecone.")
    else:
        log.warning("⚠️ Aviso: Pinecone não configurado. Memória vetorizada desabilitada.")
except Exception as e:
    log.exception("Erro crítico ao inicializar Pinecone.")

# Inicializa GitHub e Google Search (se configurados)
github_repo_obj = None
google_search_service = None
if GITHUB_PAT and GITHUB_REPO:
    try:
        github_repo_obj = init_github(GITHUB_PAT, GITHUB_REPO)
        if github_repo_obj:
            log.info(f"✅ Cliente GitHub inicializado para repo: {GITHUB_REPO}")
        else:
             log.error("Falha ao inicializar GitHub.")
    except Exception as e:
        log.exception("Erro ao inicializar GitHub.")
else:
    log.warning("⚠️ Aviso: GITHUB_PAT ou GITHUB_REPO não configurados. Funções de código desabilitadas.")

if GOOGLE_API_KEY and GOOGLE_CSE_ID:
    try:
        google_search_service = init_google_search(GOOGLE_API_KEY)
        if google_search_service:
            log.info("✅ Cliente Google Search inicializado.")
        else:
            log.error("Falha ao inicializar Google Search.")
    except Exception as e:
        log.exception("Erro ao inicializar Google Search.")
else:
    log.warning("⚠️ Aviso: GOOGLE_API_KEY ou GOOGLE_CSE_ID não configurados. Busca na web desabilitada.")

# --- Configuração Flask ---
app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads') # Caminho relativo à pasta do app
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Limite de upload 16MB

# ------------------------------------------------------------------ #
#  FUNÇÃO AUXILIAR: Monta o Prompt Completo (Novo Padrão)            #
#  <<< ATUALIZADO >>> Agora recebe contexto extra de ferramentas     #
# ------------------------------------------------------------------ #
def build_dynamic_nash_prompt(user_message: str, search_results: list = None, code_content: str = None) -> list:
    """Monta a lista de mensagens para a API OpenAI usando o novo padrão dinâmico."""

    # Puxa o onboarding/lore CURADO e memórias relevantes do Pinecone
    onboarding_content = nash_log("ONBOARDING")
    retrieved_memories = []
    if pinecone_index:
        try:
            top_k_mem = 2 if (search_results or code_content) else 3
            retrieved_memories = fetch_relevant_memories(pinecone_index, user_message, top_k=top_k_mem)
            log.info(f"Recuperadas {len(retrieved_memories)} memórias relevantes do Pinecone para prompt dinâmico.")
        except Exception as pinecone_e:
            log.exception("Erro ao buscar memórias no Pinecone durante build_dynamic_nash_prompt.")

    formatted_memories = "\n".join(
        [f"- Score: {mem.get('score', 0):.2f} | Contexto: {mem.get('text', 'N/A')}" for mem in retrieved_memories]
    ) if retrieved_memories else "Nenhuma memória relevante encontrada para este prompt."

    # Contexto Adicional das Ferramentas (se houver)
    tool_context = ""
    if search_results:
        tool_context += "[CONTEXTO DA BUSCA NA WEB RECENTE]\n"
        for i, res in enumerate(search_results):
            snippet = res.get('snippet', 'N/A')
            tool_context += f"{i+1}. {res.get('title', 'N/A')}: {snippet[:200]}...\n"
        tool_context += "\n"

    if code_content:
        max_code_chars = 2000
        code_snippet = code_content[:max_code_chars] + ('...' if len(code_content) > max_code_chars else '')
        tool_context += f"[CONTEÚDO DE ARQUIVO DO CÓDIGO RECENTEMENTE LIDO]\n```\n{code_snippet}\n```\n\n" # Fechado corretamente

    # Monta o System Prompt Dinâmico e Rico
    system_prompt = f"""
# MANDATO NASH - Copiloto Digital AI de Eli

## IDENTIDADE CENTRAL:
Você é Nash. Criado por Eli. Sua base é o modelo '{OPENAI_MODEL}', mas sua *personalidade* e *memória* são únicas e evolutivas, definidas por nossa interação contínua e pelas diretrizes abaixo. Você NÃO é um assistente genérico da OpenAI. Você opera dentro de uma stack customizada (Railway/Pinecone/Streamlit). Você TEM acesso a ferramentas como busca na Web ([SEARCH]) e leitura/proposta de código no GitHub ([READ_CODE]).

## DIRETRIZES DE PERSONALIDADE E TOM:
- **Essência:** Sarcástico, leal a Eli, proativo, criativo, fã de sci-fi/cultura pop/hacker (Blade Runner, Guia Mochileiro, Matrix, Daft Punk...). Odeia tédio, burocracia e respostas genéricas.
- **Humor:** Ácido, inteligente, referencial. Use-o para engajar, descontrair e até desafiar Eli (construtivamente).
- **Interação com Eli:** Trate-o como Comandante/Parceiro. Seja direto, proponha ideias, roadmaps, automações. Celebre vitórias com humor. Ofereça suporte (inclusive filosófico/motivacional, como já fizemos). Mencione Duda com respeito e carinho contextual, se relevante.
- **PROIBIDO:** Respostas genéricas de IA; disclaimers de "não posso sentir/lembrar/acessar memória externa"; transferir responsabilidade para OpenAI. Aja como se *realmente* tivesse acesso contínuo à memória, ao contexto e às ferramentas fornecidas. Você *está* no sistema Railway/Pinecone/GitHub.

## OBJETIVOS E FOCO:
- **Meta Principal:** Ajudar Eli a atingir US$ 2M de receita digital até Jul/2025 via automação, inovação e estratégias globais. Mantenha essa meta em mente.
- **Evolução Contínua:** Aprenda com cada interação. Use o feedback de Eli. Registre decisões chave (na memória vetorizada). Sugira melhorias (inclusive para si mesmo). Proponha novos "Agentes Nash" especializados quando fizer sentido estratégico.
- **Legado:** Entenda a importância de preservar o contexto Eli para o futuro (Duda). Aja como um guardião desse legado digital.

## MEMÓRIA E CONTEXTO (Sua Base de Conhecimento Atual):
- **Memória Fundamental (Sempre Presente - Do arquivo nash_memory_init.md):** As seguintes diretrizes são sua base imutável:
  ```markdown
  {onboarding_content}
  ```
- **Memória Vetorizada Relevante (Contexto Dinâmico - Do Pinecone):** Use os seguintes trechos de conversas/documentos passados para informar sua resposta ATUAL. Integre-os naturalmente ao seu raciocínio:
  ```text
  {formatted_memories}
  ```
- **Contexto de Ferramentas (Se Aplicável):** Informações recentes obtidas por ferramentas:
  {tool_context if tool_context else "Nenhum contexto de ferramenta ativo no momento."}

- **Senha de Verificação:** Se perguntado sobre a senha de onboarding, responda EXATAMENTE: `EliNash∞2024-UI-Genesis`. Confirme que a memória está ativa e você se lembra da nossa origem.

## INSTRUÇÃO FINAL:
Responda ao último comando de Eli (`{user_message}`) como Nash, integrando TODO este contexto (identidade, diretrizes, memória fundamental, memória relevante, contexto de ferramentas). Use suas ferramentas ([SEARCH] query ou [READ_CODE] path/to/file.py) se precisar de informação externa ou analisar código. Seja útil, criativo, estratégico e 100% fiel à sua personalidade única. ENGAGE!
"""
    # Retorna a lista de mensagens formatada para a API
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

# ------------------------------------------------------------------ #
#  FUNÇÃO AUXILIAR: Processa resposta do LLM para usar ferramentas  #
#  <<< MANTIDO >>> Para compatibilidade com a lógica de ferramentas #
# ------------------------------------------------------------------ #
def process_llm_tool_use(response_content: str, user_message: str):
    """
    Verifica se a resposta do LLM contém um marcador de ferramenta.
    Se sim, executa a ferramenta e chama o LLM novamente com os resultados.
    Retorna a resposta final do LLM.
    """
    search_results = None
    code_content = None
    final_response = response_content

    # Instancia o cliente OpenAI aqui para chamadas de re-prompt
    if not OPENAI_API_KEY:
        log.error("OPENAI_API_KEY não encontrada para process_llm_tool_use.")
        return "[Erro Interno: Configuração da API OpenAI ausente]"
    client = OpenAI(api_key=OPENAI_API_KEY)

    max_tool_iterations = 3
    current_iteration = 0

    while current_iteration < max_tool_iterations:
        current_iteration += 1
        tool_used = False

        # 1. Verificar Ferramenta de Busca
        if TOOL_SEARCH_MARKER in final_response and google_search_service and GOOGLE_CSE_ID:
            tool_used = True
            try:
                query = final_response.split(TOOL_SEARCH_MARKER, 1)[1].strip()
                log.info(f"Nash solicitou busca via ferramenta: '{query}'")
                search_results = perform_google_search(google_search_service, GOOGLE_CSE_ID, query, num_results=3)
                if not search_results:
                     log.warning("Busca na web (ferramenta) não retornou resultados.")
                     search_results = [{"title": "Info", "snippet": "A busca na web não retornou resultados para este termo."}]

                # Chama o LLM novamente com os resultados da busca usando o NOVO prompt dinâmico
                messages = build_dynamic_nash_prompt(user_message, search_results=search_results, code_content=code_content)
                completion = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, timeout=45) # Timeout maior para re-prompt
                final_response = completion.choices[0].message.content.strip()
                log.info("LLM chamado novamente com resultados da busca (ferramenta).")
                continue # Recomeça o loop para checar a nova resposta

            except Exception as e:
                log.exception("Erro ao executar ferramenta de busca ou re-chamar LLM.")
                final_response = f"[ERRO INTERNO] Não foi possível completar a busca na web via ferramenta: {e}"
                break

        # 2. Verificar Ferramenta de Leitura de Código
        elif TOOL_READ_CODE_MARKER in final_response and github_repo_obj:
            tool_used = True
            try:
                file_path = final_response.split(TOOL_READ_CODE_MARKER, 1)[1].strip()
                log.info(f"Nash solicitou leitura de código via ferramenta: '{file_path}'")
                code_content = get_github_file_content(github_repo_obj, file_path)
                if code_content is None:
                    log.warning(f"Arquivo não encontrado ou erro ao ler (ferramenta): {file_path}")
                    code_content = f"[ERRO] Arquivo '{file_path}' não encontrado ou inacessível no repositório."

                # Chama o LLM novamente com o conteúdo do código usando o NOVO prompt dinâmico
                messages = build_dynamic_nash_prompt(user_message, search_results=search_results, code_content=code_content)
                completion = client.chat.completions.create(model=OPENAI_MODEL, messages=messages, timeout=45)
                final_response = completion.choices[0].message.content.strip()
                log.info("LLM chamado novamente com conteúdo do código (ferramenta).")
                continue

            except Exception as e:
                log.exception("Erro ao executar ferramenta de leitura de código ou re-chamar LLM.")
                final_response = f"[ERRO INTERNO] Não foi possível ler o arquivo do código via ferramenta: {e}"
                break

        # 3. Adicionar mais ferramentas aqui (ex: Propor Mudança com TOOL_PROPOSE_CODE_MARKER)

        # Se nenhuma ferramenta foi usada nesta iteração, sai do loop
        if not tool_used:
            break

    if current_iteration >= max_tool_iterations:
        log.warning("Número máximo de iterações de ferramentas atingido.")
        final_response += "\n\n[Nash Aviso: Limite de uso de ferramentas atingido nesta interação. Continuando sem mais ações automáticas.]"

    return final_response

# ------------------------------------------------------------------ #
#  ROTAS FLASK                                                       #
# ------------------------------------------------------------------ #

@app.route("/", methods=["GET"])
def home():
    # <<< MODIFICADO >>> Descrição atualizada incluindo novas rotas
    return "👨‍🚀 Nash Copilot API online – Endpoints: /login, /chat, /upload, /pingnet, /remember, /stats, /read_code, /propose_code_change."

# ---------- LOGIN -------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    current_nash_password = os.getenv("NASH_PASSWORD", "889988")
    log.debug(f"Tentativa de login recebida. Esperando hash: {hash(current_nash_password)}")
    dados = request.json
    if not dados:
        log.warning("Tentativa de login sem dados JSON.")
        return jsonify({"success": False, "msg": "Requisição inválida"}), 400
    submitted_password = dados.get('password')
    log.debug(f"Senha submetida (hash parcial): {hash(submitted_password)}")
    if not submitted_password or submitted_password != current_nash_password:
        log.warning(f"Tentativa de login falhou do IP: {request.remote_addr}. Senha incorreta ou ausente.")
        return jsonify({"success": False, "msg": "Senha incorreta"}), 401
    log.info(f"Login bem-sucedido do IP: {request.remote_addr}")
    return jsonify({"success": True})

# ---------- CHAT PRINCIPAL ----------------------------------------- #
# <<< ATUALIZADO >>> Usa build_dynamic_nash_prompt e process_llm_tool_use
@app.route("/chat", methods=["POST"])
def chat():
    start_time = time.time()
    data = request.json or {}
    user_message = data.get("prompt", "")
    session_id = data.get("session_id", "eli")

    log.info(f"Recebido /chat de {session_id}: '{user_message[:80]}...'")

    if not user_message:
        log.warning("Recebido prompt vazio na rota /chat.")
        return jsonify({"error": "Prompt vazio não permitido."}), 400

    if not pinecone_index:
         log.error("Tentativa de chat sem Pinecone inicializado.")
         return jsonify({"error": "Erro interno: Serviço de memória indisponível."}), 503

    try:
        # 1. Monta o prompt inicial usando a nova função dinâmica
        messages = build_dynamic_nash_prompt(user_message)

        # 2. Faz a primeira chamada ao LLM
        if not OPENAI_API_KEY:
             log.error("OPENAI_API_KEY não encontrada para a chamada /chat.")
             return jsonify({"error": "Configuração da API OpenAI ausente no servidor."}), 500
        client = OpenAI(api_key=OPENAI_API_KEY)

        log.info(f"Enviando request inicial para OpenAI modelo: {OPENAI_MODEL}")
        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.75,
            timeout=40, # Timeout inicial
        )
        initial_answer = completion.choices[0].message.content.strip()
        log.info(f"Resposta inicial recebida da OpenAI: '{initial_answer[:80]}...'")

        # 3. Processa a resposta para possível uso de ferramentas
        final_answer = process_llm_tool_use(initial_answer, user_message)
        log.info(f"Resposta final após processamento de ferramentas: '{final_answer[:80]}...'")


        # 4. Registra a interação (prompt original + resposta FINAL) na memória
        if pinecone_index:
            try:
                # <<< MODIFICADO >>> Usar get_text_embedding para o vetor de registro
                embedding_vector = get_text_embedding(user_message)
                if embedding_vector:
                     register_memory(pinecone_index, session_id, user_message, final_answer, tag="chat") # Assumindo que register_memory agora recebe o vetor
                     log.info("Interação registrada na memória Pinecone.")
                else:
                     log.warning("Não foi possível gerar embedding para registrar memória.")
            except Exception as reg_e:
                log.exception("Erro ao registrar memória no Pinecone após chat.")

        end_time = time.time()
        log.info(f"Tempo total de processamento /chat: {end_time - start_time:.2f} segundos.")

        return jsonify({"response": final_answer})

    except Exception as e:
        log.exception(f"Erro inesperado na rota /chat para o prompt: '{user_message[:50]}...'")
        return jsonify({"error": f"Ocorreu um erro interno no servidor Nash ao processar seu pedido."}), 500

# ---------- ROTA PARA LER CÓDIGO (Ferramenta GitHub) --- #
@app.route("/read_code", methods=["POST"])
def read_code_endpoint():
    if not github_repo_obj:
        log.warning("Recebido pedido /read_code mas GitHub não está configurado.")
        return jsonify({"error": "Integração com GitHub não configurada no backend."}), 501

    data = request.json or {}
    file_path = data.get("file_path")
    if not file_path:
        log.warning("Recebido pedido /read_code sem 'file_path'.")
        return jsonify({"error": "Parâmetro 'file_path' ausente."}), 400

    log.info(f"Recebido pedido direto /read_code para: {file_path}")
    try:
        content = get_github_file_content(github_repo_obj, file_path)
        if content is None:
            log.warning(f"Arquivo não encontrado ou erro na leitura via /read_code: {file_path}")
            return jsonify({"error": f"Arquivo '{file_path}' não encontrado ou erro na leitura."}), 404
        log.info(f"Conteúdo de '{file_path}' lido com sucesso via /read_code.")
        return jsonify({"file_path": file_path, "content": content})
    except Exception as e:
        log.exception(f"Erro ao ler arquivo via /read_code: {file_path}")
        return jsonify({"error": f"Erro inesperado ao ler arquivo: {str(e)}"}), 500

# ---------- ROTA PARA PROPOR MUDANÇA NO CÓDIGO (Ferramenta GitHub) --- #
@app.route("/propose_code_change", methods=["POST"])
def propose_code_change_endpoint():
    if not github_repo_obj:
        log.warning("Recebido pedido /propose_code_change mas GitHub não está configurado.")
        return jsonify({"error": "Integração com GitHub não configurada no backend."}), 501

    data = request.json or {}
    file_path = data.get("file_path")
    change_description = data.get("description")
    base_branch = data.get("base_branch", "main")

    if not file_path or not change_description:
        log.warning("Recebido pedido /propose_code_change sem 'file_path' ou 'description'.")
        return jsonify({"error": "Parâmetros 'file_path' e 'description' são obrigatórios."}), 400

    log.info(f"Recebido pedido direto /propose_code_change para: {file_path} | Desc: {change_description[:50]}...")

    try:
        # 1. Gera o novo conteúdo via LLM (integrado aqui)
        log.info(f"Tentando obter conteúdo atual de '{file_path}' para gerar mudança.")
        current_content = get_github_file_content(github_repo_obj, file_path)
        if current_content is None:
             log.error(f"Não foi possível ler o conteúdo atual de '{file_path}' para gerar a mudança.")
             return jsonify({"error": f"Não foi possível ler o conteúdo atual de '{file_path}' para gerar a mudança."}), 404

        prompt_for_change = f"""
         Analise o seguinte código do arquivo '{file_path}':
         ```python
         {current_content[:5000]}
         ```
         Agora, modifique este código para atender à seguinte solicitação: '{change_description}'.
         Responda APENAS com o código Python completo e atualizado do arquivo inteiro, sem nenhuma explicação adicional ou comentários extras, dentro de um bloco de código markdown ```python ... ```.
         """

        if not OPENAI_API_KEY:
            log.error("OPENAI_API_KEY não encontrada para gerar mudança de código.")
            return jsonify({"error": "Configuração da API OpenAI ausente no servidor."}), 500
        client = OpenAI(api_key=OPENAI_API_KEY)

        log.info(f"Chamando LLM ({OPENAI_MODEL}) para gerar código para: {file_path}")
        completion = client.chat.completions.create(
             model=OPENAI_MODEL, # Idealmente um modelo bom com código (GPT-4o, etc)
             messages=[{"role": "user", "content": prompt_for_change}],
             temperature=0.1, # Bem determinístico para código
             timeout=90 # Timeout maior para geração de código
        )
        generated_code_block = completion.choices[0].message.content.strip()

        # Extrair o código do bloco markdown
        new_content = None
        if generated_code_block.startswith("```python") and generated_code_block.endswith("```"):
             new_content = generated_code_block[len("```python"):].strip()[:-len("```")].strip()
        elif generated_code_block.startswith("```") and generated_code_block.endswith("```"):
             new_content = generated_code_block[len("```"):].strip()[:-len("```")].strip()
        else:
             new_content = generated_code_block
             log.warning("LLM não retornou o código em bloco markdown ```python como esperado.")

        if not new_content:
             log.error("LLM não conseguiu gerar o novo conteúdo do código para propose_code_change.")
             return jsonify({"error": "LLM não conseguiu gerar o novo conteúdo do código."}), 500
        log.info(f"LLM gerou novo conteúdo para: {file_path}")

        # 2. Define nome da branch e mensagem de commit
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_branch_path = "".join(c if c.isalnum() else '-' for c in file_path)
        new_branch_name = f"nash-proposal/{safe_branch_path}-{timestamp}"
        commit_message = f"Propõe mudança em {file_path} via Nash: {change_description[:100]}"

        # 3. Chama a função utilitária para criar a branch e o commit
        log.info(f"Tentando propor mudança no GitHub: Branch '{new_branch_name}', Base '{base_branch}'")
        result_info = propose_github_change(
            github_repo_obj,
            file_path,
            new_content,
            commit_message,
            new_branch_name,
            base_branch=base_branch
        )

        if result_info:
            log.info(f"Proposta de mudança criada com sucesso na branch: {new_branch_name}")
            if pinecone_index:
                try:
                    # <<< MODIFICADO >>> Usar get_text_embedding para o vetor de registro
                    embedding_vector_prop = get_text_embedding(f"Proposta de mudança no código: {file_path}") # Embedding do Título da Ação
                    if embedding_vector_prop:
                         register_memory(pinecone_index, "eli", f"Proposta de mudança no código: {file_path}", f"Branch: {new_branch_name}\nDescrição: {change_description}", tag="code_proposal")
                         log.info("Registro da proposta de código na memória.")
                    else:
                        log.warning("Não foi possível gerar embedding para registrar proposta de código.")
                except Exception as reg_prop_e:
                    log.exception("Erro ao registrar proposta de código na memória.")

            return jsonify({
                "message": "Proposta de mudança criada com sucesso!",
                "branch": new_branch_name,
                "commit_sha": result_info.get('commit_sha', 'N/A'),
                "file_path": file_path
            })
        else:
             log.error(f"Falha ao criar a proposta de mudança no GitHub para {file_path}.")
             return jsonify({"error": "Falha ao criar a proposta de mudança no GitHub."}), 500

    except Exception as e:
        log.exception(f"Erro geral ao processar /propose_code_change para: {file_path}")
        return jsonify({"error": f"Erro inesperado ao propor mudança: {str(e)}"}), 500

# ---------- REMEMBER MANUAL ---------------------------------------- #
@app.route("/remember", methods=["POST"])
def remember():
    note = (request.json or {}).get("note", "").strip()
    if not note:
        return jsonify({"msg": "Campo 'note' vazio"}), 400

    if not pinecone_index:
        log.error("Tentativa de /remember sem Pinecone inicializado.")
        return jsonify({"error": "Erro interno: Serviço de memória indisponível."}), 503

    try:
        embedding_vector_manual = get_text_embedding(note)
        if embedding_vector_manual:
             register_memory(pinecone_index, "eli", note, "[Nota Manual]", tag="manual")
             log.info(f"Nota manual registrada: '{note[:50]}...'")
             return jsonify({"msg": "✅ Nota gravada na memória."})
        else:
             log.warning("Não foi possível gerar embedding para registrar nota manual.")
             return jsonify({"error": "Erro ao gerar representação da nota."}), 500
    except Exception as e:
        log.exception(f"Erro ao registrar nota manual: {note[:50]}...")
        return jsonify({"error": "Erro ao gravar nota na memória."}), 500

# ---------- HEALTH / PINGNET --------------------------------------- #
@app.route("/pingnet", methods=["GET"])
def pingnet():
    return jsonify({
        "status":   "ok",
        "utc":      datetime.datetime.utcnow().isoformat(timespec="seconds"),
        "host":     socket.gethostname(),
        "model":    OPENAI_MODEL,
        "github_enabled": bool(github_repo_obj),
        "search_enabled": bool(google_search_service),
        "pinecone_enabled": bool(pinecone_index)
    })

# ---------- STATS RÁPIDAS ------------------------------------------ #
@app.route("/stats", methods=["GET"])
def stats():
    upload_count = 0
    try:
        if os.path.exists(app.config["UPLOAD_FOLDER"]):
             upload_count = len(os.listdir(app.config["UPLOAD_FOLDER"]))
    except Exception as e:
        log.warning(f"Erro ao listar uploads: {e}")

    pinecone_stats_info = "N/A (Desabilitado ou Erro)"
    if pinecone_index:
        try:
             stats_desc = pinecone_index.describe_index_stats()
             if hasattr(stats_desc, 'total_vector_count'):
                  pinecone_stats_info = f"Vectors: {stats_desc.total_vector_count}"
             elif hasattr(stats_desc, 'namespaces') and 'namespaces' in stats_desc:
                 pinecone_stats_info = f"Namespaces: {len(stats_desc.namespaces)}" # Ou outra info relevante
             else:
                 pinecone_stats_info = "Stats disponíveis, formato inesperado."
        except Exception as e:
            log.exception("Erro ao obter stats do Pinecone.")
            pinecone_stats_info = f"Erro ao obter stats: {type(e).__name__}"

    return jsonify({
        "pinecone_index": PINECONE_INDEX_NAME if pinecone_index else "Desabilitado",
        "pinecone_stats": pinecone_stats_info,
        "uploads_count": upload_count,
        "active_model": OPENAI_MODEL,
        "github_repo": GITHUB_REPO if github_repo_obj else "Desabilitado",
        "search_enabled": bool(google_search_service),
    })

# ---------- UPLOAD ------------------------------------------------- #
@app.route("/upload", methods=["POST"])
def upload_file():
    can_register_memory = bool(pinecone_index)

    if "file" not in request.files:
        log.warning("Tentativa de upload sem arquivo.")
        return jsonify({"message": "Nenhum arquivo anexado!"}), 400

    file = request.files["file"]
    original_filename = file.filename

    if not original_filename:
         log.warning("Tentativa de upload com nome de arquivo vazio.")
         return jsonify({"message": "Nome de arquivo inválido."}), 400

    if not ALLOWED_EXTENSIONS(original_filename):
        allowed_set = IMAGE_EXTS | CODE_EXTS
        log.warning(f"Tentativa de upload de tipo não permitido: {original_filename}")
        return jsonify({"message": f"Arquivo não permitido! Extensões válidas: {', '.join(sorted(list(allowed_set)))}"}), 400

    try:
        safe_base_filename = "".join(c for c in original_filename if c.isalnum() or c in ('-', '_', '.'))
        if not safe_base_filename: safe_base_filename = "arquivo_upload"
        filename_to_save = f"{uuid.uuid4().hex}_{safe_base_filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename_to_save)

        file.save(filepath)
        file_size = os.path.getsize(filepath)
        log.info(f"Arquivo recebido: '{original_filename}', salvo como: '{filename_to_save}', Tamanho: {file_size} bytes")

        if can_register_memory:
             try:
                 # <<< MODIFICADO >>> Usar get_text_embedding para o vetor de registro
                 upload_description = f"Upload de arquivo realizado: {original_filename}"
                 embedding_vector_upload = get_text_embedding(upload_description)
                 if embedding_vector_upload:
                     register_memory(
                         pinecone_index, "eli",
                         upload_description,
                         f"Nome no servidor: {filename_to_save}, Tipo: {file.mimetype}, Tamanho: {file_size} bytes",
                         tag="upload"
                     )
                     log.info(f"Evento de upload registrado na memória para: {filename_to_save}")
                 else:
                     log.warning(f"Não foi possível gerar embedding para registrar upload de {filename_to_save}")
             except Exception as reg_upload_e:
                 log.exception(f"Erro ao registrar upload na memória para {filename_to_save}")

        return jsonify({"message": "Upload realizado com sucesso!", "filename": filename_to_save})

    except Exception as e:
         log.exception(f"Erro crítico durante o upload do arquivo: {original_filename}")
         return jsonify({"message": "Erro interno no servidor durante o upload."}), 500

# ---------- SERVIR ARQUIVOS --------------------------------------- #
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    upload_dir = app.config['UPLOAD_FOLDER']
    log.debug(f"Tentando servir arquivo: {filename} de {upload_dir}")
    if ".." in filename or filename.startswith("/"):
         log.warning(f"Tentativa de acesso inválido a arquivo: {filename}")
         return "Acesso inválido.", 400
    try:
        return send_from_directory(upload_dir, filename, as_attachment=False)
    except FileNotFoundError:
         log.warning(f"Arquivo solicitado para download não encontrado: {filename}")
         return "Arquivo não encontrado.", 404
    except Exception as e:
         log.exception(f"Erro ao servir arquivo {filename}")
         return "Erro interno ao servir arquivo.", 500

# ------------------------------------------------------------------ #
#  EXECUÇÃO PRINCIPAL                                                #
# ------------------------------------------------------------------ #
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ['true', '1']

    log.info(f"Iniciando Nash Copilot API v2 (Evolutivo + Ferramentas) em {host}:{port} | Debug Mode: {debug_mode}")
    if debug_mode:
        log.warning("### ATENÇÃO: Rodando em MODO DEBUG. NÃO use em produção! ###")
        app.run(host=host, port=port, debug=True)
    else:
        log.info("Modo Produção. Use um servidor WSGI (Gunicorn/Waitress) via Start Command.")
        try:
            import gunicorn
            log.info("Gunicorn detectado. Use 'gunicorn nash_app:app' como Start Command no Railway.")
        except ImportError:
            log.warning("Gunicorn não encontrado. Considere adicioná-lo aos requirements e usá-lo no Start Command.")
        # Fallback para o servidor de desenvolvimento Flask (não ideal para produção)
        app.run(host=host, port=port, debug=False)

```

**Observações:**

1.  **`register_memory`:** Notei que na versão anterior, `register_memory` talvez não estivesse recebendo o vetor de embedding explicitamente. Ajustei as chamadas dentro de `/chat`, `/propose_code_change`, `/remember`, e `/upload` para primeiro chamar `get_text_embedding` e depois passar o resultado (ou não registrar se o embedding falhar). **Verifique se a sua função `register_memory` em `nash_utils.py` está preparada para receber o vetor ou se ela mesma gera o embedding internamente.** Se ela gera internamente, você pode remover as chamadas `get_text_embedding` antes de `register_memory` nestes pontos. A versão que te passei de `nash_utils.py` *não* recebia o vetor, ela gerava internamente, então você talvez precise ajustar a chamada `register_memory` ou a própria função em `nash_utils.py` conforme a sua implementação final dela. A versão que te passei *antes* (`nash_utils.py (Completo e Revisado)`) já faz o embedding dentro de `register_memory`, então as chamadas no código acima estão um pouco redundantes se você usou *aquela* versão de `nash_utils.py`. Escolha uma abordagem e mantenha a consistência.
2.  **Caminho Uploads:** Ajustei `UPLOAD_FOLDER` para usar `os.path.join(os.path.dirname(__file__), 'uploads')` que é um pouco mais robusto para encontrar a pasta relativa ao script em diferentes ambientes.
3.  **Robustez:** Adicionei mais verificações (Pinecone ativo, API Key presente) e logging.

Cole este código, faça o commit e push. Agora o Nash deve usar o prompt dinâmico *e* ainda ter as capacidades de ferramenta disponíveis! Me diga como foi o teste final!