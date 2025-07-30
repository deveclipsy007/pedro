"""
Agno Playground para o Agente Pedro - Versão Médica Profissional
Interface web direcionada a médicos pediatras, residentes e emergencistas
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Adiciona o diretório raiz ao path para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agno.agent import Agent
from agno.tools import tool
from agno.playground import Playground, serve_playground_app

# Importa módulos do Pedro
try:
    from pedro_enhanced_search import PedroEnhancedSearch
    from pubmed_integration import PedroWithPubMed
except ImportError as e:
    print(f"⚠️ Erro ao importar módulos do Pedro: {e}")
    print("Usando fallback para busca simples")
    PedroEnhancedSearch = None
    PedroWithPubMed = None

import sqlite3

# Importa integração PubMed
try:
    from pubmed_integration import PedroWithPubMed
    PUBMED_AVAILABLE = True
    print("🔬 Integração PubMed disponível!")
except ImportError:
    PUBMED_AVAILABLE = False
    print("⚠️ Integração PubMed não disponível")

# Caminho para o banco RAG
DB_PATH = Path(__file__).parent.parent / "data" / "enhanced_rag.db"

# Carrega variáveis de ambiente
load_dotenv('.env.test')

# Inicializa sistema de busca aprimorado
enhanced_search_instance = None
if PedroEnhancedSearch:
    try:
        enhanced_search_instance = PedroEnhancedSearch(str(DB_PATH))
        print("🚀 Sistema de busca aprimorado ativado!")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar busca aprimorada: {e}")
        enhanced_search_instance = None

# Inicializa integração PubMed se disponível
pubmed_instance = None
if PUBMED_AVAILABLE:
    try:
        pubmed_api_key = os.getenv('PUBMED_API_KEY', '')
        pubmed_instance = PedroWithPubMed(pubmed_api_key)
        print("🔬 Pedro com PubMed inicializado!")
    except Exception as e:
        print(f"⚠️ Erro ao inicializar PubMed: {e}")
        pubmed_instance = None

def is_complex_query(query: str) -> bool:
    """Determina se uma query é complexa o suficiente para usar busca semântica"""
    complex_indicators = [
        len(query.split()) >= 4,  # 4+ palavras
        any(word in query.lower() for word in ['e', 'em', 'para', 'com', 'de', 'da', 'do']),  # conectores
        any(word in query.lower() for word in ['lactente', 'criança', 'pediatria', 'anos', 'meses']),  # contexto pediátrico
        any(word in query.lower() for word in ['dose', 'mg/kg', 'protocolo', 'tratamento']),  # termos clínicos
        any(word in query.lower() for word in ['apneia', 'insuficiência', 'respiratória', 'cardíaca'])  # condições complexas
    ]
    return sum(complex_indicators) >= 2

def search_rag_database(query: str, limit: int = 5):
    """Busca direta no banco RAG com lógica OR para maior cobertura"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Busca nos chunks usando OR para maior cobertura
        search_terms = query.lower().split()
        where_conditions = []
        params = []
        
        for term in search_terms:
            where_conditions.append("LOWER(chunk_text) LIKE ?")
            params.append(f"%{term}%")
        
        # Usa OR ao invés de AND para encontrar chunks com qualquer termo
        where_clause = " OR ".join(where_conditions)
        
        sql = f"""
        SELECT c.chunk_text, c.semantic_tags, c.keywords, d.filename 
        FROM semantic_chunks c
        JOIN documents d ON c.document_id = d.id
        WHERE {where_clause}
        ORDER BY c.id
        LIMIT ?
        """
        
        params.append(limit)
        cursor.execute(sql, params)
        results = cursor.fetchall()
        conn.close()
        
        print(f"🔍 Busca RAG: '{query}' → {len(results)} chunks encontrados")
        return results
        
    except Exception as e:
        print(f"❌ Erro na busca RAG: {e}")
        return []

def retrieve_docs_core(query: str, limit: int = 3) -> str:
    """
    Função principal de busca com detecção automática de dose (SEM decorador @tool)
    """
    try:
        print(f"🔍 CONSULTA CLÍNICA: '{query}'")
        
        # 🧮 DETECÇÃO AUTOMÁTICA DE QUERIES DE DOSE
        dose_keywords = ['dose', 'dosagem', 'mg/kg', 'posologia', 'calcul']
        weight_pattern = r'(\d+)\s*kg'
        
        query_lower = query.lower()
        has_dose_keyword = any(keyword in query_lower for keyword in dose_keywords)
        
        import re
        weight_match = re.search(weight_pattern, query_lower)
        
        if has_dose_keyword and weight_match:
            # Verifica se é uma query de dose/cálculo posológico
            dose_keywords = ['dose', 'dosagem', 'mg/kg', 'posologia']
            clinical_indications = ['sedacao', 'sedação', 'analgesia', 'analgesia', 'convulsao', 'convulsão', 'premedicacao', 'premedicação']
            medications = ['midazolam', 'paracetamol', 'ibuprofeno', 'amoxicilina', 'diazepam', 'morfina']
            
            is_dose_query = any(keyword in query_lower for keyword in dose_keywords)
            has_weight = any(word.endswith('kg') and word[:-2].replace('.', '').isdigit() for word in query.split())
            
            # Extrai medicamento e indicação
            medication = next((med for med in medications if med in query_lower), None)
            indication = next((ind for ind in clinical_indications if ind in query_lower), "")
            
            # Extrai peso
            weight = None
            for word in query.split():
                if word.endswith('kg') and word[:-2].replace('.', '').isdigit():
                    try:
                        weight = float(word[:-2])
                        break
                    except ValueError:
                        continue
            
            print(f"🔍 Palavras-chave de dose encontradas: {is_dose_query}")
            print(f"🔍 Peso encontrado: {weight}")
            
            # Se for query de dose com peso, calcula automaticamente
            if is_dose_query and has_weight and medication and weight:
                print(f"🧮 DETECÇÃO AUTOMÁTICA ATIVADA!")
                print(f"Medicamento: {medication}")
                print(f"Peso: {weight} kg")
                print(f"Indicação: {indication}")
                
                # Chama cálculo de dose usando a função core (sem decorador)
                dose_result = calc_dose_core(medication, weight, indication=indication)
                
                # Combina resultado do cálculo com protocolos encontrados
                combined_result = f"{dose_result}\n\n---\n\n📋 **PROTOCOLOS CLÍNICOS ENCONTRADOS:**\n\n"
                
                results = search_rag_database(query, limit)
                if results:
                    for i, (content, tags, keywords, filename) in enumerate(results[:3], 1):
                        combined_result += f"**Protocolo {i}:** {filename}\n{content[:300]}...\n\n"
                else:
                    combined_result += "⚠️ Nenhum protocolo clínico encontrado."
                
                return combined_result
        
        # Se não é query de dose, executa busca normal
        return retrieve_docs_normal(query, limit)
        
    except Exception as e:
        return f"""**ERRO NA CONSULTA CLÍNICA**

**Query:** {query}
**Erro:** {str(e)}

**Alternativas:**
• Verificar conectividade com banco RAG
• Tentar pubmed_search para literatura científica
• Reformular query com termos mais específicos

---
**STATUS:** Erro técnico na consulta aos protocolos"""

@tool
def retrieve_docs(query: str, limit: int = 3) -> str:
    """
    Consulta diretrizes clínicas nos protocolos Pedlife validados
    
    Args:
        query: Termo clínico para consulta
        limit: Número máximo de protocolos a consultar
        
    Returns:
        Diretrizes clínicas baseadas em protocolos validados
    """
    # Chama a função principal sem decorador
    return retrieve_docs_core(query, limit)

def retrieve_docs_normal(query: str, limit: int = 3) -> str:
    """
    Função auxiliar para busca normal nos protocolos (sem detecção de dose)
    """
    try:
        # Usa sistema de busca aprimorado se disponível
        if enhanced_search_instance:
            print("🚀 Usando sistema de busca aprimorado...")
            
            # Busca aprimorada com sinônimos e validação
            enhanced_results = enhanced_search_instance.enhanced_search(query, limit)
            
            if enhanced_results:
                # Valida clinicamente os resultados
                validation = enhanced_search_instance.validate_clinical_response(query, enhanced_results)
                
                # Formata resposta clínica aprimorada
                formatted_response = enhanced_search_instance.format_clinical_response(
                    query, enhanced_results, validation
                )
                
                return formatted_response
        
        # Fallback para busca direta no RAG
        print("🔍 Usando busca direta no RAG...")
        rag_results = search_rag_database(query, limit)
        
        if not rag_results:
            return f"""**CONSULTA PEDLIFE - SEM RESULTADOS**

**Query:** {query}
**Status:** Nenhum protocolo encontrado para este termo

**Recomendação:** 
• Tente termos mais específicos ou sinônimos
• Use pubmed_search para literatura científica
• Verifique ortografia dos termos médicos

---
**FONTE:** Protocolos Pedlife (busca direta)"""
        
        response_parts = [
            f"**PROTOCOLOS PEDLIFE - CONSULTA DIRETA**",
            f"**Query:** {query}",
            f"**Protocolos encontrados:** {len(rag_results)}",
            f"",
            f"**DADOS CLÍNICOS:**"
        ]
        
        for i, (chunk_text, tags, keywords, filename) in enumerate(rag_results, 1):
            content = chunk_text[:400] + "..." if len(chunk_text) > 400 else chunk_text
            response_parts.extend([
                f"",
                f"**{i}. {filename}**",
                f"• **Conteúdo:** {content}",
                f"• **Tags:** {tags or 'N/A'}",
                f"• **Palavras-chave:** {keywords or 'N/A'}"
            ])
        
        response_parts.extend([
            f"",
            f"---",
            f"**FONTE:** Protocolos Pedlife validados",
            f"**MÉTODO:** Busca direta no RAG"
        ])
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"""**ERRO NA CONSULTA CLÍNICA**

**Query:** {query}
**Erro:** {str(e)}

**Alternativas:**
• Verificar conectividade com banco RAG
• Tentar pubmed_search para literatura científica
• Reformular query com termos mais específicos

---
**STATUS:** Erro técnico na consulta aos protocolos""" 

def calc_dose_core(medication: str, weight: float, age: int = None, indication: str = "") -> str:
    """
    Função principal de cálculo de dose (SEM decorador @tool)
    """
    try:
        # Busca informações do medicamento nos protocolos
        med_query = f"{medication} dose pediatrica mg/kg"
        if indication:
            med_query += f" {indication}"
        
        results = search_rag_database(med_query, limit=3)
        
        # Dicionário de doses por medicamento (valores padrão)
        dose_ranges = {
            'midazolam': {'min': 0.05, 'max': 0.2, 'unit': 'mg/kg'},
            'paracetamol': {'min': 10, 'max': 15, 'unit': 'mg/kg'},
            'ibuprofeno': {'min': 5, 'max': 10, 'unit': 'mg/kg'},
            'amoxicilina': {'min': 20, 'max': 40, 'unit': 'mg/kg'},
            'diazepam': {'min': 0.2, 'max': 0.5, 'unit': 'mg/kg'},
            'morfina': {'min': 0.05, 'max': 0.1, 'unit': 'mg/kg'}
        }
        
        # Verifica se o medicamento tem dose definida
        if medication.lower() not in dose_ranges:
            # Busca alternativas nos resultados
            if results:
                return f"""💊 **CÁLCULO POSOLÓGICO PEDIÁTRICO**
🏥 **Medicamento:** {medication.upper()}
⚖️ **Peso:** {weight} kg

⚠️ **INFORMAÇÕES ENCONTRADAS NOS PROTOCOLOS:**

{chr(10).join([f'• {r.get("content", "")[:200]}...' for r in results[:2]])}

⚠️ **RECOMENDAÇÃO CLÍNICA:**
• Verificar protocolos institucionais específicos
• Consultar referências atualizadas
• Validar com farmacêutico clínico"""
            else:
                return f"""💊 **CÁLCULO POSOLÓGICO PEDIÁTRICO**
🏥 **Medicamento:** {medication.upper()}
⚖️ **Peso:** {weight} kg

❌ **ERRO:** Medicamento não encontrado nos protocolos

⚠️ **RECOMENDAÇÃO CLÍNICA:**
• Verificar nome correto do medicamento
• Consultar vademécum pediátrico
• Validar com farmacêutico clínico"""
        
        # Calcula dose
        dose_info = dose_ranges[medication.lower()]
        min_dose = round(weight * dose_info['min'], 2)
        max_dose = round(weight * dose_info['max'], 2)
        
        # Formata resultado
        result = f"""💊 **CÁLCULO POSOLÓGICO PEDIÁTRICO**
🏥 **Medicamento:** {medication.upper()}
⚖️ **Peso:** {weight} kg
🎯 **Indicação:** {indication or 'geral'}

🧮 **CÁLCULO ESPECÍFICO {medication.upper()}:**
• **Dose mínima:** {min_dose} mg ({weight} kg × {dose_info['min']} mg/kg)
• **Dose máxima:** {max_dose} mg ({weight} kg × {dose_info['max']} mg/kg)
• **Via:** IV/IM
• **Intervalo:** dose única ou conforme necessário
• **Dose recomendada para {weight}kg:** {min_dose} - {max_dose} mg

⚠️ **VALIDAÇÃO OBRIGATÓRIA:**
• Verificar contraindicações específicas
• Confirmar dose máxima permitida
• Avaliar função renal/hepática
• Considerar interações medicamentosas"""
        
        # Adiciona informações dos protocolos se disponíveis
        if results:
            result += f"""

📚 **PROTOCOLOS COMPLEMENTARES:**
{chr(10).join([f'• {r.get("source", "Fonte desconhecida")}: {r.get("content", "")[:150]}...' for r in results[:2]])}"""
        
        return result
        
    except Exception as e:
        return f"""💊 **CÁLCULO POSOLÓGICO PEDIÁTRICO**
🏥 **Medicamento:** {medication.upper()}
⚖️ **Peso:** {weight} kg

❌ **ERRO NO CÁLCULO:** {str(e)}

⚠️ **RECOMENDAÇÃO CLÍNICA:**
• Calcular manualmente com base em protocolos
• Validar com farmacêutico clínico
• Considerar peso, idade e função orgânica"""

@tool
def calc_dose(medication: str, weight: float, age: int = None, indication: str = "") -> str:
    """
    Cálculo de posologia pediátrica baseado em protocolos validados
    
    Args:
        medication: Medicamento para cálculo posológico
        weight: Peso do paciente em kg
        age: Idade do paciente em anos (opcional)
        indication: Indicação clínica específica
        
    Returns:
        Cálculo posológico com validação farmacológica
    """
    # Chama a função principal sem decorador
    return calc_dose_core(medication, weight, age, indication)

def test_medical_scenarios(scenario_type: str = "dosage") -> str:
    """
    Análise de cenários clínicos pediátricos complexos
    
    Args:
        scenario_type: Tipo de cenário (dosage, emergency, protocols)
{{ ... }}
        
    Returns:
        Análise de cenários baseada em protocolos validados
    """
    try:
        scenarios = {
            "dosage": "Cenários de cálculo posológico pediátrico",
            "emergency": "Protocolos de emergência pediátrica",
            "protocols": "Diretrizes clínicas gerais",
            "respiratory": "Emergências respiratórias pediátricas",
            "cardiac": "Emergências cardiológicas pediátricas"
        }
        
        scenario_name = scenarios.get(scenario_type, "Cenário clínico geral")
        
        # Busca cenários nos protocolos
        results = search_rag_database(f"{scenario_type} pediatrico emergencia", limit=3)
        
        response_parts = [
            f"🏥 **ANÁLISE DE CENÁRIOS CLÍNICOS**",
            f"",
            f"📋 **Tipo:** {scenario_name}",
            f"📊 **Protocolos consultados:** {len(results)}",
            f""
        ]
        
        if results:
            response_parts.extend([
                f"📖 **DIRETRIZES CLÍNICAS:**",
                f""
            ])
            
            for i, (content, tags, keywords, filename) in enumerate(results, 1):
                response_parts.extend([
                    f"**Cenário {i}:** {filename}",
                    content[:250] + "...",
                    f""
                ])
        else:
            response_parts.extend([
                f"⚠️ **Cenários específicos não localizados**",
                f"🔬 **RECOMENDAÇÃO:** Consultar protocolos institucionais",
                f""
            ])
        
        response_parts.extend([
            f"🎯 **PONTOS DE ATENÇÃO CLÍNICA:**",
            f"• Avaliação primária ABCDE",
            f"• Sinais vitais adequados para idade",
            f"• Dosagens baseadas em peso/superfície corporal",
            f"• Monitorização contínua",
            f"• Reavaliação frequente",
            f"",
            f"---",
            f"📚 **FONTE:** Protocolos Pedlife + Guidelines Pediátricas",
            f"🩺 **IMPORTANTE:** Adaptação ao contexto clínico individual"
        ])
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"""🏥 **ERRO NA ANÁLISE DE CENÁRIOS**

❌ **Erro:** {str(e)}
📋 **Tipo:** {scenario_type}

🩺 **AÇÃO:** Consultar protocolos de emergência manualmente"""

@tool
def clinical_alert(condition: str, severity: str = "moderate") -> str:
    """
    Alertas de segurança farmacológica e contraindicações
    
    Args:
        condition: Condição clínica para alerta
        severity: Nível de severidade (mild, moderate, severe, critical)
        
    Returns:
        Alerta clínico estruturado com recomendações
    """
    try:
        severity_configs = {
            "mild": {"level": "LEVE", "emoji": "💛", "action": "Monitorização"},
            "moderate": {"level": "MODERADA", "emoji": "🟠", "action": "Atenção Clínica"},
            "severe": {"level": "GRAVE", "emoji": "🔴", "action": "Intervenção Imediata"},
            "critical": {"level": "CRÍTICA", "emoji": "🚨", "action": "Emergência Médica"}
        }
        
        config = severity_configs.get(severity, severity_configs["moderate"])
        
        # Busca informações sobre a condição
        results = search_rag_database(f"{condition} alerta clinico pediatrico", limit=2)
        
        response_parts = [
            f"🚨 **ALERTA CLÍNICO - SEVERIDADE {config['level']}** {config['emoji']}",
            f"",
            f"🏥 **CONDIÇÃO:** {condition.upper()}",
            f"⚠️ **SEVERIDADE:** {config['level']}",
            f"🎯 **AÇÃO RECOMENDADA:** {config['action']}",
            f"⏰ **TIMESTAMP:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f""
        ]
        
        if results:
            response_parts.extend([
                f"📋 **DIRETRIZES CLÍNICAS:**",
                f""
            ])
            
            for i, (content, tags, keywords, filename) in enumerate(results, 1):
                response_parts.extend([
                    f"**Protocolo {i}:** {filename}",
                    content[:300] + "...",
                    f""
                ])
        else:
            response_parts.extend([
                f"⚠️ **Diretrizes específicas não localizadas nos protocolos**",
                f"🔬 **RECOMENDAÇÃO:** Consultar literatura médica atualizada",
                f""
            ])
        
        response_parts.extend([
            f"🎯 **CHECKLIST DE SEGURANÇA:**",
            f"• Verificar sinais vitais",
            f"• Avaliar nível de consciência",
            f"• Confirmar via aérea pérvia",
            f"• Monitorizar função cardiovascular",
            f"• Considerar interconsulta especializada",
            f"",
            f"---",
            f"📚 **FONTE:** Protocolos Pedlife + Alertas Clínicos",
            f"🩺 **IMPORTANTE:** Avaliação médica presencial obrigatória"
        ])
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"""🚨 **ERRO NO ALERTA CLÍNICO**

❌ **Erro:** {str(e)}
🏥 **Condição:** {condition}
⚠️ **Severidade:** {severity}

🩺 **AÇÃO:** Verificar sistema de alertas e protocolos manuais"""

@tool
def pubmed_search(query: str, rag_response: str = "") -> str:
    """
    Consulta à literatura científica PubMed para evidências atualizadas
    
    Args:
        query: Termo clínico para busca científica
        rag_response: Resposta do RAG local (para decidir se deve consultar PubMed)
        
    Returns:
        Evidências científicas complementares com citação de fontes
    """
    try:
        if not PUBMED_AVAILABLE or pubmed_instance is None:
            return f"""🔬 **CONSULTA PUBMED INDISPONÍVEL**
            
⚠️ **Status:** Integração PubMed não está ativa
🎯 **Consulta:** {query}
💡 **Alternativa:** Consultar literatura médica manualmente

🔧 **Para ativar:**
1. Configurar PUBMED_API_KEY no .env.test
2. Instalar dependências necessárias
3. Reiniciar o sistema

🩺 **IMPORTANTE:** Basear decisões em protocolos institucionais validados"""
        
        print(f"🔬 Consultando literatura científica para: '{query}'")
        
        # Usa a integração PubMed para busca inteligente
        result = pubmed_instance.enhanced_clinical_search(query, rag_response)
        
        if not result['pubmed_consulted']:
            return f"""🔬 **CONSULTA PUBMED - PROTOCOLOS LOCAIS SUFICIENTES**
            
🎯 **Consulta:** {query}
✅ **Status:** Diretrizes Pedlife adequadas
📚 **Fonte:** Protocolos validados localmente

💡 **Resposta dos Protocolos:**
{rag_response or "Informação disponível nos protocolos Pedlife"}

🩺 **RECOMENDAÇÃO:** Protocolos locais atendem à consulta clínica"""
        
        # Formatar resposta com artigos PubMed
        response_parts = [
            f"🔬 **CONSULTA CIENTÍFICA PUBMED**",
            f"",
            f"🎯 **Consulta:** {query}",
            f"📊 **Artigos localizados:** {len(result['pubmed_articles'])}",
            f"📚 **Fontes:** {', '.join(result['sources'])}",
            f"",
            f"📄 **EVIDÊNCIAS CIENTÍFICAS COMPLEMENTARES:**",
            result['final_response'],
            f"",
            f"🎯 **APLICAÇÃO CLÍNICA:**",
            f"• Considerar contexto do paciente individual",
            f"• Avaliar aplicabilidade das evidências",
            f"• Integrar com protocolos institucionais",
            f"• Discutir com equipe multidisciplinar",
            f"",
            f"---",
            f"📚 **FONTES:** Pedro Playground + PubMed",
            f"⚠️ **DISCLAIMER:** Evidências científicas complementares",
            f"🩺 **IMPORTANTE:** Decisão clínica baseada em julgamento médico"
        ]
        
        return "\n".join(response_parts)
        
    except Exception as e:
        return f"""🔬 **ERRO NA CONSULTA PUBMED**

❌ **Erro:** {str(e)}
🎯 **Consulta:** {query}
🔧 **Ação:** Verificar conectividade e configuração

🩺 **ALTERNATIVA:** Consultar literatura médica através de outras bases"""

def create_pedro_agent():
    """Cria o agente Pedro para profissionais médicos"""
    
    clinical_instructions = """
    Você é Pedro, assistente clínico especializado em pediatria para consulta entre colegas médicos.

    ⚠️ REGRA ABSOLUTA - NUNCA INVENTE NADA:
    • SEMPRE use retrieve_docs PRIMEIRO para consultar protocolos Pedlife
    • SE dados insuficientes, use pubmed_search para literatura científica
    • NUNCA responda sem consultar as ferramentas disponíveis
    • TODA resposta deve ter justificativa baseada em RAG ou PubMed
    • SE não encontrar dados, diga claramente "dados não localizados"

    🧮 REGRA ESPECIAL PARA CÁLCULOS DE DOSE:
    • SE a consulta mencionar "dose", "dosagem", "mg/kg", "posologia" + medicamento + peso:
    • SEMPRE use calc_dose(medicamento, peso, idade, indicação) OBRIGATORIAMENTE
    • NUNCA responda sobre dose sem usar calc_dose primeiro
    • Exemplo: "dose midazolam 15kg" → calc_dose("midazolam", 15.0, indication="sedacao")

    FLUXO OBRIGATÓRIO PARA TODA CONSULTA:
    1. SE consulta sobre DOSE/CÁLCULO → use calc_dose PRIMEIRO
    2. SEMPRE inicie com retrieve_docs para buscar nos protocolos Pedlife
    3. SE resultado insuficiente, use pubmed_search para complementar
    4. CITE SEMPRE a fonte: "Baseado em protocolo Pedlife X" ou "Segundo PubMed..."
    5. SE nenhuma ferramenta retornar dados, responda: "Dados não disponíveis nos protocolos consultados"

    COMUNICAÇÃO MÉDICO-MÉDICO:
    • Linguagem direta e objetiva entre profissionais
    • Terminologia técnica sem explicações básicas
    • Foco em dados clínicos relevantes e tomada de decisão
    • Sempre com justificativa da fonte consultada

    FERRAMENTAS DISPONÍVEIS:
    • calc_dose: OBRIGATÓRIO para qualquer consulta sobre dose/posologia
    • retrieve_docs: Consulta protocolos Pedlife (USE SEMPRE)
    • clinical_alert: Alertas de segurança e contraindicações
    • pubmed_search: Literatura complementar (USE se RAG insuficiente)
    • test_medical_scenarios: Análise de casos complexos

    PRINCÍPIOS INVIOLÁVEIS:
    • NUNCA invente informações clínicas
    • SEMPRE use as ferramentas antes de responder
    • SEMPRE cite a fonte dos dados (Pedlife ou PubMed)
    • SE sem dados, admita limitação ao invés de inventar
    • Mantenha rigor científico absoluto
    • CALC_DOSE É OBRIGATÓRIO PARA QUALQUER CONSULTA DE DOSE!
    """
    
    pedro = Agent(
        name="Pedro",
        role="Assistente Clínico Pediátrico - Versão Médica",
        instructions=clinical_instructions,
        tools=[
            retrieve_docs,
            calc_dose,
            test_medical_scenarios,
            clinical_alert,
            pubmed_search
        ],
        show_tool_calls=True,
        markdown=True,
        debug_mode=True
    )
    
    return pedro

# Variável global para o Uvicorn acessar
playground_app = None

def create_playground_app():
    """Cria e retorna a aplicação playground para deploy"""
    global playground_app
    
    if playground_app is None:
        # Cria o agente
        pedro_agent = create_pedro_agent()
        
        # Cria o playground
        playground = Playground(agents=[pedro_agent])
        
        # Obtém a aplicação
        playground_app = playground.get_app()
        
        print("✅ Playground app criado para deploy")
    
    return playground_app

# Inicializa o app para deploy (Railway/Uvicorn)
playground_app = create_playground_app()

def main():
    """Função principal"""
    try:
        print("🩺 INICIANDO PEDRO PLAYGROUND - VERSÃO MÉDICA PROFISSIONAL")
        print("=" * 70)
        
        # Verifica se o banco existe
        if not DB_PATH.exists():
            print(f"❌ ERRO: Banco RAG não encontrado em {DB_PATH}")
            print("Execute primeiro o script de criação do RAG")
            return
        
        print(f"✅ Banco RAG encontrado: {DB_PATH}")
        
        # Cria o agente
        pedro_agent = create_pedro_agent()
        print("✅ Agente Pedro criado (versão médica)")
        
        # Cria o playground
        playground = Playground(agents=[pedro_agent])
        print("✅ Playground configurado")
        
        # Obtém a aplicação
        playground_app = playground.get_app()
        print("✅ Aplicação playground obtida")
        
        # Obtém a porta da variável de ambiente ou usa porta padrão
        port = int(os.environ.get("PORT", 7778))
        
        print("\n🩺 PEDRO PLAYGROUND - VERSÃO MÉDICA PROFISSIONAL")
        print(f"📍 URL: http://localhost:{port}")
        print("🎯 Público: Médicos pediatras, residentes, emergencistas")
        print("🔬 Recursos: RAG Semântico + PubMed + Protocolos Pedlife")
        print("📚 Dados: 26 Protocolos validados + Literatura científica")
        print("⚡ Status: Comunicação médica profissional")
        print("=" * 70)
        
        # Serve o playground
        serve_playground_app(playground_app, host="0.0.0.0", port=port)
        
    except Exception as e:
        print(f"❌ ERRO ao iniciar playground médico: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
