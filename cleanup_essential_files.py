import os
import shutil
from pathlib import Path

def cleanup_non_essential_files():
    """Remove arquivos e pastas não essenciais do projeto Pedro"""
    
    # Diretório raiz do projeto
    project_root = Path(__file__).parent
    
    # Lista de arquivos e pastas essenciais (que devem ser mantidos)
    essential_files = {
        'playground/pedro_playground_medico.py',
        'pedro_enhanced_search.py',
        'pubmed_integration.py',
        'requirements.txt',
        'render.yaml',
        '.env.render.template',
        'README.md',
        'DEPLOYMENT.md',
        'DEPLOYMENT_CHECKLIST.md',
        'GIT_COMMIT_CHECKLIST.md',
        'ESSENTIAL_FILES.md',
        '.gitignore'
    }
    
    # Lista de pastas essenciais (que devem ser mantidas)
    essential_dirs = {
        'data',
        'playground'
    }
    
    # Arquivos e pastas que podem ser removidos
    removable_items = [
        # Pastas de desenvolvimento
        '.venv',
        'venv',
        '__pycache__',
        '.pytest_cache',
        'tests',
        'agents',
        'src',
        'scripts',
        'config',
        'examples',
        'docs',
        'web',
        'docker',
        'kestra',
        'logs',
        
        # Arquivos de ambiente
        '.env',
        '.env.test',
        '.env.prod',
        '.env.test.template',
        '.env.vectorial',
        
        # Arquivos de documentação técnica detalhada
        'AGNO_INTEGRATION.md',
        'COMO_USAR_RAG.md',
        'MONITORING.md',
        'PERFORMANCE_OPTIMIZATIONS.md',
        'RAG.md',
        'RAG_ANALYSIS.md',
        'TASK_8_IMPLEMENTATION_SUMMARY.md',
        'analise_rag_pedro.md',
        'best_strategy.txt',
        'pipilinerag.md',
        'pyproject.toml',
        'relatorio_teste_pedro_20250729_062941.json',
        'requirements-dev.txt',
        
        # Scripts de desenvolvimento
        'activate_enhanced_rag.py',
        'activate_vectorial_rag.py',
        'add_pubmed_key.py',
        'analise_otimizacao_rag.py',
        'auditoria_completa_rag.py',
        'auditoria_corrigida_rag.py',
        'bateria_testes_pedro.py',
        'busca_semantica_inteligente.py',
        'cleanup_projeto_pedro.py',
        'diagnosticar_rag.py',
        'fix_asyncio_loops.py',
        'fix_pedro_rag_integration.py',
        'integrar_calculadora_pedro.py',
        'migrate_to_vectorial_rag.py',
        'pedro_fixed.py',
        'pedro_rag_corrigido.py',
        'pedro_rag_final_integrado.py',
        'pedro_simple.py',
        'perguntas_teste_rag_pedlife.py',
        'process_rag_pedlife.py',
        'simple_rag_processor.py',
        'sistema_seguranca_rag_avancado.py',
        'sistema_transparencia_rag.py',
        'solucao_calculo_dose.py',
        'test_config_basic.py',
        'test_config_setup.py',
        'test_enhanced_rag.py',
        'test_enhanced_rag_response.py',
        'test_monitoring_system.py',
        'test_pedro_after_fix.py',
        'test_pedro_agent.py',
        'test_pedro_enhanced.py',
        'test_pedro_enhanced_integration.py',
        'test_pedro_rag_integration.py',
        'test_pedro_rag_only.py',
        'test_pedro_tools.py',
        'test_pedro_vector_rag.py',
        'test_performance_optimizations.py',
        'test_pipeline_orchestrator.py',
        'test_pipeline_orchestrator_simple.py',
        'test_playground.py',
        'test_rag_integration.py',
        'test_rag_integration_simple.py',
        'test_rag_paracetamol.py',
        'test_rag_pedro.py',
        'test_vector_store_engine.py',
        'test_vector_store_engine_simple.py',
        'test_vector_store_integration.py',
        'teste_calc_dose_direto.py',
        'teste_calc_dose_integrada.py',
        'teste_deteccao_dose.py',
        'teste_pedro_cenarios_completos.py',
        'teste_pedro_completo.py',
        'teste_pedro_final.py',
        'teste_pedro_perguntas_reais.py',
        'verificar_banco.py',
        'verificar_estrutura_db.py',
        
        # Arquivos playground antigos
        'playground/pedro_playground.py',
        'playground/pedro_playground_corrigido.py',
        'playground/pedro_playground_final.py',
        'playground/pedro_playground_semantico.py',
        'playground/pedro_playground_simples.py',
        'playground/__pycache__'
    ]
    
    # Arquivos específicos na pasta data que podem ser removidos
    removable_data_items = [
        'alerts.db',
        'chunks',
        'embeddings',
        'metrics.db',
        'processed',
        'rag_test.db',
        'tests',
        'vectorial_rag.db'
    ]
    
    print("🔍 INICIANDO LIMPEZA DE ARQUIVOS NÃO ESSENCIAIS")
    print("=" * 60)
    
    # Remover arquivos e pastas da lista removable_items
    removed_count = 0
    for item in removable_items:
        item_path = project_root / item
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"✅ Removido arquivo: {item}")
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"✅ Removida pasta: {item}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Erro ao remover {item}: {e}")
    
    # Remover itens específicos da pasta data
    data_dir = project_root / 'data'
    for item in removable_data_items:
        item_path = data_dir / item
        if item_path.exists():
            try:
                if item_path.is_file():
                    item_path.unlink()
                    print(f"✅ Removido arquivo da data: {item}")
                elif item_path.is_dir():
                    shutil.rmtree(item_path)
                    print(f"✅ Removida pasta da data: {item}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Erro ao remover {item} da data: {e}")
    
    # Remover arquivos .py de teste na raiz
    test_files = list(project_root.glob('test_*.py'))
    test_files.extend(list(project_root.glob('teste_*.py')))
    
    for test_file in test_files:
        try:
            test_file.unlink()
            print(f"✅ Removido arquivo de teste: {test_file.name}")
            removed_count += 1
        except Exception as e:
            print(f"❌ Erro ao remover {test_file.name}: {e}")
    
    print("\n✅ LIMPEZA CONCLUÍDA")
    print(f"📁 Total de itens removidos: {removed_count}")
    print("\n📝 Arquivos essenciais mantidos:")
    for file in essential_files:
        print(f"  • {file}")
    
    print("\n📁 Pastas essenciais mantidas:")
    for dir in essential_dirs:
        print(f"  • {dir}")

if __name__ == "__main__":
    cleanup_non_essential_files()
