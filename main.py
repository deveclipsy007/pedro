"""
API REST para o Agente Pedro - Railway Deploy
"""
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Modelos Pydantic para API
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    agent: str = "Pedro"
    status: str = "success"
    session_id: Optional[str] = None

# Importa as dependências necessárias
try:
    from playground.pedro_playground_medico import create_pedro_agent
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    print("✅ Módulos Pedro importados com sucesso")
    
    # Cria a aplicação FastAPI
    app = FastAPI(
        title="Pedro - Assistente Clínico Pediátrico",
        description="API REST para consultas médicas pediátricas",
        version="1.0.0"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Inicializar agente Pedro
    pedro_agent = None
    
    def get_pedro_agent():
        global pedro_agent
        if pedro_agent is None:
            pedro_agent = create_pedro_agent()
            print("✅ Agente Pedro inicializado")
        return pedro_agent
    
    @app.get("/")
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Pedro - Assistente Clínico Pediátrico",
            "version": "1.0.0",
            "endpoints": [
                "/chat",
                "/api/chat", 
                "/v1/chat",
                "/message",
                "/pedro",
                "/ask",
                "/query"
            ]
        }
    
    @app.post("/chat", response_model=ChatResponse)
    @app.post("/api/chat", response_model=ChatResponse)
    @app.post("/v1/chat", response_model=ChatResponse)
    @app.post("/message", response_model=ChatResponse)
    @app.post("/pedro", response_model=ChatResponse)
    @app.post("/ask", response_model=ChatResponse)
    @app.post("/query", response_model=ChatResponse)
    async def chat_endpoint(request: ChatRequest):
        try:
            # Obter agente Pedro
            agent = get_pedro_agent()
            
            # Executar consulta
            response = agent.run(request.message)
            
            return ChatResponse(
                response=response.content,
                session_id=request.session_id,
                status="success"
            )
            
        except Exception as e:
            print(f"❌ Erro no chat: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno: {str(e)}"
            )
    
    @app.get("/agents/pedro/info")
    def agent_info():
        return {
            "name": "Pedro",
            "role": "Assistente Clínico Pediátrico",
            "capabilities": [
                "Busca em protocolos Pedlife",
                "Cálculo de doses pediátricas",
                "Cenários clínicos",
                "Alertas de segurança",
                "Pesquisa PubMed"
            ],
            "protocols": 26,
            "chunks": 915
        }

except Exception as e:
    print(f"❌ Erro ao importar módulos Pedro: {e}")
    # Fallback para app básico
    from fastapi import FastAPI, HTTPException
    
    app = FastAPI(title="Pedro - Status")
    
    @app.get("/")
    @app.get("/health")
    def health_check():
        return {
            "status": "error",
            "service": "Pedro - Assistente Clínico Pediátrico",
            "version": "1.0.0",
            "error": str(e)
        }
    
    @app.post("/chat")
    @app.post("/api/chat")
    @app.post("/v1/chat") 
    @app.post("/message")
    @app.post("/pedro")
    @app.post("/ask")
    @app.post("/query")
    async def chat_fallback():
        raise HTTPException(
            status_code=503,
            detail="Serviço temporariamente indisponível"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
