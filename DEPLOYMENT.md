# Guia de Deploy - Pipeline RAG

## 📋 Visão Geral

Este guia detalha como migrar do ambiente de teste para produção seguindo as melhores práticas de segurança e performance.

## 🔄 Migração: Teste → Produção

### 1. Preparação do Ambiente de Produção

#### 1.1 Infraestrutura Necessária

```bash
# Recursos mínimos recomendados:
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Bandwidth: 100Mbps
```

#### 1.2 Configuração do Supabase (Produção)

1. **Criar projeto Supabase**:
   ```bash
   # Acesse https://supabase.com
   # Crie novo projeto com região apropriada
   # Anote: URL, anon key, service key
   ```

2. **Configurar extensão pgvector**:
   ```sql
   -- No SQL Editor do Supabase
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Configurar Row Level Security**:
   ```sql
   -- Ativar RLS nas tabelas
   ALTER TABLE stage_raw ENABLE ROW LEVEL SECURITY;
   ALTER TABLE stage_clean ENABLE ROW LEVEL SECURITY;
   ALTER TABLE stage_chunks ENABLE ROW LEVEL SECURITY;
   ALTER TABLE vector_store ENABLE ROW LEVEL SECURITY;
   
   -- Política para acesso do serviço
   CREATE POLICY "Service access" ON vector_store
   FOR ALL USING (auth.role() = 'service_role');
   ```

#### 1.3 Configuração de Variáveis de Ambiente

```bash
# Copie .env.example para .env.prod
cp .env.example .env.prod

# Configure variáveis de produção
nano .env.prod
```

**Variáveis críticas para produção**:
```env
# Database (Supabase)
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key

# OpenAI
OPENAI_API_KEY=sk-sua-chave-producao

# Security
SECRET_KEY=chave-super-segura-256-bits
ALLOWED_HOSTS=seudominio.com,api.seudominio.com

# Environment
ENVIRONMENT=production
DEBUG=false
```

### 2. Deploy com Docker

#### 2.1 Build da Imagem

```bash
# Build para produção
docker build -f docker/Dockerfile -t rag-pipeline:prod .

# Tag para registry
docker tag rag-pipeline:prod registry.seudominio.com/rag-pipeline:latest
```

#### 2.2 Deploy com Docker Compose

```bash
# Deploy em produção
docker-compose -f docker/docker-compose.prod.yml up -d

# Verificar status
docker-compose -f docker/docker-compose.prod.yml ps

# Ver logs
docker-compose -f docker/docker-compose.prod.yml logs -f
```

### 3. Deploy em Plataformas Cloud

#### 3.1 Railway

1. **Criar railway.toml**:
```toml
[build]
builder = "nixpacks"

[deploy]
healthcheckPath = "/"
restartPolicyType = "always"

[environment]
PORT = "8000"
DATABASE_URL = "sqlite:///data/enhanced_rag.db"
```

2. **Deploy**:
```bash
# Conecte repositório no Railway
# Configure variáveis de ambiente
# Deploy automático via Git
```

#### 3.2 Fly.io

1. **Configurar fly.toml**:
```toml
app = "rag-pipeline"
primary_region = "gru"

[build]
  dockerfile = "docker/Dockerfile"

[env]
  ENVIRONMENT = "production"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"
  script_checks = []

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20
    type = "connections"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    grace_period = "1s"
    interval = "15s"
    restart_limit = 0
    timeout = "2s"
```

2. **Deploy**:
```bash
# Instalar Fly CLI
curl -L https://fly.io/install.sh | sh

# Login e deploy
fly auth login
fly deploy
```

### 4. Configuração de Monitoramento

#### 4.1 Logs Centralizados

```bash
# Configurar agregação de logs
# Usar ELK Stack ou similar
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  elasticsearch:7.14.0
```

#### 4.2 Métricas com Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rag-pipeline'
    static_configs:
      - targets: ['rag-pipeline:9090']
```

#### 4.3 Alertas

```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    slack_configs:
      - api_url: 'SEU_WEBHOOK_SLACK'
        channel: '#alerts'
```

### 5. Automação e CI/CD

#### 5.1 GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and Deploy
        run: |
          docker build -t rag-pipeline:${{ github.sha }} .
          # Deploy para sua plataforma
```

#### 5.2 Cron Jobs para Pipeline

```bash
# Crontab para execução automática
# Executar pipeline a cada 6 horas
0 */6 * * * cd /app && python scripts/runner.py

# Backup diário
0 2 * * * cd /app && python scripts/backup.py

# Limpeza semanal
0 3 * * 0 cd /app && python scripts/cleanup.py
```

### 6. Segurança em Produção

#### 6.1 Secrets Management

```bash
# Usar Docker Secrets ou equivalente
echo "sua-openai-key" | docker secret create openai_api_key -
echo "sua-db-password" | docker secret create db_password -
```

#### 6.2 Network Security

```yaml
# docker-compose.prod.yml
networks:
  rag_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

#### 6.3 SSL/TLS

```nginx
# nginx.prod.conf
server {
    listen 443 ssl http2;
    server_name api.seudominio.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://rag_api:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 7. Backup e Recuperação

#### 7.1 Backup Automático

```python
# scripts/backup.py
import subprocess
import datetime

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_rag_{timestamp}.sql"
    
    subprocess.run([
        "pg_dump", 
        os.getenv("DATABASE_URL"),
        "-f", backup_file
    ])
```

#### 7.2 Estratégia de Recuperação

```bash
# Plano de recuperação em caso de falha
1. Verificar logs de erro
2. Restaurar backup mais recente
3. Re-executar pipeline se necessário
4. Validar integridade dos dados
```

### 8. Performance e Otimização

#### 8.1 Otimização de Banco

```sql
-- Índices para performance
CREATE INDEX CONCURRENTLY idx_vector_embedding_cosine 
ON vector_store USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

-- Vacuum e analyze regulares
VACUUM ANALYZE vector_store;
```

#### 8.2 Cache Redis

```python
# Configurar cache para embeddings
REDIS_URL = "redis://redis:6379/0"
CACHE_TTL = 3600  # 1 hora
```

### 9. Validação Pós-Deploy

#### 9.1 Health Checks

```bash
# Verificar saúde da API
curl -f https://api.seudominio.com/health

# Testar endpoint RAG
curl -X POST https://api.seudominio.com/rag \
  -H "Content-Type: application/json" \
  -d '{"question": "Como funciona o RAG?"}'
```

#### 9.2 Testes de Carga

```bash
# Usar Apache Bench ou similar
ab -n 1000 -c 10 https://api.seudominio.com/health
```

### 10. Manutenção Contínua

#### 10.1 Atualizações

```bash
# Processo de atualização zero-downtime
1. Deploy nova versão em staging
2. Executar testes automatizados
3. Deploy gradual em produção
4. Monitorar métricas
5. Rollback se necessário
```

#### 10.2 Monitoramento de Custos

```bash
# Monitorar custos da OpenAI API
# Configurar alertas de uso
# Otimizar batch sizes conforme necessário
```

## 🚨 Checklist de Produção

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados com backup automático
- [ ] SSL/TLS configurado
- [ ] Monitoramento ativo
- [ ] Logs centralizados
- [ ] Secrets seguros
- [ ] Health checks funcionando
- [ ] Alertas configurados
- [ ] Documentação atualizada
- [ ] Equipe treinada

## 📞 Suporte

Em caso de problemas:
1. Verificar logs: `docker-compose logs -f`
2. Verificar health checks
3. Consultar documentação
4. Contatar equipe de desenvolvimento
