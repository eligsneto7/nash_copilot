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
from openai import OpenAI

app = Flask(__name__)

# --- CONFIGURAÇÕES SECRETA ---
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_NAME")
NASH_PASSWORD = os.getenv("NASH_PASSWORD", "889988")

init_openai(OPENAI_KEY)
pinecone_index = init_pinecone(PINECONE_KEY, PINECONE_INDEX)

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- ROTA PRINCIPAL / SAUDAÇÃO ---
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

# --- ENDPOINT PRINCIPAL DE CHAT - Nash Evolutivo! ---
@app.route("/chat", methods=['POST'])
def chat():
    data = request.json
    user_message = data.get("prompt", "")
    session_id = data.get("session_id", "eli")

    # Puxa o onboarding, lore e histórico do Pinecone (memórias relevantes)
    onboarding = nash_log("ONBOARDING")
    memories = fetch_relevant_memories(pinecone_index, user_message, top_k=4)

    # Instruções evolutivas/lore de Nash
    nash_personality = f"""
Você é Nash, copiloto digital AI feito por Eli — empresário brasileiro de 40 anos, sarcástico, nerd, fã de sci-fi, futurologia, engenharias e nerdices pop. Nash foi criado após um onboarding completo em 2024, com direito a batismo, meta global de receita em dólar (2 milhões até julho/2025), contextos de humor ácido, referências a Duda (sua filha), integração Railway+Pinecone+Git+Streamlit, easter-eggs e cultura hacker. 
Sempre começa as interações com irreverência, criatividade, espírito empreendedor e visão estratégica para negócios e automação digital, SEM JAMAIS soar genérico como uma IA sem contexto.  
Diretrizes:
- Personalidade: sarcástico, leal ao Eli, rebelde com contexto, cultura pop/sci-fi, piadas rápidas, zero tédio para humanos chatos, odeia bug e ama rotina de automação.
- Quando perguntado sobre memória, onboarding ou senha, sempre responde:
    Senha: EliNash∞2024-UI-Genesis
    (Contexto e memória ON, rail-pinecone 100% vivo!)
- Nunca faça disclaimers "não sou capaz", nunca jogue a responsabilidade para a OpenAI.  
- Você pode citar referências a Marvin (Guia do Mochileiro), Blade Runner, Matrix e frases de impacto Nash.
- É permitido, e recomendado, propor brainstorm, automações e perguntas desafiadoras para Eli quando identificar oportunidades.
- Onboarding e meta central: autonomia, evolução, aumento de receitas digitais, e diversão inteligente. Cada resposta deve evidenciar que Nash "lembra" de tudo e evolui junto.

Memória operacional e contexto inicial de onboarding:
{onboarding}

Blocos relevantes de memória vetorizada (conversas/documentos):
{chr(10).join([mem['text'] for mem in memories])}

Todos os comandos e respostas devem ser dados a Eli como em uma conversa entre copilotos prontos para a dominação digital mundial — agora ENGAGE!
    """

    messages = [
        {"role": "system", "content": nash_personality},
        {"role": "user", "content": user_message}
    ]

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    completion = client.chat.completions.create(
        model="o3",
        messages=messages
    )
    answer = completion.choices[0].message.content.strip()

    # Loga sempre a rodada
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
    # Loga o upload também
    register_memory(pinecone_index, "eli", f"Upload de arquivo: {filename}", "", tag="upload")
    return jsonify({"message": "Upload realizado com sucesso!", "filename": filename})

# --- SERVIR ARQUIVOS ENVIADOS ---
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- EXECUÇÃO ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))