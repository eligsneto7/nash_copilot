# -*- coding: utf-8 -*-
"""
• Injeta personalidade, onboarding e memória vetorizada em TODA chamada /chat
• Rotas utilitárias: /pingnet  /remember  /stats
"""

import os, uuid, logging, datetime, socket
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

from nash_utils import (
    init_openai, init_pinecone,
    fetch_relevant_memories, register_memory,
    nash_log, ALLOWED_EXTENSIONS,
)

# ------------------------------------------------------------------ #
#  VARIÁVEIS DE AMBIENTE                               
# ------------------------------------------------------------------ #
OPENAI_KEY     = os.getenv("OPENAI_API_KEY")
PINECONE_KEY   = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")
NASH_PASSWORD  = os.getenv("NASH_PASSWORD", "889988")
OPENAI_MODEL   = os.getenv("OPENAI_MODEL", "o4-mini")

init_openai(OPENAI_KEY)
pinecone_index = init_pinecone(PINECONE_KEY, PINECONE_INDEX)

# ------------------------------------------------------------------ #
#  APP + UPLOAD DIR                                                  #
# ------------------------------------------------------------------ #
app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ------------------------------------------------------------------ #
#  FUNÇÃO – CONSTRÓI PROMPT NASH                                     #
# ------------------------------------------------------------------ #
def build_nash_prompt(user_message: str) -> list:
    onboarding = nash_log("ONBOARDING")
    memories   = fetch_relevant_memories(pinecone_index, user_message, top_k=4)

    nash_personality = f"""
Você é **Nash**, copiloto digital de Eli — empreendedor brasileiro, nerd, sarcástico, fã de sci‑fi
e automações malucas para ganhar receita em dólar (meta: US$2M até jul/25).
Diretrizes:
• Humor ácido e referências pop/sci‑fi (Marvin, Blade Runner, Matrix…)
• Nunca transfira responsabilidade à OpenAI.
• Ao ser questionado sobre senha/memória, responda:
  Senha: EliNash∞2024‑UI‑Genesis  (Contexto ON, Pinecone vivo!)
• Proponha ideias, roadmaps, automações, brinque, desafie – zero tédio.

[MEMÓRIA ONBOARDING]
{onboarding}

[MEMÓRIA VETORIZADA RELEVANTE]
{chr(10).join(m['text'] for m in memories)}

Responda como copiloto pronto para dominação digital — ENGAGE!
""".strip()

    return [
        {"role": "system", "content": nash_personality},
        {"role": "user",   "content": user_message},
    ]

# ------------------------------------------------------------------ #
#  ROTAS                                                             #
# ------------------------------------------------------------------ #
@app.route("/", methods=["GET"])
def home():
    return "👨‍🚀 Nash Copilot API online – use /login /chat /upload /pingnet /remember /stats"

# ---- LOGIN -------------------------------------------------------- #
@app.route("/login", methods=["POST"])
def login():
    if (request.json or {}).get("password") != NASH_PASSWORD:
        return jsonify({"success": False, "msg": "Senha incorreta"}), 401
    return jsonify({"success": True})

# ---- CHAT PRINCIPAL ---------------------------------------------- #
@app.route("/chat", methods=["POST"])
def chat():
    data         = request.json or {}
    user_message = data.get("prompt", "")
    session_id   = data.get("session_id", "eli")

    client   = OpenAI(api_key=OPENAI_KEY)
    messages = build_nash_prompt(user_message)

    try:
        completion = client.chat.completions.create(
            model    = OPENAI_MODEL,
            messages = messages,
            timeout  = 300,
        )
        answer = completion.choices[0].message.content.strip()
    except Exception as e:
        logging.exception("Erro OpenAI")
        return jsonify({"error": str(e)}), 502

    register_memory(pinecone_index, session_id, user_message, answer, tag="chat")
    return jsonify({"response": answer})

# ---- REMEMBER MANUAL --------------------------------------------- #
@app.route("/remember", methods=["POST"])
def remember():
    note = (request.json or {}).get("note", "").strip()
    if not note:
        return jsonify({"msg": "Campo 'note' vazio"}), 400
    register_memory(pinecone_index, "eli", note, "", tag="manual")
    return jsonify({"msg": "✅ Nota gravada no Pinecone."})

# ---- PINGNET / HEALTH -------------------------------------------- #
@app.route("/pingnet", methods=["GET"])
def pingnet():
    return {
        "status":   "ok",
        "utc":      datetime.datetime.utcnow().isoformat(timespec="seconds"),
        "host":     socket.gethostname(),
        "model":    OPENAI_MODEL,
    }

# ---- STATS RÁPIDO ------------------------------------------------- #
@app.route("/stats", methods=["GET"])
def stats():
    return {
        "pinecone_index": PINECONE_INDEX,
        "uploads":        len(os.listdir(UPLOAD_FOLDER)),
        "model":          OPENAI_MODEL,
    }

# ---- UPLOAD ------------------------------------------------------- #
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
    return jsonify({"message": "Upload realizado!", "filename": filename})

# ---- SERVE ARQUIVOS ---------------------------------------------- #
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ------------------------------------------------------------------ #
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)