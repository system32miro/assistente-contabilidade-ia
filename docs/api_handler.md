# Módulo API Handler

## Visão Geral
O módulo `api_handler.py` é responsável por gerir as interações com a API Groq, utilizada para gerar respostas baseadas em IA para consultas contabilísticas.

## Funções Principais

### gerar_resposta(mensagens: list) -> str
Gera uma resposta da API Groq com base nas mensagens fornecidas.

**Parâmetros:**
- `mensagens`: Lista de dicionários contendo as mensagens da conversa.

**Retorna:**
- A resposta gerada pela API ou uma mensagem de erro.

**Exemplo de uso:**