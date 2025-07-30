# 🩺 Pedro API - Guia de Uso

## 📋 Endpoints Disponíveis

Todos os endpoints abaixo aceitam consultas médicas via POST:

- `/chat`
- `/api/chat`
- `/v1/chat`
- `/message`
- `/pedro`
- `/ask`
- `/query`

## 🔧 Como Usar

### 1. Health Check
```bash
curl https://seu-app.railway.app/health
```

### 2. Consulta Médica
```bash
curl -X POST https://seu-app.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "dose midazolam para criança 15kg sedação",
    "session_id": "opcional-123"
  }'
```

### 3. Informações do Agente
```bash
curl https://seu-app.railway.app/agents/pedro/info
```

## 📝 Formato da Requisição

```json
{
  "message": "sua consulta médica aqui",
  "session_id": "opcional"
}
```

## 📨 Formato da Resposta

```json
{
  "response": "resposta clínica do Pedro",
  "agent": "Pedro",
  "status": "success",
  "session_id": "opcional"
}
```

## 🧪 Exemplos de Consultas

### Cálculo de Dose
```json
{
  "message": "dose midazolam criança 20kg"
}
```

### Protocolo Clínico
```json
{
  "message": "manejo bronquiolite lactente"
}
```

### Cenário de Emergência
```json
{
  "message": "criança 3 anos choque séptico"
}
```

### Pesquisa Científica
```json
{
  "message": "evidências corticoides bronquiolite pediatria"
}
```

## 🔍 Status Codes

- `200`: Sucesso
- `422`: Erro de validação (dados inválidos)
- `500`: Erro interno do servidor
- `503`: Serviço indisponível

## 🛠️ Teste Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar localmente
uvicorn main:app --host 0.0.0.0 --port 8000

# Testar
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "teste dose paracetamol 10kg"}'
```

## 📱 Integração Frontend

### JavaScript/Fetch
```javascript
const response = await fetch('/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'dose amoxicilina criança 8kg',
    session_id: 'user-123'
  })
});

const data = await response.json();
console.log(data.response);
```

### Python/Requests
```python
import requests

response = requests.post('/chat', json={
    'message': 'manejo asma aguda pediatria',
    'session_id': 'session-456'
})

print(response.json()['response'])
```

## 🔐 Segurança

- CORS habilitado para todos os origins (desenvolvimento)
- Para produção, configure origins específicos
- Rate limiting recomendado para uso público
- Logs de consultas para auditoria médica

## 📊 Monitoramento

Verifique os logs do Railway para:
- Tempo de resposta das consultas
- Erros de execução
- Uso de recursos (CPU/memória)
- Hits nos diferentes endpoints
