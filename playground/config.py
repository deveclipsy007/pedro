"""
Configurações específicas para o Agno Playground do Pedro
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv('../.env.test')

# Configurações do Playground
PLAYGROUND_CONFIG = {
    "title": "Pedro - Assistente Clínico",
    "description": "Interface web interativa para cálculos de dose e consulta de protocolos médicos",
    "favicon": "🏥",
    "host": "0.0.0.0",
    "port": 7777,
    "debug": False,
    "theme": "medical"
}

# Configurações do Agente
AGENT_CONFIG = {
    "name": "Pedro",
    "role": "Assistente Clínico Especializado",
    "show_tool_calls": True,
    "markdown": True,
    "debug_mode": False,
    "model": "gpt-4o"  # Modelo padrão do Agno
}

# Mensagens de boas-vindas
WELCOME_MESSAGES = [
    "👋 Olá! Sou o Pedro, seu assistente clínico especializado.",
    "💊 Posso ajudar com cálculos de dosagem medicamentosa.",
    "📋 Também consulto protocolos médicos atualizados.",
    "⚠️ Lembre-se: sempre valide com o prescritor responsável!",
    "",
    "🔧 **Comandos úteis:**",
    "• 'Calcule dose de [medicamento] para [peso]kg'",
    "• 'Busque protocolo sobre [condição]'",
    "• 'Gere alerta clínico para [condição]'"
]

# Exemplos de consultas
EXAMPLE_QUERIES = [
    "Calcule a dose de paracetamol para uma criança de 25kg",
    "Busque protocolos sobre febre em pediatria", 
    "Qual a dose de amoxicilina para adulto de 70kg?",
    "Gere alerta clínico para hipertensão severa",
    "Protocolo para manejo de dor pós-operatória"
]
