
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
