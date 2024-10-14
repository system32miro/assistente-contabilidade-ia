import datetime
from typing import List, Dict, Optional
import pdfplumber
import re
import json
import os
import logging

class ObrigacaoFiscal:
    def __init__(self, nome: str, prazo: datetime.date, descricao: str, tipo: str):
        self.nome = nome
        self.prazo = prazo
        self.descricao = descricao
        self.tipo = tipo  # 'fiscal' ou 'declarativa'

    def to_dict(self) -> Dict:
        return {
            "nome": self.nome,
            "prazo": self.prazo.isoformat(),
            "descricao": self.descricao,
            "tipo": self.tipo
        }

    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            nome=data['nome'],
            prazo=datetime.date.fromisoformat(data['prazo']),
            descricao=data['descricao'],
            tipo=data['tipo']
        )

class GestorObrigacoesFiscais:
    def __init__(self):
        self.obrigacoes: List[ObrigacaoFiscal] = []

    def adicionar_obrigacao(self, obrigacao: ObrigacaoFiscal):
        self.obrigacoes.append(obrigacao)

    def obter_obrigacoes_por_mes(self, mes: int, ano: int) -> List[ObrigacaoFiscal]:
        return [ob for ob in self.obrigacoes if ob.prazo.month == mes and ob.prazo.year == ano]

    def obter_proximas_obrigacoes(self, dias: int = 30) -> List[ObrigacaoFiscal]:
        hoje = datetime.date.today()
        limite = hoje + datetime.timedelta(days=dias)
        return [ob for ob in self.obrigacoes if hoje <= ob.prazo <= limite]

    def to_dict(self) -> Dict[str, List[Dict]]:
        return {
            "obrigacoes_fiscais": [ob.to_dict() for ob in self.obrigacoes if ob.tipo == "fiscal"],
            "obrigacoes_declarativas": [ob.to_dict() for ob in self.obrigacoes if ob.tipo == "declarativa"]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, List[Dict]]):
        gestor = cls()
        for ob_dict in data.get("obrigacoes_fiscais", []) + data.get("obrigacoes_declarativas", []):
            gestor.adicionar_obrigacao(ObrigacaoFiscal.from_dict(ob_dict))
        return gestor

def extract_pdf_content(pdf_path: str) -> str:
    texto_completo = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"
    except Exception as e:
        print(f"Erro ao extrair texto do PDF {pdf_path}: {e}")
    return texto_completo

def parse_fiscal_obligations(text: str) -> List[ObrigacaoFiscal]:
    obrigacoes = []
    linhas = text.split('\n')
    for i, linha in enumerate(linhas):
        logging.debug(f"Processando linha: {linha}")
        if re.match(r'\d{1,2}\s+de\s+[A-Za-zç]+', linha):
            data_str = linha.strip()
            if i + 1 < len(linhas):
                descricao = linhas[i + 1].strip()
                try:
                    data = datetime.datetime.strptime(data_str, "%d de %B").replace(year=2024).date()
                    obrigacoes.append(ObrigacaoFiscal("Obrigação Fiscal", data, descricao, "fiscal"))
                    logging.info(f"Obrigação fiscal adicionada: {data_str} - {descricao}")
                except ValueError as e:
                    logging.error(f"Erro ao processar data: {data_str}. Erro: {str(e)}")
    logging.info(f"Total de obrigações fiscais encontradas: {len(obrigacoes)}")
    return obrigacoes

def parse_declarative_obligations(text: str) -> List[ObrigacaoFiscal]:
    obrigacoes = []
    linhas = text.split('\n')
    for i, linha in enumerate(linhas):
        match = re.match(r'(\d{1,2})\s+de\s+([A-Za-zç]+)\s*-\s*(.+)', linha)
        if match:
            dia, mes, descricao = match.groups()
            try:
                data = datetime.datetime.strptime(f"{dia} de {mes} 2024", "%d de %B %Y").date()
                obrigacoes.append(ObrigacaoFiscal("Obrigação Declarativa", data, descricao.strip(), "declarativa"))
            except ValueError:
                print(f"Erro ao processar data: {dia} de {mes}")
    return obrigacoes

def parse_obrigacoes(texto: str) -> List[ObrigacaoFiscal]:
    obrigacoes_fiscais = parse_fiscal_obligations(texto)
    obrigacoes_declarativas = parse_declarative_obligations(texto)
    return obrigacoes_fiscais + obrigacoes_declarativas

def carregar_obrigacoes_de_arquivo(caminho_arquivo: str) -> List[ObrigacaoFiscal]:
    logging.info(f"Tentando carregar obrigações do arquivo: {caminho_arquivo}")
    texto = extract_pdf_content(caminho_arquivo)
    if not texto:
        logging.error(f"Não foi possível extrair texto do arquivo: {caminho_arquivo}")
        return []
    obrigacoes = parse_obrigacoes(texto)
    logging.info(f"Extraídas {len(obrigacoes)} obrigações do arquivo: {caminho_arquivo}")
    return obrigacoes

def formatar_data(data: datetime.date) -> str:
    return data.strftime("%d/%m/%Y")

def guardar_obrigacoes_json(gestor: GestorObrigacoesFiscais, caminho_arquivo: str):
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        json.dump(gestor.to_dict(), f, ensure_ascii=False, indent=4)

def carregar_obrigacoes_json(caminho_arquivo: str) -> GestorObrigacoesFiscais:
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return GestorObrigacoesFiscais.from_dict(data)
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado. Retornando um gestor vazio.")
        return GestorObrigacoesFiscais()

def save_obligations(obligations: GestorObrigacoesFiscais, file_path: str):
    """
    Salva as obrigações fiscais e declarativas em um arquivo JSON.
    
    :param obligations: Instância de GestorObrigacoesFiscais contendo as obrigações.
    :param file_path: Caminho do arquivo onde as obrigações serão salvas.
    """
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(obligations.to_dict(), f, ensure_ascii=False, indent=4)
    print(f"Obrigações salvas com sucesso em {file_path}")

def load_obligations(file_path: str) -> GestorObrigacoesFiscais:
    """
    Carrega as obrigações fiscais e declarativas de um arquivo JSON.
    
    :param file_path: Caminho do arquivo de onde as obrigações serão carregadas.
    :return: Instância de GestorObrigacoesFiscais contendo as obrigações carregadas.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        gestor = GestorObrigacoesFiscais.from_dict(data)
        print(f"Obrigações carregadas com sucesso de {file_path}")
        return gestor
    except FileNotFoundError:
        print(f"Arquivo {file_path} não encontrado. Retornando um gestor vazio.")
        return GestorObrigacoesFiscais()
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON {file_path}. Retornando um gestor vazio.")
        return GestorObrigacoesFiscais()

# Exemplo de uso atualizado
if __name__ == "__main__":
    gestor = GestorObrigacoesFiscais()
    
    # Defina os caminhos corretos para os PDFs
    caminho_pdf_fiscal = os.path.join("data", "Obrigacoes_pagamento.pdf")
    caminho_pdf_declarativo = os.path.join("data", "Obrigacoes_declarativas.pdf")
    
    # Verifique se os arquivos existem
    if not os.path.exists(caminho_pdf_fiscal):
        print(f"Arquivo não encontrado: {caminho_pdf_fiscal}")
    else:
        obrigacoes_fiscais = carregar_obrigacoes_de_arquivo(caminho_pdf_fiscal)
        for ob in obrigacoes_fiscais:
            gestor.adicionar_obrigacao(ob)
        print(f"Obrigações fiscais carregadas de {caminho_pdf_fiscal}")

    if not os.path.exists(caminho_pdf_declarativo):
        print(f"Arquivo não encontrado: {caminho_pdf_declarativo}")
    else:
        obrigacoes_declarativas = carregar_obrigacoes_de_arquivo(caminho_pdf_declarativo)
        for ob in obrigacoes_declarativas:
            gestor.adicionar_obrigacao(ob)
        print(f"Obrigações declarativas carregadas de {caminho_pdf_declarativo}")

    # Salvar as obrigações
    caminho_json = os.path.join("data", "obrigacoes_fiscais.json")
    save_obligations(gestor, caminho_json)

    # Carregar as obrigações
    gestor_carregado = load_obligations(caminho_json)

    print("\nPróximas obrigações fiscais e declarativas (carregadas do JSON):")
    for ob in gestor_carregado.obter_proximas_obrigacoes():
        print(f"{ob.tipo.capitalize()}: {ob.nome} - {formatar_data(ob.prazo)} - {ob.descricao}")
