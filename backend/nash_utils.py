# nash_utils.py (Versão Corrigida - Pinecone SDK Atualizado)

import os
import uuid
import logging
import datetime
import json
from typing import List, Dict, Optional, Tuple, Any # Melhor usar typing explícito

from openai import OpenAI, OpenAIError # Importar erro específico ajuda no tratamento
# <<< MODIFICADO >>> Importações Pinecone atualizadas
from pinecone import Pinecone # Nova classe principal
# from pinecone import Index # Index é obtido via instância Pinecone
# import pinecone <<< REMOVIDO >>> Não usar mais o módulo diretamente para init

from github import Github, GithubException # Importar erro específico
from googleapiclient.discovery import build, Resource # Tipagem para o serviço
from google.auth.exceptions import GoogleAuthError # Importar erro específico
import time # Para retry logic
from dotenv import load_dotenv # Útil para desenvolvimento local

# Carrega variáveis de ambiente de .env se existir (bom para dev local)
load_dotenv()

# Configuração do Logger
log = logging.getLogger(__name__)
# Configuração básica (pode ser feita no app principal também)
if not log.hasHandlers():
     logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')

# --- Constantes Globais ---
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small" # Modelo de embedding padrão
# Definindo conjuntos de extensões para clareza
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"}
CODE_EXTS = {".py", ".txt", ".md", ".json", ".csv", ".pdf", ".log", ".sh", ".yaml", ".toml", ".html", ".css", ".js", ".ipynb"}
AUDIO_VIDEO_EXTS = {".mp3", ".wav", ".ogg", ".mp4", ".mov", ".avi", ".webm"}
ALLOWED_EXTENSIONS_SET = IMAGE_EXTS | CODE_EXTS | AUDIO_VIDEO_EXTS

# --- Inicialização de Clientes ---

# Cache simples para clientes (evita reinicializar toda hora)
_openai_client = None
_pinecone_client = None # <<< MODIFICADO >>> Cache para o cliente Pinecone
_pinecone_index_obj = None # <<< MODIFICADO >>> Cache para o objeto Index
_github_repo = None
_google_search_service = None

def init_openai(api_key: Optional[str] = None) -> Optional[OpenAI]:
    """Inicializa e retorna o cliente OpenAI."""
    global _openai_client
    if _openai_client:
        return _openai_client

    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        log.error("Chave da API OpenAI (OPENAI_API_KEY) não encontrada.")
        return None
    try:
        _openai_client = OpenAI(api_key=api_key)
        log.info("Cliente OpenAI inicializado com sucesso.")
        # Teste rápido de conexão (opcional, mas útil)
        # _openai_client.models.list()
        # log.info("Teste de conexão OpenAI OK.")
        return _openai_client
    except OpenAIError as e:
        log.exception(f"Falha ao inicializar cliente OpenAI: {e}")
        return None
    except Exception as e:
         log.exception(f"Erro inesperado ao inicializar cliente OpenAI: {e}")
         return None

# <<< ATUALIZADO >>> Função init_pinecone revisada para novo SDK
def init_pinecone(api_key: Optional[str] = None, index_name: Optional[str] = None) -> Optional[Any]: # Retorna objeto Index
    """Inicializa e retorna o objeto Index do Pinecone usando o novo SDK."""
    global _pinecone_client, _pinecone_index_obj
    if _pinecone_index_obj:
        return _pinecone_index_obj

    api_key = api_key or os.getenv("PINECONE_API_KEY")
    index_name = index_name or os.getenv("PINECONE_INDEX_NAME")

    if not api_key or not index_name:
        log.error("Chave da API Pinecone (PINECONE_API_KEY) ou nome do Index (PINECONE_INDEX_NAME) não encontrados.")
        return None

    try:
        # 1. Inicializa o cliente Pinecone (se ainda não foi)
        if not _pinecone_client:
            log.info(f"Inicializando Pinecone Client...")
            _pinecone_client = Pinecone(api_key=api_key)
            log.info(f"Cliente Pinecone instanciado.")

        # 2. Verifica se o índice existe <<< NOVA ABORDAGEM >>>
        log.info(f"Verificando existência do Index Pinecone: {index_name}...")
        try:
            # Chama list_indexes() - o resultado pode variar um pouco entre versões
            indexes_description = _pinecone_client.list_indexes()
            log.info(f"Resultado bruto de list_indexes(): {indexes_description}") # LOG EXTRA

            # Tenta extrair nomes assumindo que é uma lista de objetos/dicionários com 'name'
            # ou diretamente o atributo .names se for a estrutura esperada
            available_names = []
            if hasattr(indexes_description, 'names'): # Verifica se a estrutura esperada com .names existe
                 available_names = indexes_description.names
                 log.info(f"Extraído via .names: {available_names} (Tipo: {type(available_names)})")
            elif isinstance(indexes_description, list): # Verifica se é uma lista (outra estrutura possível)
                available_names = [index_info['name'] for index_info in indexes_description if 'name' in index_info]
                log.info(f"Extraído via iteração de lista: {available_names} (Tipo: {type(available_names)})")
            else:
                 # Se não for nenhuma das estruturas conhecidas, loga e falha
                 log.error(f"Estrutura inesperada retornada por list_indexes(): {type(indexes_description)}. Não foi possível extrair nomes.")
                 return None # Não é possível verificar

            # Verifica se available_names é realmente iterável agora
            if not isinstance(available_names, (list, tuple, set)):
                 log.error(f"Falha ao obter uma lista iterável de nomes de índice. Obtido: {available_names} (Tipo: {type(available_names)})")
                 return None

            # PASSO 3: Verificar a existência na lista 'available_names'
            if index_name not in available_names:
                log.error(f"O Index Pinecone '{index_name}' não foi encontrado na sua conta/projeto. Índices disponíveis: {available_names}")
                return None # Retorna None se não existe

            log.info(f"Index '{index_name}' encontrado na lista de nomes disponíveis.")

        except ApiException as list_err:
             log.exception(f"Erro da API Pinecone ao tentar listar índices: {list_err}")
             return None # Falha se não conseguir nem listar
        except Exception as list_generic_err: # Captura outros erros inesperados ao listar/processar
             log.exception(f"Erro inesperado ao processar a lista de índices: {list_generic_err}")
             return None

        # 3. Obtém o objeto Index
        log.info(f"Obtendo objeto Index para '{index_name}'...")
        _pinecone_index_obj = _pinecone_client.Index(index_name)

        # 4. Valida a conexão fazendo uma chamada rápida
        log.info(f"Validando conexão com o Index '{index_name}' via describe_index_stats...")
        stats = _pinecone_index_obj.describe_index_stats()
        log.info(f"Conectado ao Pinecone Index '{index_name}'. Status: {stats}")
        return _pinecone_index_obj

    except ApiException as api_e: # Erro mais específico da API Pinecone
         log.exception(f"Erro de API Pinecone durante a inicialização/conexão com Index '{index_name}': {api_e}")
         _pinecone_client = None
         _pinecone_index_obj = None
         return None
    except Exception as e:
        log.exception(f"Erro genérico durante a inicialização/conexão com Pinecone Index '{index_name}'. Tipo: {type(e).__name__}")
        _pinecone_client = None
        _pinecone_index_obj = None
        return None

def init_github(pat: Optional[str] = None, repo_name: Optional[str] = None) -> Optional[Any]: # Retorna 'Repository' mas Any evita dependência forte
    """Inicializa e retorna o objeto Repository do PyGithub."""
    global _github_repo
    if _github_repo:
        return _github_repo

    pat = pat or os.getenv("GITHUB_PAT")
    repo_name = repo_name or os.getenv("GITHUB_REPO") # Esperado formato "usuario/repo"

    if not pat or not repo_name:
        log.warning("GITHUB_PAT ou GITHUB_REPO não configurados. Funções GitHub desabilitadas.")
        return None

    try:
        g = Github(pat)
        user = g.get_user() # Verifica autenticação
        log.info(f"GitHub autenticado como: {user.login}")
        _github_repo = g.get_repo(repo_name)
        log.info(f"Acesso ao repositório GitHub '{_github_repo.full_name}' concedido.")
        return _github_repo
    except GithubException as e:
        log.exception(f"Erro do GitHub ao inicializar ou acessar repositório '{repo_name}': {e.status} {e.data}")
        return None
    except Exception as e:
        log.exception(f"Erro inesperado ao inicializar GitHub para o repositório '{repo_name}': {e}")
        return None

def init_google_search(api_key: Optional[str] = None) -> Optional[Resource]:
    """Inicializa e retorna o cliente de serviço Google Custom Search."""
    global _google_search_service
    if _google_search_service:
        return _google_search_service

    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        log.warning("GOOGLE_API_KEY não configurado. Busca na Web desabilitada.")
        return None

    try:
        # Não precisa do CSE ID aqui, só na hora da busca
        _google_search_service = build("customsearch", "v1", developerKey=api_key)
        log.info("Cliente Google Custom Search API inicializado.")
        return _google_search_service
    except GoogleAuthError as e:
         log.exception(f"Erro de autenticação Google ao inicializar Search API: {e}")
         return None
    except Exception as e:
        log.exception(f"Erro inesperado ao inicializar Google Custom Search API: {e}")
        return None


# --- Funções de Embedding e Memória ---

def get_text_embedding(text: str, client: Optional[OpenAI] = None, retries: int = 3, delay: int = 2) -> Optional[List[float]]:
    """Gera embedding para um texto usando o modelo OpenAI configurado."""
    if not text or not isinstance(text, str):
         log.warning("Tentativa de gerar embedding para texto vazio ou inválido.")
         return None

    client = client or init_openai() # Tenta inicializar se não foi passado
    if not client:
        log.error("Cliente OpenAI não disponível para get_text_embedding.")
        return None

    text_to_embed = text.replace("\n", " ") # Modelo da OpenAI funciona melhor sem novas linhas

    for attempt in range(retries):
        try:
            response = client.embeddings.create(
                input=[text_to_embed], # Espera uma lista de strings
                model=OPENAI_EMBEDDING_MODEL
            )
            # A resposta agora é um objeto com um atributo 'data' que é uma lista de embeddings
            if response.data and len(response.data) > 0:
                embedding_vector = response.data[0].embedding
                # log.debug(f"Embedding gerado com sucesso para texto (início): '{text_to_embed[:50]}...' Dimensão: {len(embedding_vector)}")
                return embedding_vector
            else:
                log.error("Resposta da API de embedding da OpenAI não continha dados válidos.")
                return None # Retorna None se a resposta for inesperada

        except OpenAIError as e:
            log.error(f"Erro da API OpenAI ao gerar embedding (tentativa {attempt + 1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1)) # Backoff exponencial simples
            else:
                log.error("Número máximo de tentativas excedido para gerar embedding.")
                return None
        except Exception as e:
            log.exception(f"Erro inesperado ao gerar embedding (tentativa {attempt + 1}/{retries}): {e}")
            # Não tenta novamente em erros inesperados
            return None
    return None # Caso o loop termine sem sucesso

# <<< ATUALIZADO >>> Tipo do parâmetro 'index' e tratamento de erro
def fetch_relevant_memories(index: Any, query_text: str, top_k: int = 3, namespace: str = "nash-default") -> List[Dict[str, Any]]:
    """Busca memórias relevantes no Pinecone para um dado texto."""
    if not index: # 'index' agora é o objeto retornado por pc.Index()
        log.error("Objeto Index Pinecone não fornecido para fetch_relevant_memories.")
        return []
    if not query_text:
         log.warning("Texto de consulta vazio para fetch_relevant_memories.")
         return []

    query_embedding = get_text_embedding(query_text)
    if not query_embedding:
        log.error("Falha ao gerar embedding para a consulta de memória.")
        return []

    try:
        log.info(f"Consultando Pinecone (top_k={top_k}, namespace={namespace}) para: '{query_text[:50]}...'")
        # A chamada a 'query' no objeto Index está correta
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            namespace=namespace
        )

        memories = []
        # A estrutura de 'results.matches' é mantida no novo SDK
        if results and results.matches:
            for match in results.matches:
                metadata = match.get('metadata', {})
                score = match.get('score', 0.0)
                memory_text = metadata.get('text', '[Texto da memória ausente]')
                memory_response = metadata.get('response', '')
                timestamp = metadata.get('timestamp', 'N/A')

                memories.append({
                    "id": match.id,
                    "score": score,
                    "text": memory_text,
                    "response": memory_response,
                    "timestamp": timestamp,
                    "metadata": metadata
                })
            log.info(f"Encontradas {len(memories)} memórias relevantes.")
        else:
             log.info("Nenhuma memória relevante encontrada na consulta ao Pinecone.")

        return memories

    # except pinecone.exceptions.ApiException as e: <<< ANTIGO >>>
    except Exception as e: # <<< ATUALIZADO >>> Captura exceção genérica ou específica do novo SDK
        log.exception(f"Erro durante a consulta de memória no Pinecone. Tipo: {type(e).__name__}")
        return []

# <<< ATUALIZADO >>> Tipo do parâmetro 'index' e tratamento de erro
def register_memory(index: Any,
                    session_id: str,
                    text: str,
                    response: str,
                    tag: str = "chat",
                    namespace: str = "nash-default",
                    embedding_vector: Optional[List[float]] = None) -> bool:
    """
    Registra uma interação ou nota na memória Pinecone.
    Pode usar um embedding pré-calculado ou gerar um internamente.
    """
    if not index: # 'index' agora é o objeto retornado por pc.Index()
        log.error("Objeto Index Pinecone não fornecido para register_memory.")
        return False
    if not text:
         log.warning("Tentativa de registrar memória com texto vazio.")
         return False

    vector_id = str(uuid.uuid4())
    timestamp = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

    # --- Lógica de Embedding ---
    if embedding_vector:
        log.debug(f"Usando embedding pré-calculado para registrar memória (ID: {vector_id}).")
        if not isinstance(embedding_vector, list) or not all(isinstance(x, float) for x in embedding_vector):
             log.error(f"Embedding pré-calculado inválido fornecido para register_memory (ID: {vector_id}). Tipo: {type(embedding_vector)}")
             return False
    else:
        log.debug(f"Gerando embedding internamente para registrar memória (ID: {vector_id}).")
        combined_text = f"{text} [NASH]: {response}" if response else text
        embedding_vector = get_text_embedding(combined_text)
        if not embedding_vector:
            log.error(f"Falha ao gerar embedding interno para registro de memória (ID: {vector_id}).")
            return False

    # --- Criação do Metadata ---
    metadata = {
        "session_id": session_id,
        "text": text,
        "response": response or "",
        "tag": tag,
        "timestamp": timestamp,
        "text_length": len(text),
        "response_length": len(response or ""),
    }

    # --- Upsert no Pinecone ---
    try:
        # A chamada a 'upsert' no objeto Index está correta
        index.upsert(vectors=[(vector_id, embedding_vector, metadata)], namespace=namespace)
        log.info(f"Memória registrada (Tag: {tag}, Namespace: {namespace}) ID: {vector_id} para sessão: {session_id}")
        return True
    # except pinecone.exceptions.ApiException as e: <<< ANTIGO >>>
    except Exception as e: # <<< ATUALIZADO >>> Captura exceção genérica ou específica do novo SDK
        log.exception(f"Erro durante o upsert da memória no Pinecone (ID: {vector_id}). Tipo: {type(e).__name__}")
        return False

def nash_log(section: str) -> str:
    """Lê o conteúdo de uma seção específica do arquivo nash_memory_init.md."""
    try:
        # Tenta caminhos relativos comuns
        possible_paths = [
            "nash_memory_init.md",
            os.path.join(os.path.dirname(__file__), "nash_memory_init.md")
        ]
        filepath = None
        for p in possible_paths:
            if os.path.exists(p):
                filepath = p
                break

        if not filepath:
            log.warning(f"Arquivo 'nash_memory_init.md' não encontrado.")
            return f"[AVISO: Arquivo nash_memory_init.md não encontrado. Usando fallback para seção '{section}']"

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Simples parser baseado em marcadores ## SEÇÃO ## ... ## FIM SEÇÃO ##
        start_marker = f"## {section.upper()} ##"
        end_marker = f"## FIM {section.upper()} ##"
        start_index = content.find(start_marker)
        if start_index == -1:
            log.warning(f"Seção '{section}' não encontrada com marcador '{start_marker}' em nash_memory_init.md")
            return f"[AVISO: Seção '{section}' não encontrada em nash_memory_init.md]"

        start_index += len(start_marker)
        end_index = content.find(end_marker, start_index)
        if end_index == -1:
            log.warning(f"Marcador final '{end_marker}' não encontrado para seção '{section}' em nash_memory_init.md")
            # Retorna tudo a partir do start_marker se não achar o end_marker
            return content[start_index:].strip()

        return content[start_index:end_index].strip()

    except FileNotFoundError:
         # Este caso já é tratado acima, mas por segurança
         log.warning(f"Arquivo 'nash_memory_init.md' não encontrado durante nash_log.")
         return f"[AVISO: Arquivo nash_memory_init.md não encontrado ao tentar ler seção '{section}']"
    except Exception as e:
        log.exception(f"Erro ao ler seção '{section}' de nash_memory_init.md: {e}")
        return f"[ERRO: Falha ao ler memória fundamental da seção '{section}']"


# --- Funções de Validação e Utilitários ---

def allowed_file(filename: str) -> bool:
    """Verifica se a extensão do arquivo é permitida."""
    if not filename or '.' not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS_SET


# --- Funções de Integração (GitHub, Google Search) ---

def get_github_file_content(repo: Any, file_path: str, branch: str = "main") -> Optional[str]:
    """Obtém o conteúdo de um arquivo do repositório GitHub configurado."""
    if not repo:
        log.error("Objeto repositório GitHub não inicializado para get_github_file_content.")
        return None
    try:
        log.info(f"Tentando ler arquivo '{file_path}' da branch '{branch}' no repo {repo.full_name}")
        # Tenta obter o conteúdo usando ref=branch
        file_content = repo.get_contents(file_path, ref=branch)

        # Verifica se é um arquivo (e não diretório) e decodifica
        if file_content.type == "file":
            decoded_content = file_content.decoded_content.decode("utf-8")
            log.info(f"Conteúdo de '{file_path}' lido com sucesso (Tamanho: {len(decoded_content)} bytes).")
            return decoded_content
        else:
             log.warning(f"Caminho '{file_path}' na branch '{branch}' não é um arquivo (Tipo: {file_content.type}).")
             return None # Não é um arquivo

    except GithubException as e:
        if e.status == 404:
            log.warning(f"Arquivo '{file_path}' não encontrado na branch '{branch}' do repositório. Status: {e.status}")
        else:
            log.exception(f"Erro do GitHub ao obter conteúdo de '{file_path}' (Branch: {branch}): Status {e.status} - {e.data}")
        return None
    except Exception as e:
        log.exception(f"Erro inesperado ao obter conteúdo de '{file_path}' (Branch: {branch}): {e}")
        return None


def propose_github_change(repo: Any, file_path: str, new_content: str, commit_message: str, new_branch_name: str, base_branch: str = "main") -> Optional[Dict[str, str]]:
    """
    Cria uma nova branch, atualiza/cria um arquivo nela com o novo conteúdo e faz o commit.
    Retorna informações sobre o commit se bem-sucedido.
    """
    if not repo:
        log.error("Objeto repositório GitHub não inicializado para propose_github_change.")
        return None

    try:
        # 1. Obter SHA da branch base para criar a nova branch a partir dela
        log.info(f"Obtendo SHA da branch base '{base_branch}'...")
        base_ref = repo.get_git_ref(f"heads/{base_branch}")
        base_sha = base_ref.object.sha
        log.info(f"SHA da branch base '{base_branch}' obtido: {base_sha}")

        # 2. Criar a nova branch
        new_ref_path = f"refs/heads/{new_branch_name}"
        try:
            log.info(f"Criando nova branch '{new_branch_name}' a partir de '{base_branch}'...")
            repo.create_git_ref(ref=new_ref_path, sha=base_sha)
            log.info(f"Branch '{new_branch_name}' criada com sucesso.")
        except GithubException as e:
            # Código 422 geralmente indica que a branch já existe
            if e.status == 422 and "Reference already exists" in str(e.data):
                 log.warning(f"Branch '{new_branch_name}' já existe. Tentando prosseguir com a atualização nela.")
                 # Não retorna erro, tenta atualizar o arquivo na branch existente
            else:
                 raise # Re-lança outros erros de criação de branch

        # 3. Verificar se o arquivo existe na nova branch para decidir entre criar/atualizar
        current_sha = None
        try:
            existing_file = repo.get_contents(file_path, ref=new_branch_name)
            current_sha = existing_file.sha
            log.info(f"Arquivo '{file_path}' encontrado na branch '{new_branch_name}'. Será atualizado (SHA: {current_sha}).")
            # Atualizar o arquivo
            commit_info = repo.update_file(
                path=file_path,
                message=commit_message,
                content=new_content,
                sha=current_sha,
                branch=new_branch_name
            )
            action = "atualizado"
        except GithubException as e:
            if e.status == 404:
                log.info(f"Arquivo '{file_path}' não encontrado na branch '{new_branch_name}'. Será criado.")
                # Criar o arquivo
                commit_info = repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=new_content,
                    branch=new_branch_name
                )
                action = "criado"
            else:
                 # Outro erro ao tentar obter o arquivo existente
                 log.exception(f"Erro do GitHub ao verificar/atualizar arquivo '{file_path}' na branch '{new_branch_name}': Status {e.status} - {e.data}")
                 return None # Falha

        # 4. Logar sucesso e retornar info
        commit_sha = commit_info['commit'].sha
        log.info(f"Arquivo '{file_path}' {action} com sucesso na branch '{new_branch_name}'. Commit SHA: {commit_sha}")
        return {"commit_sha": commit_sha, "branch": new_branch_name, "file_path": file_path}

    except GithubException as e:
        log.exception(f"Erro do GitHub durante a proposta de mudança para '{file_path}' na branch '{new_branch_name}': Status {e.status} - {e.data}")
        return None
    except Exception as e:
        log.exception(f"Erro inesperado durante a proposta de mudança no GitHub para '{file_path}': {e}")
        return None


def perform_google_search(service: Optional[Resource], cse_id: Optional[str], query: str, num_results: int = 5) -> Optional[List[Dict[str, str]]]:
    """Realiza uma busca usando a Google Custom Search API."""
    if not service:
        log.error("Serviço Google Search não inicializado para perform_google_search.")
        return None
    if not cse_id:
        log.error("Google Custom Search Engine ID (GOOGLE_CSE_ID) não configurado.")
        return None
    if not query:
        log.warning("Query de busca vazia fornecida.")
        return None

    try:
        log.info(f"Executando Google Search (CSE ID: {cse_id}) para query: '{query}' (num_results={num_results})")
        # Parâmetros da API: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
        result = service.cse().list(
            q=query,
            cx=cse_id,
            num=num_results,
            # lr="lang_pt", # Opcional: Restringir a PT
            # siteSearch="exemplo.com", # Opcional: Buscar em site específico
            # filter="1", # Opcional: Remover resultados duplicados
        ).execute()

        items = result.get('items', [])
        if not items:
             log.info(f"Busca no Google para '{query}' não retornou resultados.")
             return [] # Retorna lista vazia se não houver itens

        search_results = []
        for item in items:
            search_results.append({
                "title": item.get("title", "N/A"),
                "link": item.get("link", "#"),
                "snippet": item.get("snippet", "N/A")
            })
        log.info(f"Busca no Google retornou {len(search_results)} resultados.")
        return search_results

    except GoogleAuthError as e:
         log.exception(f"Erro de autenticação Google durante a busca: {e}")
         return None
    except Exception as e:
        # A API pode retornar erros específicos que podem ser tratados aqui (e.g., cota excedida)
        log.exception(f"Erro inesperado durante a busca no Google para '{query}': {e}")
        return None

# --- Fim de nash_utils.py ---