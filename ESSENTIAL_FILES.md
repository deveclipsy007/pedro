# Arquivos Essenciais do Projeto Pedro

## 📁 Estrutura de Arquivos Essenciais para Produção

### Código Principal
- `playground/pedro_playground_medico.py` - Playground principal com interface médica
- `pedro_enhanced_search.py` - Sistema de busca semântica aprimorada
- `pubmed_integration.py` - Integração com a API do PubMed

### Banco de Dados
- `data/enhanced_rag.db` - Banco de dados SQLite com 915 chunks semânticos
- `data/raw/` - Pasta com 26 protocolos clínicos da Pedlife em formato .md

### Configuração e Dependências
- `requirements.txt` - Dependências do projeto
- `render.yaml` - Configuração para deploy no Render
- `.env.render.template` - Template de variáveis de ambiente

### Documentação
- `README.md` - Visão geral do projeto
- `DEPLOYMENT.md` - Instruções detalhadas de deploy
- `DEPLOYMENT_CHECKLIST.md` - Checklist para deploy
- `GIT_COMMIT_CHECKLIST.md` - Checklist para commit no GitHub

## 📁 Pastas Essenciais

### Pasta `data/`
Contém o banco de dados RAG e os protocolos clínicos:
- `enhanced_rag.db` - Banco com 915 chunks semânticos
- `raw/` - 26 protocolos Pedlife (.md)

### Pasta `playground/`
Contém o código do playground médico:
- `pedro_playground_medico.py` - Arquivo principal do playground

## 🚫 Arquivos e Pastas que Podem ser Removidos

### Arquivos de Teste e Desenvolvimento
- `test_*.py` - Arquivos de teste
- `teste_*.py` - Scripts de teste
- `bateria_testes_pedro.py` - Bateria de testes completa
- `*.md` de documentação técnica detalhada (exceto README.md e DEPLOYMENT.md)

### Pastas de Desenvolvimento
- `.venv/` - Ambiente virtual
- `venv/` - Ambiente virtual
- `__pycache__/` - Cache do Python
- `.pytest_cache/` - Cache de testes
- `tests/` - Pasta de testes
- `agents/` - Pasta com versões antigas dos agentes
- `src/` - Pasta com código fonte antigo
- `scripts/` - Pasta com scripts de desenvolvimento
- `config/` - Pasta com configurações antigas
- `examples/` - Pasta com exemplos
- `docs/` - Pasta com documentação detalhada
- `web/` - Pasta com interface web antiga
- `docker/` - Pasta com configuração Docker
- `kestra/` - Pasta com workflows

### Arquivos de Configuração Local
- `.env` - Arquivo de ambiente local
- `.env.test` - Arquivo de ambiente de teste
- `.env.prod` - Arquivo de ambiente de produção
- `.env.*.template` - Templates (exceto .env.render.template)

### Scripts de Desenvolvimento
- `activate_enhanced_rag.py` - Script de ativação
- `fix_*.py` - Scripts de correção
- `migrate_*.py` - Scripts de migração
- `process_*.py` - Scripts de processamento
- `verificar_*.py` - Scripts de verificação
- `cleanup_projeto_pedro.py` - Script de limpeza
- `integrar_calculadora_pedro.py` - Script de integração

## ✅ Arquivos Essenciais para Manter

1. **Código Principal**:
   - `playground/pedro_playground_medico.py`
   - `pedro_enhanced_search.py`
   - `pubmed_integration.py`

2. **Dados**:
   - `data/enhanced_rag.db`
   - `data/raw/*.md` (todos os 26 protocolos)

3. **Configuração**:
   - `requirements.txt`
   - `render.yaml`
   - `.env.render.template`

4. **Documentação**:
   - `README.md`
   - `DEPLOYMENT.md`
   - `DEPLOYMENT_CHECKLIST.md`
   - `GIT_COMMIT_CHECKLIST.md`

## 📋 Próximos Passos

1. Remover arquivos e pastas não essenciais listados acima
2. Manter apenas os arquivos essenciais identificados
3. Verificar integridade do projeto após limpeza
4. Testar funcionalidades principais

Esta lista garante que o projeto mantenha apenas os componentes necessários para:
- Executar o agente Pedro com todas as funcionalidades
- Deploy no Render
- Integração com frontend React
- Acesso aos protocolos clínicos da Pedlife
- Busca semântica e integração PubMed
