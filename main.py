import logging
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import os
import json
import schedule
import time
import threading
from dotenv import load_dotenv
from backend.api_handler import inicializar_api
from frontend.gui import AssistenteContabilidade
from backend.config import DIRETORIO_MODELOS, CAMINHO_CSV_TREINO
from backend.utils import guardar_conversa, responder_upload_fatura
from backend.categorizador import carregar_modelo, categorizar_item
from training.treino_agendado import executar_treino_agendado
from backend.fiscal_obligations import GestorObrigacoesFiscais, carregar_obrigacoes_de_arquivo, save_obligations, load_obligations

# Configuração do logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, f'app_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Carrega as variáveis de ambiente do ficheiro .env
load_dotenv()

def carregar_modelo_mais_recente():
    caminho_registro = os.path.join(DIRETORIO_MODELOS, 'registro_versoes.json')
    logging.info(f"Verificando registro de versões em: {caminho_registro}")
    
    if os.path.exists(caminho_registro):
        with open(caminho_registro, 'r') as f:
            registro = json.load(f)
        if registro:
            modelo_mais_recente = max(registro, key=lambda x: x['data_treino'])
            caminho_modelo = os.path.join(DIRETORIO_MODELOS, modelo_mais_recente['nome_arquivo'])
            logging.info(f"Tentando carregar o modelo mais recente: {caminho_modelo}")
            if os.path.exists(caminho_modelo):
                modelo, vectorizer = carregar_modelo(caminho_modelo)
                if modelo is not None:
                    return modelo, vectorizer
            else:
                logging.error(f"Arquivo do modelo mais recente não encontrado: {caminho_modelo}")
    else:
        logging.warning(f"Arquivo de registro não encontrado: {caminho_registro}")
    
    # Se não encontrar no registro ou o arquivo não existir, tenta carregar o modelo padrão
    caminho_modelo_padrao = os.path.join(DIRETORIO_MODELOS, 'modelo_categorias.joblib')
    if os.path.exists(caminho_modelo_padrao):
        logging.info(f"Tentando carregar o modelo padrão: {caminho_modelo_padrao}")
        return carregar_modelo(caminho_modelo_padrao)
    
    logging.error(f"Nenhum modelo encontrado em: {DIRETORIO_MODELOS}")
    return None, None

def verificar_e_carregar_modelo():
    """
    Verifica se existe um modelo salvo e o carrega.
    Se não existir, alerta o utilizador para executar o script de treino.
    """
    modelo_path = os.path.join(DIRETORIO_MODELOS, 'modelo_categorias.joblib')
    if os.path.exists(modelo_path):
        logging.info("Modelo existente encontrado. Carregando...")
        return carregar_modelo(DIRETORIO_MODELOS)
    else:
        logging.warning("Modelo não encontrado.")
        messagebox.showwarning("Modelo não encontrado", 
                               "O modelo de categorização não foi encontrado. "
                               "Por favor, execute o script 'treinar_modelo_categorias.py' "
                               "para treinar o modelo antes de iniciar a aplicação.")
        return None, None

def inicializar_categorizador():
    logging.info(f"Tentando carregar o modelo mais recente de {DIRETORIO_MODELOS}")
    modelo, vectorizer = carregar_modelo_mais_recente()
    if modelo is None:
        logging.error(f"Falha ao carregar o modelo de {DIRETORIO_MODELOS}")
        logging.info("Verificando se o diretório de modelos existe")
        if not os.path.exists(DIRETORIO_MODELOS):
            logging.error(f"O diretório {DIRETORIO_MODELOS} não existe")
            os.makedirs(DIRETORIO_MODELOS)
            logging.info(f"Diretório {DIRETORIO_MODELOS} criado")
        else:
            logging.info(f"O diretório {DIRETORIO_MODELOS} existe")
            logging.info(f"Conteúdo do diretório {DIRETORIO_MODELOS}:")
            for file in os.listdir(DIRETORIO_MODELOS):
                logging.info(f"- {file}")
        raise ValueError("Modelo de categorização não disponível. Execute o script de treino.")
    logging.info("Modelo carregado com sucesso")
    return modelo, vectorizer

def verificar_permissoes():
    arquivos_necessarios = [
        os.path.join("data", "Obrigacoes_pagamento.pdf"),
        os.path.join("data", "Obrigacoes_declarativas.pdf"),
        os.path.join("data", "obrigacoes_fiscais.json")
    ]
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            if not os.access(arquivo, os.R_OK):
                logging.error(f"Sem permissão de leitura para o arquivo: {arquivo}")
                return False
        else:
            logging.warning(f"Arquivo não encontrado: {arquivo}")
    return True

def main():
    logging.info("Iniciando aplicação")
    try:
        if not verificar_permissoes():
            raise PermissionError("Sem permissões adequadas para os arquivos necessários")
        inicializar_api()
        modelo, vectorizer = inicializar_categorizador()
        
        root = ttk.Window(themename="superhero")
        root.title("Assistente de Contabilidade")
        root.geometry("1000x700")
        app = AssistenteContabilidade(root, guardar_conversa, modelo, vectorizer)
        root.mainloop()
    except PermissionError as e:
        logging.error(f"Erro de permissão: {e}")
        messagebox.showerror("Erro de Permissão", str(e))
    except ValueError as e:
        logging.error(f"Erro ao inicializar: {e}")
        messagebox.showerror("Erro de Inicialização", str(e))
    except Exception as e:
        logging.error(f"Erro inesperado: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {e}")

def teste_integracao_categorizacao():
    try:
        modelo, vectorizer = inicializar_categorizador()
        
        descricoes_teste = [
            "Computador portátil Dell Latitude para uso profissional",
            "Serviço de auditoria financeira anual",
            "Manutenção preventiva de ar condicionado",
            "Licença anual de Microsoft Office 365",
            "Consultoria em gestão de projetos - contrato trimestral"
        ]
        
        print("Teste de integração - Categorização:")
        for descricao in descricoes_teste:
            resultado = categorizar_item(descricao, modelo, vectorizer)
            print(f"Descrição: '{descricao}'")
            if "erro" in resultado:
                print(f"Erro: {resultado['erro']}")
            else:
                print(f"Categoria prevista: {resultado['categoria']}")
                print(f"Categoria Fiscal: {resultado['tax_category']}")
            print()
    except Exception as e:
        print(f"Erro no teste de integração: {str(e)}")
        logging.error(f"Erro no teste de integração: {str(e)}")

def agendar_treino():
    # Agendar para executar no primeiro dia de cada mês às 00:00
    schedule.every().day.at("00:00").do(executar_treino_agendado)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()

if __name__ == "__main__":
    agendar_treino()
    teste_integracao_categorizacao()
    main()
