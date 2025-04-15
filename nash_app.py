# nash_app.py
from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from nash_utils import (
    init_openai, init_pinecone, 
    create_embedding, 
    fetch_relevant_memories, 
    register_memory, 
    nash_log, 
    ALLOWED_EXTENSIONS
)

app = Flask(__name__)

# --- CONFIGURAÇÃO SECRETA ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")
NASH_PASSWORD = os.getenv("NASH_PASSWORD", "889988")  # Default para MVP

init_openai(OPENAI_KEY)
pinecone_index = init_pinecone(PINECONE_KEY, PINECONE_INDEX)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ROTA PRINCIPAL / SAUDAÇÃO (prevenção de 404) ---
@app.route("/", methods=["GET"])
def home():
    return "👨‍🚀 Nash Copilot API online! Use endpoints /login, /chat, /upload."

# --- LOGIN SIMPLES ---
@app.route("/login", methods=['POST'])
def login():
    dados = request.json
    if not dados or dados.get('password') != NASH_PASSWORD:
        return jsonify({"success": False, "msg": "Senha incorreta"}), 401
    return jsonify({"success": True})

# --- ENDPOINT PRINCIPAL DE CHAT ---
@app.route("/chat", methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("prompt", "")
    session_id = data.get("session_id", "eli")  # Único usuário

    # 1. Recuperar contexto relevante das memórias vetorizadas
    memories = fetch_relevant_memories(pinecone_index, user_message, top_k=4)
    context_init = nash_log("ONBOARDING")  # Lore inicial sempre injetada

    # 2. Montar prompt inteligente
    prompt = (
        context_init +
        "\n\n--- Conversa relevante do passado ---\n" +
        "\n".join([item["text"] for item in memories]) +
        "\n\n--- Novo comando do Eli ---\n" +
        user_message
    )

    # 3. Consultar o modelo GPT-4.1
    response = create_embedding(prompt, model="gpt-4-1106-preview")
    answer = response  # (Simplificando, adapte se usar função de resposta/direta do OpenAI)

    # 4. Logar toda interação e embeddar no Pinecone
    register_memory(pinecone_index, session_id, user_message, answer, tag="chat")

    return jsonify({"response": answer})

# --- UPLOAD DE ARQUIVOS ---
@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"message": "Nenhum arquivo anexado!"}), 400
    file = request.files["file"]
    if file.filename == "" or not ALLOWED_EXTENSIONS(file.filename):
        return jsonify({"message": "Arquivo não permitido!"}), 400
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    # Logar metadados no Pinecone
    register_memory(pinecone_index, "eli", f"Upload de arquivo: {filename}", "", tag="upload")
    return jsonify({"message": "Upload realizado com sucesso!", "filename": filename})

# --- SERVIR ARQUIVOS ENVIADOS ---
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))