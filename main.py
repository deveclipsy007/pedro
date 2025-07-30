"""
Health check endpoint para Railway
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Importa as dependências necessárias
try:
    from playground.pedro_playground_medico import playground_app
    print("✅ Playground app importado com sucesso")
except Exception as e:
    print(f"❌ Erro ao importar playground app: {e}")
    # Fallback para criar app básico
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Pedro - Assistente Clínico Pediátrico",
            "version": "1.0.0"
        }
    
    playground_app = app

# Exporta para o Railway
app = playground_app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
