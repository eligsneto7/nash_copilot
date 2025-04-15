# nash_utils.py

import openai
from pinecone import Pinecone
import os
import json
import hashlib

# --- Inicialização dos recursos externos ---

def init_openai(api_key):
    openai.api_key = api_key

def init_pinecone(api_key, index_name):
    pc = Pinecone(api_key=api_key)
    return pc.Index(index_name)

# --- Embeddings e Consultas GPT ---
def create_embedding(text, model="gpt-4-1106-preview"):
    # Esta função chama o modelo GPT-4.1 para obter resposta OpenAI by Chat API
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{
            "role": "system",
            "content": (
                "Você é Nash, um copiloto digital sci-fi, inteligente, sarcástico, "
                "personalidade avançada, memoria evolutiva, para Eli, empresário e futurista."
            )
        }, {
            "role": "user",
            "content": text
        }]
    )
    return completion.choices[0].message.content.strip()

def get_text_embedding(text, model="text-embedding-ada-002"):
    result = openai.Embedding.create(
        input=[text], model=model
    )
    return result["data"][0]["embedding"]

# --- Memória Vetorizada (Pinecone) ---
def register_memory(pinecone_index, user_id, user_input, agent_response, tag="chat"):
    # Salva o contexto de cada interação no Pinecone para busca futura
    text = f"[{tag}] Prompt: {user_input}\nResposta Nash: {agent_response}"
    vec = get_text_embedding(user_input)
    id_hash = hashlib.sha256((user_id + user_input).encode()).hexdigest()
    pinecone_index.upsert(vectors=[{
        "id": id_hash,
        "values": vec,
        "metadata": {"user_id": user_id, "text": text, "tag": tag}
    }])

def fetch_relevant_memories(pinecone_index, user_input, top_k=4):
    vec = get_text_embedding(user_input)
    res = pinecone_index.query(vector=vec, top_k=top_k, include_metadata=True)
    results = []
    for match in res['matches']:
        text = match.get("metadata", {}).get("text", "")
        results.append({"score": match.get("score", 0), "text": text})
    return results

# --- Logger/Contexto de Lore Inicial ---
def nash_log(tag="ONBOARDING"):
    try:
        with open("nash_memory_init.md", "r", encoding="utf-8") as f:
            md = f.read()
        return f"[MEMÓRIA INICIAL – {tag}]\n{md}"
    except Exception as e:
        return f"[MEMÓRIA INICIAL INACESSÍVEL – {e}]"

# --- Uploads (Validação de extensão) ---
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".svg"}
CODE_EXTS = {".py", ".txt", ".md", ".json", ".csv", ".pdf"}
def ALLOWED_EXTENSIONS(filename):
    fname = filename.lower()
    return any(fname.endswith(ext) for ext in IMAGE_EXTS | CODE_EXTS)