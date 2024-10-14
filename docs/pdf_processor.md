# Módulo PDF Processor

## Visão Geral
O módulo `pdf_processor.py` é responsável por extrair e processar informações de faturas em formato PDF. Ele utiliza bibliotecas como `pdfplumber` e `PyPDF2` para realizar a extração de texto e implementa várias funções para analisar e estruturar os dados extraídos.

## Funções Principais

### extrair_texto_pdf(caminho_pdf: str) -> str
Extrai o texto completo de um arquivo PDF.

**Parâmetros:**
- `caminho_pdf`: Caminho para o arquivo PDF.

**Retorna:**
- Texto extraído do PDF ou uma mensagem de erro.

**Exemplo de uso:**