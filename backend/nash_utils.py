# nash_utils.py

import os
import hashlib
from openai import OpenAI
from pinecone import Pinecone

# --- Inicialização OpenAI & Pinecone ---
def init_openai(api_key: str):
    """Define a variável de ambiente para o cliente OpenAI."""
    os.environ["OPENAI_API_KEY"] = api_key

def init_pinecone(api_key: str, index_name: str):
    """Inicializa o client Pinecone e retorna o Index."""
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)

# --- Chat Completion (opcional) ---
def create_chat_completion(messages: list, model: str = None) -> str:
    """
    Cria uma completion de chat usando o modelo definido em OPENAI_MODEL ou
    um model passado diretamente.
    """
    model = model or os.getenv("OPENAI_MODEL", "o4-mini")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content.strip()

# --- Embedding de Texto ---
def get_text_embedding(text: str, model: str = None) -> list:
    """
    Gera embedding para o texto usando o modelo definido em OPENAI_EMBEDDING_MODEL
    ou o padrão text-embedding-ada-002.
    """
    model = model or os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.embeddings.create(input=[text], model=model)
    return resp.data[0].embedding

# --- Memória Vetorizada (Pinecone) ---
def register_memory(pinecone_index, user_id: str, user_input: str, agent_response: str, tag: str = "chat"):
    """
    Salva no Pinecone um vetor representando a interação (prompt + resposta).
    """
    text = f"[{tag}] Prompt: {user_input}\nResposta Nash: {agent_response}"
    vec = get_text_embedding(user_input)
    id_hash = hashlib.sha256((user_id + user_input).encode("utf-8")).hexdigest()
    pinecone_index.upsert(vectors=[{
        "id": id_hash,
        "values": vec,
        "metadata": {"user_id": user_id, "text": text, "tag": tag}
    }])

def fetch_relevant_memories(pinecone_index, user_input: str, top_k: int = 4) -> list:
    """
    Recupera os top_k fragmentos de memória mais relevantes do Pinecone
    para um dado input do usuário.
    """
    vec = get_text_embedding(user_input)
    res = pinecone_index.query(vector=vec, top_k=top_k, include_metadata=True)
    results = []
    for match in res.matches:
        txt = match.metadata.get("text", "")
        results.append({"score": match.score, "text": txt})
    return results

# --- Logger / Contexto de Onboarding ---
def nash_log(tag: str = "ONBOARDING") -> str:
    """
    Lê e retorna o conteúdo de nash_memory_init.md como memória inicial.
    """
    try:
        with open("nash_memory_init.md", "r", encoding="utf-8") as f:
            md = f.read()
        return f"[MEMÓRIA INICIAL – {tag}]\n{md}"
    except Exception as e:
        return f"[MEMÓRIA INICIAL INACESSÍVEL – {e}]"

# --- Validação de Extensões para Uploads ---
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"}
CODE_EXTS  = {".py", ".txt", ".md", ".json", ".csv", ".pdf"}

def ALLOWED_EXTENSIONS(filename: str) -> bool:
    """
    Retorna True se o arquivo termina em uma das extensões permitidas
    (imagem ou texto/código).
    """
    fn = filename.lower()
    return any(fn.endswith(ext) for ext in IMAGE_EXTS | CODE_EXTS)