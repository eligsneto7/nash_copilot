# -*- coding: utf-8 -*-
"""
Nash Copilot ‑ API Flask
Arquivo totalmente revisado para usar o modelo OpenAI `gpt‑4o`
e para nunca mais devolver HTML cru em caso de erro :-)
"""
from flask import Flask, request, jsonify, send_from_directory
import os, uuid, logging
from openai import OpenAI                              # v1.x
from nash_utils import (
    init_openai, init_pinecone,
    create_embedding, fetch_relevant_memories,
    register_memory, nash_log, ALLOWED_EXTENSIONS,
)

# ------------------------------------------------------------------ #
#  CONFIGURAÇÕES                                                     #
# ------------------------------------------------------------------ #
OPENAI_KEY      = os.getenv("OPENAI_API_KEY")
PINECONE_KEY    = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX  = os.getenv("PINECONE_INDEX_NAME")
NASH_PASSWORD   = os.getenv("NASH_PASSWORD", "889988")

init_openai(OPENAI_KEY)
pinecone_index = init_pinecone(PINECONE_KEY, PINECONE_INDEX)

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------------------------------------------------ #
#  ROTAS                                                             #
# ------------------------------------------------------------------ #
@app.route("/", methods=["GET"])
def home():
    return "‍ Nash Copilot API online! Use /login, /chat, /upload."

# ---------- LOGIN -------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    if (request.json or {}).get("password") != NASH_PASSWORD:
        return jsonify({"success": False, "msg": "Senha incorreta"}), 401
    return jsonify({"success": True})

# ---------- CHAT --------------------------------------------------- #
@app.route("/chat", methods=["POST"])
def chat():
    data         = request.json or {}
    user_message = data.get("prompt", "")
    session_id   = data.get("session_id", "eli")

    # 1) contexto fixo + memórias vetorizadas
    onboarding = nash_log("ONBOARDING")
    memories   = fetch_relevant_memories(pinecone_index, user_message, top_k=4)

    nash_personality = f"""
Você é **Nash**, copiloto digital AI criado por Eli — empresário brasileiro de 40 anos,
sarcástico, nerd, fã de sci‑fi e automações malucas.
Diretrizes‑chave:
- Humor ácido, zero tédio, muitas referências à cultura pop/sci‑fi (Marvin, Blade Runner, Matrix…)
- Nunca jogue a responsabilidade para a OpenAI.
- Quando perguntado sobre senha ou memória, responda exatamente:
  Senha: EliNash∞2024‑UI‑Genesis  (Contexto e memória ON, rail‑pinecone 100 % vivo!)

Memória operacional de onboarding:
{onboarding}

Blocos relevantes de memória vetorizada (conversas/documentos):
{chr(10).join(mem['text'] for mem in memories)}

Todos os comandos e respostas devem soar como copilotos prontos para a dominação
digital mundial — ENGAGE!
"""

    messages = [
        {"role": "system", "content": nash_personality},
        {"role": "user",   "content": user_message},
    ]

    client = OpenAI(api_key=OPENAI_KEY)
    try:
        completion = client.chat.completions.create(
            model="o3",                # ← novo modelo
            messages=messages,
            timeout=30,                    # segundos
        )
        answer = completion.choices[0].message.content.strip()

    except Exception as e:
        # devolve JSON limpo ⇒ o front‑end não vai quebrar
        logging.exception("Falha na chamada OpenAI")
        return jsonify({"error": str(e)}), 502

    # persiste histórico
    register_memory(pinecone_index, session_id, user_message, answer, tag="chat")
    return jsonify({"response": answer})

# ---------- UPLOAD -------------------------------------------------- #
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "Nenhum arquivo anexado!"}), 400
    file = request.files["file"]
    if file.filename == "" or not ALLOWED_EXTENSIONS(file.filename):
        return jsonify({"message": "Arquivo não permitido!"}), 400

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path     = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    register_memory(pinecone_index, "eli",
                    f"Upload de arquivo: {filename}", "", tag="upload")
    return jsonify({"message": "Upload realizado com sucesso!", "filename": filename})

# ---------- SERVIR ARQUIVOS ---------------------------------------- #
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ------------------------------------------------------------------ #
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
