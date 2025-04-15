# Nash Copilot — README MVP
## O que É:
Agente Nash, copiloto sci-fi para Eli. GPT-4.1 + Pinecone (memória vetorial), frontend Streamlit ultra-futurista. Onboarding e personalidade gravadas para evolução constante.

## Deploy Rápido (RAILWAY)
1. Faça fork/clone do projeto para o seu GitHub.
2. No Railway, crie um novo projeto, importe do seu repositório, ou “Deploy from GitHub”.
3. No painel do Railway do projeto:
   - Configure as Variáveis de Ambiente:  
      - `OPENAI_API_KEY`: Sua chave OpenAI (com acesso GPT4)
      - `PINECONE_API_KEY`: Chave Pinecone
      - `PINECONE_INDEX_NAME`: Nome do index do Pinecone
      - `NASH_PASSWORD`: 889988
   - Defina o comando de execução para backend: `python nash_app.py` ou use `gunicorn nash_app:app`
   - Certifique que tem um diretório /uploads na raiz para arquivos.

4. Rode o backend. O endpoint estará ativo de acordo com sua URL Railway.
5. No seu computador (ou outro Railway), rode o `nash_ui.py` (o Streamlit conecta ao backend via HTTP).
   - Troque as URLs no código para o endpoint do Railway.

## Dicas
- Se quiser CI/CD automático, mantenha o GitHub integrado ao Railway.
- Customize o Markdown inicial, easter-eggs e system prompts como quiser!