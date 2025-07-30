# Checklist Final de Arquivos para Commit no GitHub

## 📁 Arquivos Essenciais para Deploy no Railway

### Código e Configuração
- [ ] `playground/pedro_playground_medico.py` (Playground principal médico)
- [ ] `pedro_enhanced_search.py` (Busca semântica aprimorada)
- [ ] `pubmed_integration.py` (Integração com PubMed)
- [ ] `requirements.txt` (Dependências do projeto)
- [ ] `railway.toml` (Configuração do Railway)
- [ ] `Procfile` (Comando de inicialização)
- [ ] `.env.railway.template` (Template de variáveis de ambiente)

### Banco de Dados e Dados
- [ ] `data/enhanced_rag.db` (Banco RAG com 915 chunks semânticos)
- [ ] `data/raw/` (26 protocolos Pedlife em formato .md)

### Documentação
- [ ] `README.md` (Visão geral do projeto)
- [ ] `DEPLOYMENT.md` (Instruções detalhadas de deploy)
- [ ] `DEPLOYMENT_CHECKLIST.md` (Checklist de deploy)
- [ ] `GIT_COMMIT_CHECKLIST.md` (Este arquivo)

## 🚫 Arquivos que NÃO devem ser commitados

### Ambientes e Caches
- [ ] `.env` (Arquivo de ambiente com segredos)
- [ ] `.env.test` (Arquivo de ambiente de teste)
- [ ] `.env.prod` (Arquivo de ambiente de produção)
- [ ] `.venv/` (Ambiente virtual)
- [ ] `venv/` (Ambiente virtual)
- [ ] `__pycache__/` (Cache do Python)
- [ ] `*.pyc` (Arquivos compilados do Python)

### Logs e Dados Temporários
- [ ] `logs/` (Diretório de logs)
- [ ] `*.log` (Arquivos de log)
- [ ] `*.tmp` (Arquivos temporários)
- [ ] `*.bak` (Arquivos de backup)

### Arquivos de Configuração Local
- [ ] `.vscode/` (Configurações do VS Code)
- [ ] `.idea/` (Configurações do IntelliJ IDEA)
- [ ] `.DS_Store` (Arquivos do macOS)
- [ ] `Thumbs.db` (Arquivos do Windows)

## ✅ Validações Antes do Commit

### Estrutura do Projeto
- [ ] Verificar que todos os arquivos essenciais estão presentes
- [ ] Confirmar que o banco `enhanced_rag.db` está atualizado
- [ ] Validar que os 26 protocolos Pedlife estão em `data/raw/`

### Código e Funcionalidades
- [ ] Testar o playground localmente antes do commit
- [ ] Validar que todas as 5 ferramentas estão funcionando
- [ ] Confirmar detecção automática de cálculo de dose
- [ ] Verificar integração RAG + PubMed

### Configuração
- [ ] Revisar `railway.toml` para garantir comandos corretos
- [ ] Verificar `.env.railway.template` para variáveis essenciais
- [ ] Confirmar que `requirements.txt` está atualizado

### Documentação
- [ ] Revisar `README.md` para informações atualizadas
- [ ] Validar instruções em `DEPLOYMENT.md`
- [ ] Confirmar checklist em `DEPLOYMENT_CHECKLIST.md`

## 📝 Comandos Git Recomendados

```bash
# Adicionar arquivos específicos (recomendado)
git add playground/pedro_playground_medico.py
git add pedro_enhanced_search.py
git add pubmed_integration.py
git add requirements.txt
git add railway.toml
git add Procfile
git add .env.railway.template
git add data/enhanced_rag.db
git add data/raw/
git add README.md
git add DEPLOYMENT.md
git add DEPLOYMENT_CHECKLIST.md

git commit -m "Deploy version: Agente Pedro com RAG semântico e integração PubMed"
git push origin main
```

## ⚠️ Avisos Importantes

1. **Nunca commite segredos**: Arquivos `.env` com API keys não devem ser commitados
2. **Verifique o tamanho do repositório**: O banco `enhanced_rag.db` é grande, mas necessário
3. **Teste localmente primeiro**: Sempre valide o funcionamento antes do commit
4. **Mantenha documentação atualizada**: Qualquer mudança deve refletir na documentação

---

📝 **Dica**: Use `git status` para verificar quais arquivos serão commitados antes de fazer o commit final.
