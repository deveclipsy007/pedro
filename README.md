# Pipeline RAG - Projeto Completo

## 📋 Visão Geral

Este projeto implementa um pipeline completo de RAG (Retrieval-Augmented Generation) seguindo as melhores práticas de desenvolvimento, com ambiente de teste e produção bem estruturados.

## 🏗️ Arquitetura do Pipeline

```
┌────────────┐     ┌───────────────┐     ┌────────────────┐
│  EXTRAÇÃO  │ →  │ PROCESSAMENTO │ →  │ AVALIAÇÃO + CI │
└────────────┘     └───────────────┘     └────────────────┘
```

### Fases do Pipeline:

1. **Extração**: Captura documentos brutos (.md, .mdx, .json, .docx)
2. **Processamento**: Limpa, converte e fragmenta em chunks
3. **Avaliação & Deploy**: Testa abordagens, elege a melhor e automatiza

## 📁 Estrutura do Projeto

```
project/
├── data/
│   ├── raw/              # Arquivos originais (.md)
│   ├── processed/        # MD normalizado
│   └── tests/            # Queries de teste
├── scripts/
│   ├── 1_extrai_dados.py
│   ├── 2_normaliza_e_chunk.py
│   ├── 3_gera_embeddings.py
│   ├── 4_avalia.py
│   └── runner.py
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── docker-compose.prod.yml
├── config/
│   ├── database.py
│   ├── settings.py
│   └── logging.py
├── src/
│   ├── raglib/
│   │   ├── __init__.py
│   │   ├── extract.py
│   │   ├── chunk.py
│   │   ├── embeddings.py
│   │   └── evaluate.py
│   └── api/
│       ├── main.py
│       └── endpoints.py
├── tests/
│   ├── queries.yaml
│   └── test_pipeline.py
├── logs/
├── .env.example
├── .env.test
├── .env.prod
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## 🚀 Quick Start

### 1. Configuração do Ambiente de Teste

```bash
# Clone e configure o projeto
git clone <repo-url>
cd rag-pipeline

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env.test
# Edite .env.test com suas credenciais
```

### 2. Executar Pipeline Local

```bash
# 1. Coloque arquivos .md em data/raw/
# 2. Execute scripts sequencialmente:
poetry run python scripts/1_extrai_dados.py
poetry run python scripts/2_normaliza_e_chunk.py
poetry run python scripts/3_gera_embeddings.py
poetry run python scripts/4_avalia.py
```

### 3. Executar com Docker (Recomendado)

```bash
# Ambiente de teste
docker-compose up --build

# Ambiente de produção
docker-compose -f docker/docker-compose.prod.yml up --build
```

## 🔧 Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env.test` ou `.env.prod` e configure:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/rag_db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# OpenAI
OPENAI_API_KEY=sk-...

# Pipeline
WATCH=true
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
EMBEDDING_MODEL=text-embedding-3-small
```

## 📊 Monitoramento

- **Logs**: Disponíveis em `/logs/{step}.jsonl`
- **KPIs**: Latência, tokens gerados, precision@k
- **Avaliação**: Recall@k e MRR por estratégia de chunking

## 🌐 Deploy em Produção

### Supabase + Render/Fly.io

1. Configure Supabase com extensão pgvector
2. Build e push da imagem Docker
3. Configure cron jobs para execução automática
4. Ative Row-Level Security

### Integração com Agente IA

```python
# Endpoint RAG
GET /rag?question=sua_pergunta

# Retorna:
{
  "answer": "resposta contextual",
  "sources": ["fonte1.md", "fonte2.md"],
  "chunks": [...],
  "metadata": {...}
}
```

## 🧪 Testes

```bash
# Executar testes
pytest tests/

# Avaliar estratégias de chunking
python scripts/4_avalia.py
```

## 📈 Próximos Passos

- [ ] Implementar prompts RAG especializados
- [ ] Configurar governança e controle de acesso
- [ ] Desenvolver UI (React + Supabase)
- [ ] Otimizar performance e custos

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.
