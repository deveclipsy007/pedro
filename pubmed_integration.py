"""
🔬 INTEGRAÇÃO PUBMED PARA O AGENTE PEDRO
Consulta inteligente à base científica quando o RAG local não tem informação suficiente
"""

import requests
import json
import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
import os
from dataclasses import dataclass
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PubMedArticle:
    """Estrutura para armazenar dados de um artigo do PubMed"""
    pubmed_id: str
    title: str
    abstract: str
    journal: str
    doi: str
    issn: str
    authors: List[str]
    publication_date: str
    relevance_score: float = 0.0

class PubMedAPI:
    """
    🔬 CLIENTE PARA API DO PUBMED
    
    Funcionalidades:
    - Busca por termos médicos
    - Obtenção de abstracts completos
    - Rate limiting automático
    - Validação de relevância
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa cliente PubMed
        
        Args:
            api_key: Chave da API (opcional, mas recomendada para 10 req/s)
        """
        self.api_key = api_key or os.getenv('PUBMED_API_KEY', '')
        self.base_search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        self.base_fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        self.last_request_time = 0
        self.min_interval = 0.1  # 100ms entre requests (10 req/s max)
        
        logger.info(f"🔬 PubMed API inicializada {'com' if self.api_key else 'sem'} API key")
    
    def _rate_limit(self):
        """Aplica rate limiting para respeitar limites da API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_articles(self, query: str, max_results: int = 5) -> List[str]:
        """
        🔍 BUSCA ARTIGOS POR TERMO MÉDICO
        
        Args:
            query: Termo de busca médico
            max_results: Máximo de resultados
            
        Returns:
            Lista de PubMed IDs encontrados
        """
        try:
            self._rate_limit()
            
            params = {
                'db': 'pubmed',
                'retmode': 'json',
                'retmax': max_results,
                'term': query,
                'sort': 'relevance'  # Ordenar por relevância
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            logger.info(f"🔍 Buscando no PubMed: '{query}'")
            response = requests.get(self.base_search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pubmed_ids = data.get('esearchresult', {}).get('idlist', [])
            
            logger.info(f"📊 Encontrados {len(pubmed_ids)} artigos para '{query}'")
            return pubmed_ids
            
        except Exception as e:
            logger.error(f"❌ Erro na busca PubMed: {e}")
            return []
    
    def fetch_article_details(self, pubmed_id: str) -> Optional[PubMedArticle]:
        """
        📄 OBTÉM DETALHES COMPLETOS DE UM ARTIGO
        
        Args:
            pubmed_id: ID do artigo no PubMed
            
        Returns:
            Objeto PubMedArticle com dados completos ou None se erro
        """
        try:
            self._rate_limit()
            
            params = {
                'db': 'pubmed',
                'id': pubmed_id,
                'rettype': 'abstract',
                'retmode': 'xml'
            }
            
            if self.api_key:
                params['api_key'] = self.api_key
            
            response = requests.get(self.base_fetch_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Extrair dados do XML
            article_data = self._parse_article_xml(root, pubmed_id)
            
            if article_data:
                logger.info(f"📄 Artigo {pubmed_id} obtido com sucesso")
                return article_data
            else:
                logger.warning(f"⚠️ Dados insuficientes para artigo {pubmed_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro ao obter artigo {pubmed_id}: {e}")
            return None
    
    def _parse_article_xml(self, root: ET.Element, pubmed_id: str) -> Optional[PubMedArticle]:
        """
        🔧 PARSE DOS DADOS XML DO ARTIGO
        
        Args:
            root: Elemento raiz do XML
            pubmed_id: ID do artigo
            
        Returns:
            PubMedArticle com dados extraídos
        """
        try:
            # Título
            title_elem = root.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "Título não disponível"
            
            # Abstract
            abstract_elem = root.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else "Abstract não disponível"
            
            # Journal
            journal_elem = root.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "Journal não informado"
            
            # DOI
            doi_elem = root.find('.//ELocationID[@EIdType="doi"]')
            doi = doi_elem.text if doi_elem is not None else ""
            
            # ISSN
            issn_elem = root.find('.//ISSN')
            issn = issn_elem.text if issn_elem is not None else ""
            
            # Autores
            authors = []
            for author_elem in root.findall('.//Author'):
                lastname = author_elem.find('LastName')
                firstname = author_elem.find('ForeName')
                if lastname is not None and firstname is not None:
                    authors.append(f"{firstname.text} {lastname.text}")
            
            # Data de publicação
            pub_date_elem = root.find('.//PubDate/Year')
            pub_date = pub_date_elem.text if pub_date_elem is not None else "Data não informada"
            
            return PubMedArticle(
                pubmed_id=pubmed_id,
                title=title,
                abstract=abstract,
                journal=journal,
                doi=doi,
                issn=issn,
                authors=authors,
                publication_date=pub_date
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no parse XML: {e}")
            return None
    
    def intelligent_search(self, medical_query: str, max_articles: int = 3) -> List[PubMedArticle]:
        """
        🧠 BUSCA INTELIGENTE COM VALIDAÇÃO DE RELEVÂNCIA
        
        Args:
            medical_query: Query médica para buscar
            max_articles: Máximo de artigos a retornar
            
        Returns:
            Lista de artigos relevantes ordenados por relevância
        """
        logger.info(f"🧠 Iniciando busca inteligente PubMed: '{medical_query}'")
        
        # 1. Buscar IDs dos artigos
        pubmed_ids = self.search_articles(medical_query, max_articles * 2)
        
        if not pubmed_ids:
            logger.warning("⚠️ Nenhum artigo encontrado no PubMed")
            return []
        
        # 2. Obter detalhes dos artigos
        articles = []
        for pubmed_id in pubmed_ids[:max_articles]:
            article = self.fetch_article_details(pubmed_id)
            if article:
                # Calcular score de relevância básico
                article.relevance_score = self._calculate_relevance(article, medical_query)
                articles.append(article)
        
        # 3. Ordenar por relevância
        articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        logger.info(f"📊 Retornando {len(articles)} artigos relevantes")
        return articles
    
    def _calculate_relevance(self, article: PubMedArticle, query: str) -> float:
        """
        📊 CALCULA SCORE DE RELEVÂNCIA SIMPLES
        
        Args:
            article: Artigo para avaliar
            query: Query original
            
        Returns:
            Score de relevância (0-1)
        """
        query_terms = query.lower().split()
        text_to_search = f"{article.title} {article.abstract}".lower()
        
        matches = sum(1 for term in query_terms if term in text_to_search)
        relevance = matches / len(query_terms) if query_terms else 0
        
        return min(relevance, 1.0)

class PedroWithPubMed:
    """
    🤖 PEDRO COM INTEGRAÇÃO PUBMED
    
    Combina RAG local com consulta científica externa quando necessário
    """
    
    def __init__(self, pubmed_api_key: Optional[str] = None):
        """
        Inicializa Pedro com capacidade PubMed
        
        Args:
            pubmed_api_key: Chave da API PubMed (opcional)
        """
        self.pubmed = PubMedAPI(pubmed_api_key)
        logger.info("🤖 Pedro com PubMed inicializado")
    
    def should_consult_pubmed(self, rag_response: str, confidence_threshold: float = 0.7) -> bool:
        """
        🤔 DECIDE SE DEVE CONSULTAR PUBMED
        
        Critérios:
        - Resposta do RAG muito genérica
        - Baixa confiança na resposta
        - Menção explícita de falta de informação
        
        Args:
            rag_response: Resposta do RAG local
            confidence_threshold: Limite de confiança
            
        Returns:
            True se deve consultar PubMed
        """
        # Indicadores de baixa qualidade/confiança
        low_confidence_indicators = [
            "não tenho informação",
            "não encontrei",
            "não sei",
            "não está disponível",
            "informação insuficiente",
            "dados limitados",
            "não há dados específicos"
        ]
        
        rag_lower = rag_response.lower()
        
        # Verificar indicadores de baixa confiança
        has_low_confidence = any(indicator in rag_lower for indicator in low_confidence_indicators)
        
        # Verificar se resposta é muito curta (pode ser genérica)
        is_too_short = len(rag_response.split()) < 20
        
        should_consult = has_low_confidence or is_too_short
        
        if should_consult:
            logger.info("🤔 RAG local insuficiente, consultando PubMed...")
        
        return should_consult
    
    def enhanced_clinical_search(self, query: str, rag_response: str = "") -> Dict:
        """
        🔬 BUSCA CLÍNICA APRIMORADA COM PUBMED
        
        Args:
            query: Query clínica
            rag_response: Resposta do RAG local (opcional)
            
        Returns:
            Dicionário com resposta combinada e fontes
        """
        result = {
            'query': query,
            'rag_response': rag_response,
            'pubmed_consulted': False,
            'pubmed_articles': [],
            'final_response': rag_response,
            'sources': ['RAG Pedlife']
        }
        
        # Decidir se deve consultar PubMed
        if self.should_consult_pubmed(rag_response):
            logger.info("🔬 Consultando PubMed para informação adicional...")
            
            # Buscar artigos relevantes
            articles = self.pubmed.intelligent_search(query, max_articles=3)
            
            if articles:
                result['pubmed_consulted'] = True
                result['pubmed_articles'] = articles
                result['sources'].append('PubMed')
                
                # Combinar resposta RAG com evidências PubMed
                pubmed_summary = self._create_pubmed_summary(articles)
                result['final_response'] = self._combine_responses(rag_response, pubmed_summary)
                
                logger.info(f"✅ Resposta enriquecida com {len(articles)} artigos PubMed")
            else:
                logger.warning("⚠️ Nenhum artigo relevante encontrado no PubMed")
        
        return result
    
    def _create_pubmed_summary(self, articles: List[PubMedArticle]) -> str:
        """
        📝 CRIA RESUMO DOS ARTIGOS PUBMED
        
        Args:
            articles: Lista de artigos PubMed
            
        Returns:
            Resumo formatado dos artigos
        """
        if not articles:
            return ""
        
        summary_parts = ["\n🔬 **EVIDÊNCIAS CIENTÍFICAS ADICIONAIS (PubMed):**\n"]
        
        for i, article in enumerate(articles, 1):
            summary_parts.append(f"**{i}. {article.title}**")
            summary_parts.append(f"   📄 *{article.journal}* ({article.publication_date})")
            
            if article.doi:
                summary_parts.append(f"   🔗 DOI: {article.doi}")
            
            # Resumo do abstract (primeiras 200 palavras)
            abstract_preview = article.abstract[:400] + "..." if len(article.abstract) > 400 else article.abstract
            summary_parts.append(f"   📋 **Resumo:** {abstract_preview}")
            
            if article.authors:
                authors_str = ", ".join(article.authors[:3])
                if len(article.authors) > 3:
                    authors_str += f" et al. ({len(article.authors)} autores)"
                summary_parts.append(f"   👥 **Autores:** {authors_str}")
            
            summary_parts.append(f"   📊 **Relevância:** {article.relevance_score:.2f}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def _combine_responses(self, rag_response: str, pubmed_summary: str) -> str:
        """
        🔄 COMBINA RESPOSTA RAG COM EVIDÊNCIAS PUBMED
        
        Args:
            rag_response: Resposta do RAG local
            pubmed_summary: Resumo dos artigos PubMed
            
        Returns:
            Resposta combinada e estruturada
        """
        if not pubmed_summary:
            return rag_response
        
        combined = []
        
        # Resposta do RAG local
        if rag_response and len(rag_response.strip()) > 10:
            combined.append("📚 **INFORMAÇÃO DOS PROTOCOLOS PEDLIFE:**")
            combined.append(rag_response)
            combined.append("")
        
        # Evidências PubMed
        combined.append(pubmed_summary)
        
        # Disclaimer
        combined.append("---")
        combined.append("⚠️ **IMPORTANTE:** As informações do PubMed são complementares aos protocolos Pedlife. Sempre consulte diretrizes locais e supervisão médica adequada.")
        
        return "\n".join(combined)

# Função de conveniência para uso direto
def search_pubmed_if_needed(query: str, rag_response: str = "", api_key: str = None) -> Dict:
    """
    🚀 FUNÇÃO DE CONVENIÊNCIA PARA BUSCA PUBMED
    
    Args:
        query: Query clínica
        rag_response: Resposta do RAG (opcional)
        api_key: Chave da API PubMed (opcional)
        
    Returns:
        Resultado da busca combinada
    """
    pedro_pubmed = PedroWithPubMed(api_key)
    return pedro_pubmed.enhanced_clinical_search(query, rag_response)

if __name__ == "__main__":
    # Teste básico
    print("🔬 Testando integração PubMed...")
    
    # Exemplo de uso
    test_query = "midazolam pediatric sedation dosage"
    test_rag_response = "Não tenho informação específica sobre essa dosagem."
    
    result = search_pubmed_if_needed(test_query, test_rag_response)
    
    print(f"Query: {result['query']}")
    print(f"PubMed consultado: {result['pubmed_consulted']}")
    print(f"Artigos encontrados: {len(result['pubmed_articles'])}")
    print(f"Fontes: {result['sources']}")
