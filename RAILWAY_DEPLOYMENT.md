# 🚀 Deploy do Pedro no Railway

Este guia documenta como fazer deploy do agente Pedro no Railway.

## 📋 Pré-requisitos

- Conta no Railway (https://railway.app)
- Repositório Pedro no GitHub
- Chave da API OpenAI (obrigatória)
- Chave da API PubMed (opcional)

## 🔧 Configuração do Projeto

### 1. Conectar Repositório
1. Acesse o Railway Dashboard
2. Clique em "New Project"
3. Selecione "Deploy from GitHub repo"
4. Conecte o repositório do Pedro

### 2. Configurar Variáveis de Ambiente

No Railway Dashboard, vá em **Settings > Variables** e configure:

#### ✅ Variáveis Obrigatórias:
```
OPENAI_API_KEY=sua_chave_openai_aqui
```

#### 🔧 Variáveis de Configuração (já definidas no railway.toml):
```
PORT=8000
DEBUG=false
DATABASE_URL=sqlite:///data/enhanced_rag.db
RAG_DATABASE_PATH=data/enhanced_rag.db
AGENT_NAME=Pedro
AGENT_ROLE=Assistente Clínico Pediátrico
```

#### 📚 Variáveis Opcionais:
```
PUBMED_API_KEY=sua_chave_pubmed_aqui  # Apenas se usar integração PubMed
```

### 3. Configuração de Deploy

O Railway irá automaticamente:
- Detectar o `requirements.txt` e instalar dependências
- Usar o comando do `Procfile` para inicializar a aplicação
- Aplicar configurações do `railway.toml`

#### Comandos Utilizados:
- **Build**: `pip install -r requirements.txt`
- **Start**: `uvicorn playground.pedro_playground_medico:playground_app --host 0.0.0.0 --port $PORT`

## 📁 Arquivos de Configuração

### railway.toml
Configuração principal do Railway com variáveis de ambiente padrão.

### Procfile
Define o comando de inicialização da aplicação.

### .env.railway.template
Template com todas as variáveis necessárias (apenas para referência - NÃO commitar com valores reais).

## 🔍 Verificações Importantes

### ✅ Checklist de Deploy

- [ ] Arquivo `data/enhanced_rag.db` está no repositório
- [ ] `requirements.txt` está atualizado
- [ ] Variável `OPENAI_API_KEY` configurada no Railway
- [ ] Variável `PORT` definida (padrão: 8000)
- [ ] Aplicação responde na URL fornecida pelo Railway

### 🔧 Estrutura de Arquivos Necessários

```
pedro/
├── data/
│   └── enhanced_rag.db          # Base de dados RAG (915 chunks)
├── playground/
│   └── pedro_playground_medico.py
├── requirements.txt
├── railway.toml                 # Configuração Railway
├── Procfile                     # Comando de inicialização
└── .env.railway.template        # Template de variáveis
```

## 🚨 Segurança

- **NUNCA** commite chaves API no repositório
- Use o painel do Railway para configurar variáveis sensíveis
- O arquivo `.env.railway.template` é apenas referência

##  Troubleshooting

### Logs
Acesse **Deployments > [Latest] > Logs** no Railway Dashboard.

### Problemas Comuns

1. **Erro de chave API ausente**
   - Verifique se `OPENAI_API_KEY` está configurada
   - Confirme se a chave está válida

2. **Banco de dados não encontrado**
   - Confirme se `data/enhanced_rag.db` está no repositório
   - Verifique se o path `RAG_DATABASE_PATH=data/enhanced_rag.db` está correto

3. **Aplicação não responde**
   - Verifique se a porta configurada coincide com `$PORT`
   - Confirme se o host está como `0.0.0.0`

### Testando Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar variáveis (copiar de .env.railway.template)
cp .env.railway.template .env
# Editar .env com suas chaves

# 3. Executar aplicação
uvicorn playground.pedro_playground_medico:playground_app --host 0.0.0.0 --port 8000
```

## 📈 Performance

### Recursos Recomendados
- **CPU**: 1-2 vCPUs (mínimo)
- **RAM**: 1-2 GB (mínimo)
- **Storage**: 512 MB (para SQLite local)

### Otimizações
- `DEBUG=false` em produção
- Monitorar uso de memória nos logs
- Configurar limits de rate limiting se necessário

## 🎯 Validação Final

Após deploy bem-sucedido:

1. ✅ Acesse a URL fornecida pelo Railway
2. ✅ Interface do Pedro carrega corretamente
3. ✅ Faça uma consulta de teste médica
4. ✅ Verifique resposta com base no RAG
5. ✅ Teste integração PubMed (se configurada)

## 📞 Suporte

Em caso de problemas:
1. Verifique logs no Railway Dashboard
2. Confirme todas as variáveis de ambiente
3. Teste localmente com a mesma configuração
4. Verifique se o banco RAG está acessível

---
🩺 **Pedro - Assistente Clínico Pediátrico**  
Deploy adaptado para Railway | Documentação atualizada em {{ data_atual }}
