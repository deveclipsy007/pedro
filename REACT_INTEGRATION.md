# Integração do Agente Pedro com React

## 🚀 Visão Geral

Esta documentação explica como integrar o agente Pedro com uma aplicação React via API REST. Após o deploy no Render, o Pedro expõe uma API que pode ser consumida diretamente pelo frontend.

## 🌐 Endpoints da API

Após o deploy no Render, o Pedro estará disponível em uma URL pública como:
```
https://seu-app-no-render.onrender.com
```

### Endpoints Disponíveis:

1. **Listar Agentes** (GET)
   ```
   GET /api/agents
   ```
   Retorna informações sobre os agentes disponíveis.

2. **Enviar Mensagem** (POST)
   ```
   POST /api/agents/{agent_id}/runs
   ```
   Envia uma mensagem para o agente e obtém uma resposta.

3. **Status do Playground** (GET)
   ```
   GET /api/playground/status
   ```
   Verifica o status do playground.

## 🔧 Configuração do React

### 1. Instalação de Dependências

Instale as dependências necessárias no seu projeto React:

```bash
npm install axios
# ou
yarn add axios
```

### 2. Configuração de Variáveis de Ambiente

Crie um arquivo `.env` na raiz do seu projeto React:

```env
REACT_APP_PEDRO_API_URL=https://seu-app-no-render.onrender.com
```

### 3. Criação do Serviço de API

Crie um arquivo `src/services/pedroApi.js`:

```javascript
import axios from 'axios';

// Configuração da instância do axios
const api = axios.create({
  baseURL: process.env.REACT_APP_PEDRO_API_URL || 'http://localhost:7778',
  timeout: 30000, // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  },
});

// Função para obter informações dos agentes
export const getAgents = async () => {
  try {
    const response = await api.get('/api/agents');
    return response.data;
  } catch (error) {
    console.error('Erro ao obter agentes:', error);
    throw error;
  }
};

// Função para enviar mensagem ao agente
export const sendMessageToAgent = async (agentId, message, sessionId = null) => {
  try {
    const payload = {
      task: message,
      ...(sessionId && { session_id: sessionId }),
    };
    
    const response = await api.post(`/api/agents/${agentId}/runs`, payload);
    return response.data;
  } catch (error) {
    console.error('Erro ao enviar mensagem:', error);
    throw error;
  }
};

// Função para verificar status do playground
export const getPlaygroundStatus = async () => {
  try {
    const response = await api.get('/api/playground/status');
    return response.data;
  } catch (error) {
    console.error('Erro ao verificar status:', error);
    throw error;
  }
};

export default {
  getAgents,
  sendMessageToAgent,
  getPlaygroundStatus,
};
```

## 💻 Exemplo de Componente React

Crie um componente `src/components/PedroChat.js`:

```javascript
import React, { useState, useEffect } from 'react';
import { getAgents, sendMessageToAgent } from '../services/pedroApi';

const PedroChat = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState('');
  const [message, setMessage] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  
  // Carrega os agentes disponíveis
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const data = await getAgents();
        setAgents(data);
        if (data.length > 0) {
          setSelectedAgent(data[0].agent_id);
        }
      } catch (error) {
        console.error('Falha ao carregar agentes:', error);
      }
    };
    
    fetchAgents();
  }, []);
  
  // Envia mensagem para o agente
  const handleSendMessage = async () => {
    if (!message.trim() || !selectedAgent) return;
    
    // Adiciona a mensagem do usuário à conversa
    const userMessage = {
      id: Date.now(),
      sender: 'user',
      content: message,
      timestamp: new Date(),
    };
    
    setConversation(prev => [...prev, userMessage]);
    setLoading(true);
    setMessage('');
    
    try {
      // Envia a mensagem para o agente
      const response = await sendMessageToAgent(selectedAgent, message);
      
      // Adiciona a resposta do agente à conversa
      const agentMessage = {
        id: Date.now() + 1,
        sender: 'agent',
        content: response.response || response.output || 'Sem resposta',
        timestamp: new Date(),
      };
      
      setConversation(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Erro na comunicação com o agente:', error);
      
      // Adiciona mensagem de erro à conversa
      const errorMessage = {
        id: Date.now() + 1,
        sender: 'system',
        content: 'Erro na comunicação com o agente. Tente novamente.',
        timestamp: new Date(),
      };
      
      setConversation(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };
  
  // Manipula o envio ao pressionar Enter
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  return (
    <div className="pedro-chat-container">
      <div className="chat-header">
        <h2>Assistente Clínico Pedro</h2>
        {agents.length > 0 && (
          <select 
            value={selectedAgent} 
            onChange={(e) => setSelectedAgent(e.target.value)}
            disabled={loading}
          >
            {agents.map(agent => (
              <option key={agent.agent_id} value={agent.agent_id}>
                {agent.name} - {agent.role}
              </option>
            ))}
          </select>
        )}
      </div>
      
      <div className="chat-messages">
        {conversation.map(msg => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            <div className="message-content">
              {msg.content}
            </div>
            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message agent">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
      </div>
      
      <div className="chat-input">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Digite sua consulta médica..."
          disabled={loading}
          rows="3"
        />
        <button 
          onClick={handleSendMessage}
          disabled={!message.trim() || loading}
        >
          {loading ? 'Enviando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};

export default PedroChat;
```

## 🎨 Estilos CSS

Adicione estilos ao componente criando `src/components/PedroChat.css`:

```css
.pedro-chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chat-header {
  background-color: #007bff;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h2 {
  margin: 0;
  font-size: 1.2rem;
}

.chat-header select {
  padding: 0.5rem;
  border-radius: 4px;
  border: none;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f8f9fa;
}

.message {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
}

.message.user {
  align-items: flex-end;
}

.message.agent, .message.system {
  align-items: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 0.75rem 1rem;
  border-radius: 18px;
  word-wrap: break-word;
}

.message.user .message-content {
  background-color: #007bff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message.agent .message-content {
  background-color: #e9ecef;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message.system .message-content {
  background-color: #fff3cd;
  color: #856404;
  border-bottom-left-radius: 4px;
}

.message-timestamp {
  font-size: 0.75rem;
  color: #6c757d;
  margin-top: 0.25rem;
}

.chat-input {
  display: flex;
  padding: 1rem;
  background-color: white;
  border-top: 1px solid #ddd;
}

.chat-input textarea {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  margin-right: 0.5rem;
}

.chat-input button {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.chat-input button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.typing-indicator {
  display: flex;
  align-items: center;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #6c757d;
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
```

## 📦 Uso do Componente

Importe e use o componente em seu aplicativo React:

```javascript
// src/App.js
import React from 'react';
import PedroChat from './components/PedroChat';
import './components/PedroChat.css';

function App() {
  return (
    <div className="App">
      <PedroChat />
    </div>
  );
}

export default App;
```

## 🔐 Considerações de Segurança

1. **Proteção de Chaves de API**:
   - Nunca exponha chaves de API no frontend
   - Use variáveis de ambiente no backend
   - Implemente autenticação e autorização adequadas

2. **Validação de Entrada**:
   - Sempre valide e sanitize entradas do usuário
   - Limite o tamanho das mensagens
   - Implemente rate limiting

3. **HTTPS**:
   - Certifique-se de que a comunicação usa HTTPS
   - Configure cabeçalhos de segurança apropriados

## 🧪 Testes

Para testar localmente antes do deploy:

1. Inicie o Pedro localmente:
   ```bash
   python playground/pedro_playground_medico.py
   ```

2. Configure a URL base no `.env` do React:
   ```env
   REACT_APP_PEDRO_API_URL=http://localhost:7778
   ```

3. Inicie a aplicação React:
   ```bash
   npm start
   ```

## 🚀 Deploy no Render

1. Após o deploy do Pedro no Render, atualize a URL no `.env` do React:
   ```env
   REACT_APP_PEDRO_API_URL=https://seu-app-no-render.onrender.com
   ```

2. Faça o deploy do frontend React em um serviço como Vercel, Netlify ou Render.

## 📞 Suporte

Para problemas com a integração:

1. Verifique se o Pedro está rodando corretamente no Render
2. Confirme que os endpoints da API estão acessíveis
3. Verifique os logs do Render para erros
4. Teste os endpoints diretamente com ferramentas como Postman ou curl

## 📚 Recursos Adicionais

- [Documentação do Agno Framework](https://docs.agno.com)
- [Documentação do Render](https://render.com/docs)
- [Documentação do React](https://reactjs.org/docs/getting-started.html)
- [Documentação do Axios](https://axios-http.com/docs/intro)
