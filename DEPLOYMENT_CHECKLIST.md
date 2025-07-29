# Checklist de Deploy do Agente Pedro no Render

## 📁 Estrutura de Arquivos Essenciais

### Código Fonte
- [ ] `playground/pedro_playground_medico.py` (Playground principal)
- [ ] `pedro_enhanced_search.py` (Busca semântica)
- [ ] `pubmed_integration.py` (Integração PubMed)
- [ ] ` requirements.txt` (Dependências)

### Banco de Dados
- [ ] `data/enhanced_rag.db` (Banco RAG com 915 chunks)

### Configuração
- [ ] `render.yaml` (Configuração do Render)
- [ ] `.env.render.template` (Template de variáveis de ambiente)

### Documentação
- [ ] `README.md` (Instruções gerais)
- [ ] `DEPLOYMENT.md` (Instruções específicas de deploy)

## ⚙️ Configurações Necessárias no Render

### Variáveis de Ambiente
- [ ] `OPENAI_API_KEY` (API Key da OpenAI)
- [ ] `PUBMED_API_KEY` (API Key do PubMed - opcional)

### Build Settings
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `uvicorn playground.pedro_playground_medico:playground_app --host 0.0.0.0 --port $PORT`

### Deploy Settings
- [ ] Auto Deploy: Ativado (para deploys automáticos em push)
- [ ] Health Check Path: `/` ou `/health` (se implementado)

## ✅ Validações Pós-Deploy

### Funcionalidades do Agente
- [ ] Playground acessível via URL do Render
- [ ] Agente Pedro aparece no playground
- [ ] Todas as 5 ferramentas estão disponíveis:
  - [ ] `retrieve_docs` (Busca nos protocolos Pedlife)
  - [ ] `calc_dose` (Cálculo de dose pediátrica)
  - [ ] `test_medical_scenarios` (Cenários clínicos)
  - [ ] `clinical_alert` (Alertas de segurança)
  - [ ] `pubmed_search` (Busca científica)

### Integrações
- [ ] RAG Semântico funcionando (busca em `enhanced_rag.db`)
- [ ] Cálculo de dose automático para queries com peso/medicação
- [ ] Fallback PubMed quando RAG insuficiente
- [ ] Citação correta de fontes (Pedlife + PubMed)

### Performance e Segurança
- [ ] Respostas clínicas específicas (não genéricas)
- [ ] Tempo de resposta aceitável (< 5 segundos)
- [ ] Logging de buscas e decisões clínicas
- [ ] Validadores de segurança e guardrails ativos

## 🚀 Próximos Passos Após Deploy

1. Testar queries clínicas reais no playground
2. Validar cálculos de dose com diferentes medicações
3. Verificar fallback PubMed com queries complexas
4. Monitorar logs do Render para erros
5. Configurar alertas de saúde do serviço

---

📝 **Importante**: Nunca subir arquivos `.env` com segredos para o repositório. Usar sempre `.env.render.template` como referência.
