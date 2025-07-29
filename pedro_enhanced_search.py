#!/usr/bin/env python3
"""
Sistema de Busca Aprimorado para o Pedro
Inclui normalização, sinônimos, busca fuzzy e validação inteligente
"""

import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher

class PedroEnhancedSearch:
    """Sistema de busca aprimorado com normalização e sinônimos"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.medical_synonyms = self._load_medical_synonyms()
        
    def _load_medical_synonyms(self) -> Dict[str, List[str]]:
        """Carrega dicionário de sinônimos médicos"""
        return {
            # Analgésicos
            'paracetamol': ['acetaminophen', 'tylenol', 'panadol'],
            'ibuprofeno': ['ibuprofen', 'advil', 'brufen', 'nurofen'],
            'dipirona': ['metamizol', 'novalgina'],
            
            # Sedativos/Ansiolíticos
            'midazolam': ['dormicum', 'versed'],
            'diazepam': ['valium', 'dienpax'],
            'lorazepam': ['ativan', 'lorax'],
            
            # Antibióticos
            'amoxicilina': ['amoxicillin', 'amoxil'],
            'ceftriaxona': ['ceftriaxone', 'rocephin'],
            'azitromicina': ['azithromycin', 'zitromax'],
            
            # Broncodilatadores
            'salbutamol': ['albuterol', 'ventolin', 'aerolin'],
            'fenoterol': ['berotec'],
            
            # Corticoides
            'prednisolona': ['prednisolone', 'prelone'],
            'dexametasona': ['dexamethasone', 'decadron'],
            'hidrocortisona': ['hydrocortisone', 'cortef'],
            
            # Emergência
            'adrenalina': ['epinefrina', 'epinephrine', 'adrenaline'],
            'noradrenalina': ['norepinephrine', 'noradrenaline'],
            
            # Anticonvulsivantes
            'fenitoina': ['phenytoin', 'hidantal'],
            'carbamazepina': ['carbamazepine', 'tegretol'],
            
            # Condições clínicas
            'asma': ['asthma', 'broncoespasmo'],
            'pneumonia': ['pneumonia', 'pnm'],
            'bronquiolite': ['bronchiolitis', 'vsr'],
            'celulite': ['cellulitis', 'infeccao pele'],
            'meningite': ['meningitis'],
            'convulsao': ['seizure', 'epilepsia', 'crise convulsiva'],
            'anafilaxia': ['anaphylaxis', 'choque anafilatico'],
            'desidratacao': ['dehydration'],
            'cetoacidose': ['ketoacidosis', 'cad'],
            
            # Escalas e scores
            'glasgow': ['gcs', 'escala coma'],
            'apgar': ['score apgar'],
            'pews': ['pediatric early warning'],
            
            # Vias de administração
            'endovenoso': ['iv', 'intravenous', 'venoso'],
            'intramuscular': ['im', 'muscular'],
            'subcutaneo': ['sc', 'subcutaneous'],
            'oral': ['po', 'via oral'],
            'inalatorio': ['nebulizacao', 'aerossol']
        }
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto removendo acentos e convertendo para minúsculas"""
        if not text:
            return ""
        
        # Remove acentos
        text = unicodedata.normalize('NFD', text)
        text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
        
        # Converte para minúsculas
        text = text.lower()
        
        # Remove caracteres especiais, mantém apenas letras, números e espaços
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Remove espaços múltiplos
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def expand_query_with_synonyms(self, query: str) -> List[str]:
        """Expande query com sinônimos médicos"""
        normalized_query = self.normalize_text(query)
        query_terms = normalized_query.split()
        
        expanded_terms = set(query_terms)  # Termos originais
        
        # Adiciona sinônimos
        for term in query_terms:
            if term in self.medical_synonyms:
                expanded_terms.update(self.medical_synonyms[term])
                
        # Também verifica se o termo é sinônimo de algo
        for main_term, synonyms in self.medical_synonyms.items():
            if term in synonyms:
                expanded_terms.add(main_term)
                expanded_terms.update(synonyms)
        
        return list(expanded_terms)
    
    def fuzzy_match_score(self, term1: str, term2: str, threshold: float = 0.8) -> float:
        """Calcula score de similaridade entre dois termos"""
        return SequenceMatcher(None, term1.lower(), term2.lower()).ratio()
    
    def enhanced_search(self, query: str, limit: int = 5) -> List[Dict]:
        """Busca aprimorada com normalização, sinônimos e ranking"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Expande query com sinônimos
            expanded_terms = self.expand_query_with_synonyms(query)
            
            print(f"🔍 Query original: '{query}'")
            print(f"🔄 Termos expandidos: {expanded_terms[:10]}...")  # Mostra primeiros 10
            
            # Busca com termos expandidos
            results = []
            for term in expanded_terms:
                cursor.execute("""
                    SELECT c.chunk_text, c.semantic_tags, c.keywords, d.filename, c.id
                    FROM semantic_chunks c
                    JOIN documents d ON c.document_id = d.id
                    WHERE LOWER(c.chunk_text) LIKE ?
                    LIMIT ?
                """, [f'%{term.lower()}%', limit])
                
                chunk_results = cursor.fetchall()
                for result in chunk_results:
                    chunk_text, tags, keywords, filename, chunk_id = result
                    
                    # Calcula score de relevância
                    relevance_score = self._calculate_relevance_score(
                        query, chunk_text, term, expanded_terms
                    )
                    
                    results.append({
                        'chunk_text': chunk_text,
                        'semantic_tags': tags,
                        'keywords': keywords,
                        'filename': filename,
                        'chunk_id': chunk_id,
                        'matched_term': term,
                        'relevance_score': relevance_score,
                        'confidence': self._calculate_confidence(chunk_text, expanded_terms)
                    })
            
            # Remove duplicatas baseado no chunk_id
            unique_results = {}
            for result in results:
                chunk_id = result['chunk_id']
                if chunk_id not in unique_results or result['relevance_score'] > unique_results[chunk_id]['relevance_score']:
                    unique_results[chunk_id] = result
            
            # Ordena por relevância e retorna top resultados
            final_results = sorted(unique_results.values(), 
                                 key=lambda x: x['relevance_score'], 
                                 reverse=True)[:limit]
            
            conn.close()
            
            print(f"✅ Encontrados {len(final_results)} chunks únicos")
            for i, result in enumerate(final_results, 1):
                print(f"   {i}. {result['filename']} (score: {result['relevance_score']:.2f}, confiança: {result['confidence']:.2f})")
            
            return final_results
            
        except Exception as e:
            print(f"❌ Erro na busca aprimorada: {e}")
            return []
    
    def _calculate_relevance_score(self, original_query: str, chunk_text: str, 
                                 matched_term: str, all_terms: List[str]) -> float:
        """Calcula score de relevância do chunk"""
        score = 0.0
        normalized_chunk = self.normalize_text(chunk_text)
        normalized_query = self.normalize_text(original_query)
        
        # Score base por termo encontrado
        if matched_term.lower() in normalized_chunk:
            score += 1.0
        
        # Bonus por múltiplos termos da query
        query_words = normalized_query.split()
        matches = sum(1 for word in query_words if word in normalized_chunk)
        score += matches * 0.5
        
        # Bonus por contexto médico (palavras-chave específicas)
        medical_context_words = ['dose', 'mg/kg', 'administrar', 'tratamento', 'terapia', 'protocolo']
        context_matches = sum(1 for word in medical_context_words if word in normalized_chunk)
        score += context_matches * 0.3
        
        # Penalty por chunks muito curtos ou muito longos
        chunk_length = len(chunk_text)
        if chunk_length < 50:
            score *= 0.7  # Chunk muito curto
        elif chunk_length > 2000:
            score *= 0.8  # Chunk muito longo
        
        return score
    
    def _calculate_confidence(self, chunk_text: str, terms: List[str]) -> float:
        """Calcula confiança da informação no chunk"""
        confidence = 0.5  # Base
        normalized_chunk = self.normalize_text(chunk_text)
        
        # Indicadores de alta confiança
        high_confidence_indicators = [
            'protocolo', 'diretriz', 'recomendacao', 'dose', 'mg/kg', 
            'administrar', 'via', 'intervalo', 'posologia'
        ]
        
        confidence_boost = sum(0.1 for indicator in high_confidence_indicators 
                             if indicator in normalized_chunk)
        confidence += confidence_boost
        
        # Limita entre 0 e 1
        return min(1.0, confidence)
    
    def validate_clinical_response(self, query: str, results: List[Dict]) -> Dict:
        """Valida se a resposta é clinicamente relevante"""
        if not results:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'reason': 'Nenhum resultado encontrado'
            }
        
        # Verifica se pelo menos um resultado tem alta relevância
        high_relevance_results = [r for r in results if r['relevance_score'] >= 1.0]
        
        if not high_relevance_results:
            return {
                'is_valid': False,
                'confidence': 0.3,
                'reason': 'Resultados com baixa relevância'
            }
        
        # Calcula confiança média
        avg_confidence = sum(r['confidence'] for r in high_relevance_results) / len(high_relevance_results)
        
        return {
            'is_valid': True,
            'confidence': avg_confidence,
            'reason': f'{len(high_relevance_results)} resultado(s) de alta relevância encontrado(s)',
            'best_result': high_relevance_results[0]
        }
    
    def format_clinical_response(self, query: str, results: List[Dict], validation: Dict) -> str:
        """Formata resposta clínica aprimorada"""
        if not validation['is_valid']:
            return f"""**CONSULTA PEDLIFE - DADOS INSUFICIENTES**

**Query:** {query}
**Status:** {validation['reason']}
**Confiança:** {validation['confidence']:.1%}

**Recomendação:** Tentar pubmed_search para literatura científica complementar."""

        best_result = validation['best_result']
        
        response_parts = [
            f"**PROTOCOLOS PEDLIFE - RESPOSTA VALIDADA**",
            f"",
            f"**Query:** {query}",
            f"**Confiança:** {validation['confidence']:.1%}",
            f"**Fonte:** {best_result['filename']}",
            f"**Termo encontrado:** {best_result['matched_term']}",
            f"",
            f"**DADOS CLÍNICOS:**",
            f"{best_result['chunk_text'][:500]}{'...' if len(best_result['chunk_text']) > 500 else ''}",
            f"",
            f"**METADADOS:**",
            f"• **Tags semânticas:** {best_result['semantic_tags']}",
            f"• **Palavras-chave:** {best_result['keywords']}",
            f"• **Score de relevância:** {best_result['relevance_score']:.2f}",
            f"",
            f"---",
            f"**FONTE:** Protocolos Pedlife validados",
            f"**VALIDAÇÃO:** Sistema de busca aprimorado com sinônimos médicos"
        ]
        
        return "\n".join(response_parts)

def test_enhanced_search():
    """Testa o sistema de busca aprimorado"""
    db_path = "data/enhanced_rag.db"
    
    if not Path(db_path).exists():
        print("❌ Banco RAG não encontrado!")
        return
    
    enhanced_search = PedroEnhancedSearch(db_path)
    
    # Testes com medicamentos que falharam antes
    test_queries = [
        "ibuprofeno dose pediatrica",
        "midazolam sedacao",
        "diazepam convulsao",
        "adrenalina anafilaxia",
        "salbutamol asma",
        "prednisolona corticoide"
    ]
    
    print("🧪 TESTANDO SISTEMA DE BUSCA APRIMORADO")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Testando: '{query}'")
        print("-" * 40)
        
        results = enhanced_search.enhanced_search(query, limit=3)
        validation = enhanced_search.validate_clinical_response(query, results)
        
        if validation['is_valid']:
            print(f"✅ SUCESSO - Confiança: {validation['confidence']:.1%}")
            print(f"   Melhor resultado: {validation['best_result']['filename']}")
        else:
            print(f"❌ FALHA - {validation['reason']}")

if __name__ == "__main__":
    test_enhanced_search()
