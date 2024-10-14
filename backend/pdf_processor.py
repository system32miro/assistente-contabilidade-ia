import pdfplumber
import re
import logging
from datetime import datetime
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

def extrair_texto_pdf(caminho_pdf):
    logging.info(f"A extrair texto do PDF: {caminho_pdf}")
    try:
        verificar_pdf_protegido(caminho_pdf)
        texto = extrair_texto_pdfplumber(caminho_pdf)
        texto = pre_processar_texto(texto)
        logging.info("Texto extraído e pré-processado com sucesso")
        return texto
    except Exception as e:
        erro = f"Erro ao extrair texto do PDF: {str(e)}"
        logging.error(erro)
        return erro

def verificar_pdf_protegido(caminho_pdf):
    with open(caminho_pdf, 'rb') as file:
        pdf = PdfReader(file)
        if pdf.is_encrypted:
            raise ValueError("O PDF está protegido por senha.")

def extrair_texto_pdfplumber(caminho_pdf):
    texto = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        if len(pdf.pages) == 0:
            raise ValueError("O PDF não contém páginas.")
        
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += texto_pagina
            else:
                logging.warning(f"Não foi possível extrair texto da página {pagina.page_number}.")

    if not texto:
        raise ValueError("Não foi possível extrair texto de nenhuma página do PDF.")
    
    return texto

def pre_processar_texto(texto):
    texto = remover_cabecalho_rodape(texto)
    texto = remover_caracteres_especiais(texto)
    texto = normalizar_datas(texto)
    texto = padronizar_moeda(texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def remover_cabecalho_rodape(texto):
    texto = re.sub(r'^.*\n', '', texto)  # Remove a primeira linha (cabeçalho)
    texto = re.sub(r'\n.*$', '', texto)  # Remove a última linha (rodapé)
    return texto

def remover_caracteres_especiais(texto):
    texto = re.sub(r'[^\x00-\x7F]+', '', texto)  # Remove caracteres não-ASCII
    texto = re.sub(r'[^\w\s.,€$%/-]', '', texto)  # Remove caracteres especiais exceto pontuação comum e símbolos monetários
    return texto

def normalizar_datas(texto):
    texto = re.sub(r'(\d{2})[/.](\d{2})[/.](\d{4})', r'\1-\2-\3', texto)
    texto = re.sub(r'(\d{1})[/.](\d{2})[/.](\d{4})', r'0\1-\2-\3', texto)
    texto = re.sub(r'(\d{2})[/.](\d{1})[/.](\d{4})', r'\1-0\2-\3', texto)
    return texto

def padronizar_moeda(texto):
    def format_currency(match):
        value = match.group(1).replace(',', '.')
        return f"{float(value):.2f}€"
    
    return re.sub(r'(\d+(?:[.,]\d+)?)\s*€', format_currency, texto)

def validar_pdf(caminho_pdf):
    if not caminho_pdf.lower().endswith('.pdf'):
        return False
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            return len(pdf.pages) > 0
    except Exception:
        return False

def detect_invoice_layout(texto):
    layout_info = inicializar_layout_info()
    layout_info = detectar_tipo_documento(texto, layout_info)
    layout_info = detectar_numero_fatura(texto, layout_info)
    layout_info = detectar_nif(texto, layout_info)
    layout_info = detectar_data_emissao(texto, layout_info)
    layout_info = detectar_valores(texto, layout_info)
    return layout_info

def inicializar_layout_info():
    return {
        "tipo_documento": None,
        "numero_fatura": None,
        "nif_emissor": None,
        "nif_cliente": None,
        "data_emissao": None,
        "total": None,
        "iva": None
    }

def detectar_tipo_documento(texto, layout_info):
    if re.search(r'\b(?:Fatura|Factura)\b', texto, re.IGNORECASE):
        layout_info["tipo_documento"] = "Fatura"
    elif re.search(r'\bRecibo\b', texto, re.IGNORECASE):
        layout_info["tipo_documento"] = "Recibo"
    return layout_info

def detectar_numero_fatura(texto, layout_info):
    numero_fatura_match = re.search(r'\b(?:Fatura|Factura|Documento)\s*[Nn]º?\s*[:.]?\s*(\w+)', texto)
    if numero_fatura_match:
        layout_info["numero_fatura"] = numero_fatura_match.group(1)
    return layout_info

def detectar_nif(texto, layout_info):
    nif_emissor_match = re.search(r'\bNIF\s*:?\s*(\d{9})\b', texto)
    if nif_emissor_match:
        layout_info["nif_emissor"] = nif_emissor_match.group(1)
    
    nif_cliente_match = re.search(r'\bNIF\s*Cliente\s*:?\s*(\d{9})\b', texto, re.IGNORECASE)
    if nif_cliente_match:
        layout_info["nif_cliente"] = nif_cliente_match.group(1)
    
    return layout_info

def detectar_data_emissao(texto, layout_info):
    data_emissao_match = re.search(r'\bData\s*(?:de\s*)?Emissão\s*:?\s*(\d{2}[-/]\d{2}[-/]\d{4})', texto, re.IGNORECASE)
    if data_emissao_match:
        layout_info["data_emissao"] = data_emissao_match.group(1)
    return layout_info

def detectar_valores(texto, layout_info):
    total_match = re.search(r'\bTotal\s*(?:a\s*Pagar)?\s*:?\s*[€]?\s*([\d.,]+)', texto, re.IGNORECASE)
    if total_match:
        layout_info["total"] = total_match.group(1)
    
    iva_match = re.search(r'\bIVA\s*:?\s*[€]?\s*([\d.,]+)', texto, re.IGNORECASE)
    if iva_match:
        layout_info["iva"] = iva_match.group(1)
    
    return layout_info

def extrair_itens_fatura(texto_fatura):
    padrao_item = r'(\d+)\s+(.*?)\s+([\d.,]+)\s*€?\s+([\d.,]+)%?\s+([\d.,]+)\s*€?'
    correspondencias = re.finditer(padrao_item, texto_fatura, re.MULTILINE)
    
    return [criar_item_fatura(match) for match in correspondencias]

def criar_item_fatura(match):
    return {
        "quantidade": match.group(1),
        "descricao": match.group(2).strip(),
        "preco_unitario": match.group(3),
        "iva": match.group(4),
        "total": match.group(5)
    }

def extrair_dados_estruturados(texto, layout):
    dados = inicializar_dados_estruturados(layout)
    dados = extrair_nomes(texto, dados)
    dados["items"] = extrair_itens_fatura(texto)
    dados = extrair_metodo_pagamento(texto, dados)
    dados = extrair_data_vencimento(texto, dados)
    dados = processar_datas(dados)
    dados = processar_valores_monetarios(dados)
    return dados

def inicializar_dados_estruturados(layout):
    return {
        "tipo_documento": layout["tipo_documento"],
        "numero_fatura": layout["numero_fatura"],
        "nif_emissor": layout["nif_emissor"],
        "nif_cliente": layout["nif_cliente"],
        "data_emissao": layout["data_emissao"],
        "total": layout["total"],
        "iva": layout["iva"],
        "nome_emissor": None,
        "nome_cliente": None,
        "items": [],
        "metodo_pagamento": None,
        "data_vencimento": None
    }

def extrair_nomes(texto, dados):
    nome_emissor_match = re.search(r'^(.*?)\n', texto)
    if nome_emissor_match:
        dados["nome_emissor"] = nome_emissor_match.group(1).strip()

    nome_cliente_match = re.search(r'(?:Cliente|Destinatário):\s*(.*?)\n', texto, re.IGNORECASE)
    if nome_cliente_match:
        dados["nome_cliente"] = nome_cliente_match.group(1).strip()
    
    return dados

def extrair_metodo_pagamento(texto, dados):
    metodo_pagamento_match = re.search(r'Método de Pagamento:\s*(.*?)\n', texto, re.IGNORECASE)
    if metodo_pagamento_match:
        dados["metodo_pagamento"] = metodo_pagamento_match.group(1).strip()
    return dados

def extrair_data_vencimento(texto, dados):
    data_vencimento_match = re.search(r'Data de Vencimento:\s*(\d{2}-\d{2}-\d{4})', texto, re.IGNORECASE)
    if data_vencimento_match:
        dados["data_vencimento"] = data_vencimento_match.group(1)
    return dados

def processar_datas(dados):
    if dados["data_emissao"]:
        dados["data_emissao"] = formatar_data(dados["data_emissao"])
    if dados["data_vencimento"]:
        dados["data_vencimento"] = formatar_data(dados["data_vencimento"])
    return dados

def processar_valores_monetarios(dados):
    dados["total"] = formatar_valor_monetario(dados["total"])
    dados["iva"] = formatar_valor_monetario(dados["iva"])
    for item in dados["items"]:
        item["preco_unitario"] = formatar_valor_monetario(item["preco_unitario"])
        item["total"] = formatar_valor_monetario(item["total"])
    return dados

def formatar_data(data_str):
    try:
        return datetime.strptime(data_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return data_str

def formatar_valor_monetario(valor_str):
    if valor_str:
        valor_str = valor_str.replace('.', '').replace(',', '.')
        try:
            return f"{float(valor_str):.2f}"
        except ValueError:
            return valor_str
    return None