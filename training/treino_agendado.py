import logging
import os
import time
from datetime import datetime
import json
from training.treinar_modelo_categorias import carregar_dados, treinar_modelo, avaliar_modelo, gerar_dados
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib
import pandas as pd

# Adicione estas linhas aqui
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import CAMINHO_CSV_TREINO, DIRETORIO_MODELOS

# Configuração do logging
log_directory = 'logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

log_filename = os.path.join(log_directory, f'treino_agendado_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def registrar_metricas(y_true, y_pred, nome_arquivo):
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted')
    
    metricas = {
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }
    
    caminho_arquivo = os.path.join(log_directory, nome_arquivo)
    
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as f:
            historico = json.load(f)
    else:
        historico = []
    
    historico.append(metricas)
    
    with open(caminho_arquivo, 'w') as f:
        json.dump(historico, f, indent=4)
    
    logging.info(f"Métricas registradas: Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
    return metricas

def salvar_modelo_versionado(modelo, diretorio_destino):
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f'modelo_categorias_{data_atual}.joblib'
    caminho_modelo = os.path.join(diretorio_destino, nome_arquivo)
    joblib.dump(modelo, caminho_modelo)
    logging.info(f"Modelo salvo com sucesso em: {caminho_modelo}")
    return nome_arquivo

def atualizar_registro_versoes(nome_arquivo, metricas):
    caminho_registro = os.path.join(DIRETORIO_MODELOS, 'registro_versoes.json')
    if os.path.exists(caminho_registro):
        with open(caminho_registro, 'r') as f:
            registro = json.load(f)
    else:
        registro = []

    versao = {
        "nome_arquivo": nome_arquivo,
        "data_treino": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metricas": metricas
    }
    registro.append(versao)

    with open(caminho_registro, 'w') as f:
        json.dump(registro, f, indent=4)

    logging.info(f"Registro de versão atualizado para o modelo: {nome_arquivo}")

def executar_treino_agendado():
    # Gerar novos dados
    novos_dados = gerar_dados(num_samples=1000)  # ou o número que preferir
    
    # Salvar os novos dados (opcional)
    novos_dados.to_csv('data/novos_dados_gerados.csv', index=False)
    
    # Carregar dados existentes e combinar com os novos
    dados_existentes = carregar_dados(CAMINHO_CSV_TREINO)
    dados_combinados = pd.concat([dados_existentes, novos_dados], ignore_index=True)
    
    # Treinar o modelo com os dados combinados
    modelo, X_test, y_test = treinar_modelo(dados_combinados)
    
    # Avaliar o modelo
    relatorio_avaliacao = avaliar_modelo(modelo, X_test, y_test)
    print("Relatório de avaliação:")
    print(relatorio_avaliacao)
    
    # Salvar o novo modelo
    nome_arquivo = salvar_modelo_versionado(modelo, DIRETORIO_MODELOS)
    
    # Registrar métricas
    y_pred = modelo.predict(X_test)
    metricas = registrar_metricas(y_test, y_pred, 'metricas_modelo.json')
    
    # Atualizar registro de versões
    atualizar_registro_versoes(nome_arquivo, metricas)

    logging.info("Treino agendado concluído com sucesso.")