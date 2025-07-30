#!/usr/bin/env python3
"""
Script de verificação do Pedro para Railway
Automatiza a verificação e preparação para deploy no Railway
"""

import os
import sys
from pathlib import Path
import sqlite3

def check_file_exists(file_path, description):
    """Verifica se um arquivo existe e reporta o status"""
    if file_path.exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - AUSENTE")
        return False

def check_database_integrity():
    """Verifica a integridade do banco RAG"""
    db_path = Path("data/enhanced_rag.db")
    
    if not db_path.exists():
        print("❌ Banco RAG não encontrado!")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verifica se existem chunks (tabela semantic_chunks)
        cursor.execute("SELECT COUNT(*) FROM semantic_chunks")
        chunk_count = cursor.fetchone()[0]
        
        # Verifica se existem documentos
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"✅ Banco RAG OK: {doc_count} documentos, {chunk_count} chunks semânticos")
        return chunk_count > 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco RAG: {e}")
        return False

def check_environment_variables():
    """Verifica variáveis de ambiente necessárias"""
    required_vars = {
        "OPENAI_API_KEY": "Chave OpenAI (OBRIGATÓRIA)",
        "PUBMED_API_KEY": "Chave PubMed (OPCIONAL)"
    }
    
    print("\n🔐 Variáveis de Ambiente:")
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {var}: {masked} - {description}")
        else:
            status = "❌" if var == "OPENAI_API_KEY" else "⚠️"
            print(f"{status} {var}: NÃO CONFIGURADA - {description}")

def verify_requirements():
    """Verifica se requirements.txt está presente e válido"""
    req_path = Path("requirements.txt")
    
    if not check_file_exists(req_path, "Requirements"):
        return False
    
    try:
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        required_packages = ['agno', 'fastapi', 'uvicorn', 'openai', 'langchain']
        missing_packages = []
        
        for package in required_packages:
            if package not in content.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ Pacotes possivelmente ausentes: {missing_packages}")
        else:
            print("✅ Requirements.txt parece completo")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar requirements: {e}")
        return False

def create_railway_checklist():
    """Cria checklist específico para Railway"""
    checklist = """
# 📋 CHECKLIST DE DEPLOY PEDRO NO RAILWAY

## ✅ Arquivos Necessários
- [ ] data/enhanced_rag.db (banco RAG com chunks)
- [ ] requirements.txt (dependências Python)
- [ ] railway.toml (configuração Railway)
- [ ] Procfile (comando de inicialização)
- [ ] .env.railway.template (template de variáveis)

## 🔧 Configuração Railway
- [ ] Projeto criado no Railway
- [ ] Repositório GitHub conectado
- [ ] OPENAI_API_KEY configurada (obrigatória)
- [ ] PUBMED_API_KEY configurada (opcional)
- [ ] PORT definida (recomendado: 8000)

## 🚀 Deploy
- [ ] Build executado com sucesso
- [ ] Start command funcionando
- [ ] Health check respondendo
- [ ] URL pública acessível
- [ ] Interface Pedro carregando

## 🧪 Testes
- [ ] Consulta médica de teste
- [ ] Resposta baseada em RAG
- [ ] PubMed funcionando (se configurado)
- [ ] Logs sem erros críticos

## 🆘 Em caso de erro:
1. Verificar logs no Railway Dashboard
2. Confirmar variáveis de ambiente
3. Testar localmente
4. Verificar integridade do banco RAG
"""
    
    with open("RAILWAY_CHECKLIST.md", 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Checklist criado: RAILWAY_CHECKLIST.md")

def main():
    """Função principal de verificação"""
    print("🚀 PEDRO - VERIFICAÇÃO PARA RAILWAY")
    print("=" * 50)
    
    # Verifica diretório correto
    if not Path("pedro_enhanced_search.py").exists():
        print("❌ Execute este script na raiz do projeto Pedro!")
        sys.exit(1)
    
    print("📁 Verificando arquivos essenciais...")
    
    # Arquivos essenciais
    essential_files = [
        (Path("requirements.txt"), "Requirements Python"),
        (Path("data/enhanced_rag.db"), "Banco RAG"),
        (Path("playground/pedro_playground_medico.py"), "Playground médico"),
        (Path("pedro_enhanced_search.py"), "Sistema de busca"),
    ]
    
    all_files_ok = True
    for file_path, description in essential_files:
        if not check_file_exists(file_path, description):
            all_files_ok = False
    
    # Novos arquivos Railway
    print("\n📁 Verificando arquivos Railway...")
    railway_files = [
        (Path("railway.toml"), "Configuração Railway"),
        (Path("Procfile"), "Comando de inicialização"),
        (Path(".env.railway.template"), "Template de variáveis"),
    ]
    
    for file_path, description in railway_files:
        check_file_exists(file_path, description)
    
    # Verifica banco de dados
    print("\n🗄️ Verificando banco de dados...")
    db_ok = check_database_integrity()
    
    # Verifica requirements
    print("\n📦 Verificando dependências...")
    req_ok = verify_requirements()
    
    # Verifica variáveis de ambiente
    check_environment_variables()
    
    # Cria checklist
    print("\n📋 Criando checklist...")
    create_railway_checklist()
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📊 RESUMO DA VERIFICAÇÃO:")
    
    if all_files_ok:
        print("✅ Arquivos essenciais presentes")
    else:
        print("❌ Alguns arquivos essenciais ausentes")
    
    if db_ok:
        print("✅ Banco RAG íntegro")
    else:
        print("❌ Problemas no banco RAG")
    
    if req_ok:
        print("✅ Requirements OK")
    else:
        print("❌ Problemas nos requirements")
    
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print("✅ OPENAI_API_KEY presente")
    else:
        print("⚠️ OPENAI_API_KEY não configurada (configure no Railway)")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Configure OPENAI_API_KEY no Railway Dashboard")
    print("2. Faça push dos novos arquivos para GitHub")
    print("3. Conecte repositório no Railway")
    print("4. Configure variáveis de ambiente")
    print("5. Monitore logs do deploy")
    print("6. Teste a aplicação na URL fornecida")
    
    print("\n📚 Consulte: RAILWAY_DEPLOYMENT.md para guia completo")
    print("📋 Use: RAILWAY_CHECKLIST.md para acompanhar progresso")

if __name__ == "__main__":
    main()
