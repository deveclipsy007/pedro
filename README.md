# Agente Pedro - Assistente Clínico Pediátrico

## 📋 Visão Geral

O Agente Pedro é um assistente clínico especializado em pediatria desenvolvido com o framework Agno, integrando Retrieval-Augmented Generation (RAG) com protocolos clínicos reais da Pedlife e busca científica em PubMed. O agente está preparado para deploy no Render e integração com frontends React.

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   PROTOCOLOS    │ →  │   PROCESSAMENTO  │ →  │   AGENTE PEDRO     │
│   PEDLIFE       │     │   RAG SEMÂNTICO  │     │   (AGNO FRAMEWORK) │
└─────────────────┘     └──────────────────┘     └────────────────────┘
         │                        │                         │
         ▼                        ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  VADEMECUM      │ →  │  BANCO DE DADOS  │ ← → │  API REST (FASTAPI)│
│  PEDIÁTRICO     │     │  SEMÂNTICO       │     │  + PLAYGROUND      │
└─────────────────┘     └──────────────────┘     └────────────────────┘
         │                        │                         │
         ▼                        ▼                         ▼
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│   PUBMED        │ ← → │  BUSCA CIENTÍFICA│ ← → │  FRONTEND REACT    │
│   INTEGRATION   │     │  EVIDÊNCIAS      │     │  (INTEGRAÇÃO)      │
└─────────────────┘     └──────────────────┘     └────────────────────┘
```

### Componentes Principais:

1. **Protocolos Pedlife**: 26 documentos clínicos (.md) com protocolos pediátricos reais
2. **Processamento RAG**: Sistema semântico com chunking inteligente e busca por similaridade
3. **Agente Pedro**: Assistente clínico especializado com 5 ferramentas integradas
4. **API REST**: Endpoints FastAPI expostos automaticamente pelo Playground Agno
5. **Frontend React**: Interface web para interação com o agente

## 📁 Estrutura do Projeto

```
project/
├── data/
│   ├── raw/              # Protocolos Pedlife originais (.md)
│   └── enhanced_rag.db   # Banco de dados semântico processado
├── playground/
│   ├── pedro_playground_medico.py  # Agente + API REST
│   └── config.py         # Configurações do playground
├── pedro_enhanced_search.py       # Busca semântica aprimorada
├── pubmed_integration.py          # Integração com PubMed
├── activate_enhanced_rag.py       # Ativação do pipeline RAG
├── enhanced_service.py            # Serviço RAG semântico
├── pedro_rag_wrapper.py           # Wrapper robusto para RAG
├── requirements.txt       # Dependências do projeto
├── render.yaml            # Configuração de deploy no Render
├── ESSENTIAL_FILES.md     # Arquivos essenciais para produção
├── REACT_INTEGRATION.md   # Documentação de integração React
└── README.md              # Este arquivo
```

## 🚀 Quick Start

### 1. Configuração do Ambiente

```bash
# Clone e configure o projeto
git clone <repo-url>
cd pedro-agent

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente (opcional)
cp .env.example .env.test
# Edite .env.test com suas credenciais (API keys, etc)
```

### 2. Processar Protocolos e Ativar RAG

```bash
# 1. Coloque os protocolos .md em data/raw/
# 2. Ative o pipeline RAG semântico:
python activate_enhanced_rag.py

# 3. Verifique se o banco enhanced_rag.db foi criado
ls data/enhanced_rag.db
```

### 3. Executar Agente Localmente

```bash
# Iniciar o Playground do Agente Pedro
python playground/pedro_playground_medico.py

# Acesse http://localhost:7778 para interface web
# A API REST estará disponível em http://localhost:7778
```

### 4. Deploy no Render

```bash
# O deploy é feito automaticamente via render.yaml
# Basta conectar o repositório ao Render
# O endpoint público será fornecido pelo Render
```

## 🔧 Funcionamento do Agente Pedro

### Ferramentas Integradas

1. **retrieve_docs**: Busca semântica em protocolos Pedlife
2. **calc_dose**: Calculadora posológica pediátrica
3. **test_medical_scenarios**: Teste de cenários clínicos
4. **clinical_alert**: Alertas clínicos baseados em protocolos
5. **pubmed_search**: Busca científica em literatura médica

### Fluxo de Processamento

1. **Consulta Recebida**: Pergunta clínica via API ou interface web
2. **Detecção Inteligente**: Identificação automática de tipo de consulta
3. **Busca RAG**: Consulta a protocolos Pedlife via busca semântica
4. **Processamento**: Análise e combinação de informações relevantes
5. **Resposta Final**: Retorno com fontes, evidências e recomendações

## 🌐 Integração com Frontend React

### Endpoints da API

O Playground do Agno expõe automaticamente uma API REST completa:

```
# Listar agentes disponíveis
GET /api/agents

# Enviar consulta para o agente
POST /api/agents/pedro/runs
Content-Type: application/json

{
  "task": "Qual a dose de midazolam para sedação de criança de 15kg?"
}

# Status do playground
GET /api/playground/status

# Documentação interativa
GET /docs
GET /redoc
```

### Exemplo de Integração React

```javascript
// Exemplo de componente React para interagir com o Pedro
import React, { useState } from 'react';

const PedroChat = () => {
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // Substitua pela URL do seu deploy no Render
      const res = await fetch('https://seu-app.onrender.com/api/agents/pedro/runs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ task: message })
      });
      
      const data = await res.json();
      setResponse(data.response || data.result);
    } catch (error) {
      setResponse('Erro na comunicação com o agente Pedro');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input 
          type="text" 
          value={message} 
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Digite sua consulta clínica..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Processando...' : 'Enviar'}
        </button>
      </form>
      
      {response && (
        <div className="response">
          <h3>Resposta do Pedro:</h3>
          <div dangerouslySetInnerHTML={{ __html: response }} />
        </div>
      )}
    </div>
  );
};

export default PedroChat;
```

### Considerações de Segurança

1. **Sem Autenticação Padrão**: A API REST local/deploy não requer chave por padrão
2. **Implementação de Autenticação**: Para produção, adicione middleware de autenticação
3. **HTTPS**: Em produção, use sempre conexões HTTPS
4. **Rate Limiting**: Implemente limites de requisições para evitar abuso

## 🧪 Testes e Validação

```bash
# Testar funcionalidades do agente
python teste_pedro_completo.py

# Validar integração RAG
python teste_rag_integration.py

# Testar cálculos posológicos
python teste_calc_dose.py
```

## 📈 Monitoramento e Logs

- **Logs do Agente**: Disponíveis no console durante execução
- **Logs do RAG**: Registrados em `logs/rag_processing.log`
- **Monitoramento de Erros**: Tratamento de exceções com mensagens detalhadas
- **Performance**: Tempo de resposta registrado para otimização

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.
