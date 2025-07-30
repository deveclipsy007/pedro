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
    agent_error = None
    
    def get_pedro_agent():
        global pedro_agent, agent_error
        
        if pedro_agent is None and agent_error is None:
            try:
                # Verificar variáveis de ambiente críticas
                if not os.environ.get("OPENAI_API_KEY"):
                    raise ValueError("OPENAI_API_KEY não configurada")
                
                # Verificar banco de dados
                if not os.path.exists("data/enhanced_rag.db"):
                    raise FileNotFoundError("Banco RAG não encontrado: data/enhanced_rag.db")
                
                # Criar agente com configuração defensiva
                pedro_agent = create_pedro_agent()
                print("✅ Agente Pedro inicializado com sucesso")
                
            except Exception as e:
                agent_error = f"Erro ao inicializar Pedro: {str(e)}"
                print(f"❌ {agent_error}")
                
        if pedro_agent is None:
            raise Exception(agent_error or "Agente não inicializado")
            
        return pedro_agent
    
    @app.get("/")
    @app.get("/health")
    def health_check():
        """Health check resiliente - não depende do agente Pedro"""
        try:
            # Verificação básica sem inicializar o agente
            return {
                "status": "healthy",
                "service": "Pedro - Assistente Clínico Pediátrico",
                "version": "1.0.0",
                "timestamp": str(os.environ.get('RAILWAY_DEPLOYMENT_ID', 'local')),
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
        except Exception as e:
            # Health check nunca deve falhar
            return {
                "status": "degraded",
                "service": "Pedro - Assistente Clínico Pediátrico", 
                "version": "1.0.0",
                "error": str(e)
            }
    
    @app.get("/health/detailed")
    def detailed_health_check():
        """Health check detalhado - inclui validação do agente"""
        try:
            # Tenta inicializar o agente para verificação completa
            agent = get_pedro_agent()
            
            return {
                "status": "healthy",
                "service": "Pedro - Assistente Clínico Pediátrico",
                "version": "1.0.0",
                "agent_status": "ready",
                "capabilities": [
                    "Busca em protocolos Pedlife",
                    "Cálculo de doses pediátricas", 
                    "Cenários clínicos",
                    "Alertas de segurança",
                    "Pesquisa PubMed"
                ],
                "database_status": "connected" if os.path.exists("data/enhanced_rag.db") else "missing"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Pedro - Assistente Clínico Pediátrico",
                "version": "1.0.0", 
                "agent_status": "error",
                "error": str(e),
                "suggestion": "Verifique OPENAI_API_KEY e dependências"
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
            # Validar entrada
            if not request.message or not request.message.strip():
                raise HTTPException(
                    status_code=422,
                    detail="Mensagem não pode estar vazia"
                )
            
            # Obter agente Pedro
            agent = get_pedro_agent()
            
            # Executar consulta
            response = agent.run(request.message.strip())
            
            return ChatResponse(
                response=response.content,
                session_id=request.session_id,
                status="success"
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
            
        except ValueError as e:
            # Erro de configuração (ex: OPENAI_API_KEY)
            raise HTTPException(
                status_code=503,
                detail=f"Serviço mal configurado: {str(e)}"
            )
            
        except FileNotFoundError as e:
            # Banco de dados ausente
            raise HTTPException(
                status_code=503,
                detail=f"Recurso não encontrado: {str(e)}"
            )
            
        except Exception as e:
            # Outros erros
            print(f"❌ Erro no chat: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno do servidor: {str(e)}"
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
    print(f"❌ Erro crítico ao importar módulos Pedro: {e}")
    print(f"❌ Tipo do erro: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    
    # Fallback para app básico de diagnóstico
    from fastapi import FastAPI, HTTPException
    
    app = FastAPI(
        title="Pedro - Modo Diagnóstico",
        description="Modo de diagnóstico - verifique configurações"
    )
    
    @app.get("/")
    @app.get("/health")
    def health_check_fallback():
        return {
            "status": "error",
            "service": "Pedro - Assistente Clínico Pediátrico",
            "version": "1.0.0",
            "mode": "diagnostic",
            "error": str(e),
            "error_type": type(e).__name__,
            "suggestions": [
                "Verifique se OPENAI_API_KEY está configurada",
                "Confirme se data/enhanced_rag.db existe",
                "Verifique se todas as dependências estão instaladas",
                "Consulte logs detalhados do Railway"
            ]
        }
    
    @app.get("/debug")
    def debug_info():
        return {
            "environment_vars": {
                "OPENAI_API_KEY": "SET" if os.environ.get("OPENAI_API_KEY") else "NOT_SET",
                "PORT": os.environ.get("PORT", "NOT_SET"),
                "RAILWAY_ENVIRONMENT": os.environ.get("RAILWAY_ENVIRONMENT", "NOT_SET"),
                "RAILWAY_DEPLOYMENT_ID": os.environ.get("RAILWAY_DEPLOYMENT_ID", "NOT_SET")
            },
            "files_check": {
                "data/enhanced_rag.db": os.path.exists("data/enhanced_rag.db"),
                "playground/pedro_playground_medico.py": os.path.exists("playground/pedro_playground_medico.py"),
                "pedro_enhanced_search.py": os.path.exists("pedro_enhanced_search.py"),
                "pubmed_integration.py": os.path.exists("pubmed_integration.py")
            },
            "python_path": sys.path,
            "working_directory": str(Path.cwd()),
            "import_error": str(e)
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
            detail={
                "error": "Serviço indisponível",
                "reason": str(e),
                "solution": "Configure OPENAI_API_KEY no Railway Dashboard",
                "debug_endpoint": "/debug"
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
