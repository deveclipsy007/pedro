# Requirements Document

## Introduction

Este documento define os requisitos para integrar completamente o agente Pedro com o pipeline RAG, garantindo que ele use embeddings vetoriais em vez do índice simples atual, e que o pipeline RAG seja executado corretamente.

## Requirements

### Requirement 1

**User Story:** Como desenvolvedor, eu quero que o Pedro use o pipeline RAG completo com embeddings vetoriais, para que ele forneça respostas mais precisas baseadas em similaridade semântica.

#### Acceptance Criteria

1. WHEN Pedro recebe uma pergunta médica THEN ele DEVE gerar embedding da query usando OpenAI
2. WHEN Pedro busca informações THEN ele DEVE consultar a vector_store usando similaridade de embeddings
3. WHEN Pedro retorna resultados THEN ele DEVE usar a melhor estratégia de chunking selecionada automaticamente
4. IF não há dados na vector_store THEN Pedro DEVE executar o pipeline RAG automaticamente
5. WHEN Pedro calcula dosagens THEN ele DEVE primeiro consultar o RAG para informações do medicamento

### Requirement 2

**User Story:** Como administrador do sistema, eu quero que o pipeline RAG seja executado corretamente, para que os dados médicos sejam processados e indexados adequadamente.

#### Acceptance Criteria

1. WHEN o sistema inicia THEN ele DEVE carregar as variáveis de ambiente do arquivo .env.test
2. WHEN o pipeline é executado THEN ele DEVE processar todos os arquivos .md em data/raw/
3. WHEN o processamento termina THEN ele DEVE gerar embeddings para todos os chunks
4. WHEN a avaliação é executada THEN ela DEVE selecionar a melhor estratégia de chunking
5. IF há falhas no pipeline THEN o sistema DEVE registrar logs detalhados

### Requirement 3

**User Story:** Como usuário do Pedro, eu quero que as respostas sejam baseadas exclusivamente nos protocolos médicos processados, para que eu tenha informações confiáveis e atualizadas.

#### Acceptance Criteria

1. WHEN Pedro responde sobre medicamentos THEN ele DEVE citar a fonte específica do protocolo
2. WHEN não há informações no RAG THEN Pedro DEVE informar claramente a ausência de dados
3. WHEN Pedro fornece dosagens THEN ele DEVE incluir alertas de segurança dos protocolos
4. IF há múltiplas fontes relevantes THEN Pedro DEVE priorizar por relevância semântica
5. WHEN Pedro processa uma query THEN ele DEVE usar apenas informações dos documentos indexados

### Requirement 4

**User Story:** Como desenvolvedor, eu quero que o sistema seja facilmente configurável e monitorável, para que eu possa manter e atualizar o pipeline RAG eficientemente.

#### Acceptance Criteria

1. WHEN o sistema inicia THEN ele DEVE validar todas as configurações necessárias
2. WHEN há erros de configuração THEN o sistema DEVE fornecer mensagens claras de diagnóstico
3. WHEN o pipeline é executado THEN ele DEVE gerar métricas de performance
4. IF há atualizações nos documentos THEN o sistema DEVE reprocessar automaticamente
5. WHEN há falhas THEN o sistema DEVE permitir reexecução de etapas específicas

### Requirement 5

**User Story:** Como usuário final, eu quero que o Pedro responda rapidamente e com alta qualidade, para que eu possa obter informações médicas de forma eficiente.

#### Acceptance Criteria

1. WHEN Pedro recebe uma query THEN ele DEVE responder em menos de 5 segundos
2. WHEN Pedro busca informações THEN ele DEVE retornar os 3 chunks mais relevantes
3. WHEN há informações relacionadas THEN Pedro DEVE incluir contexto adicional relevante
4. IF a query é ambígua THEN Pedro DEVE solicitar esclarecimentos específicos
5. WHEN Pedro fornece informações THEN ele DEVE incluir nível de confiança da resposta