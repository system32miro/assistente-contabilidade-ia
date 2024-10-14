import pandas as pd
import logging
import os
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib
import sys
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import CAMINHO_CSV_TREINO, DIRETORIO_MODELOS

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def gerar_dados(num_samples=1000):
    import random
    from datetime import datetime, timedelta

    categorias = [
        "Serviços de Marketing", "Formação e Desenvolvimento", "Telecomunicações",
        "Serviços de Manutenção", "Serviços de Auditoria", "Licenciamento de Software",
        "Serviços Jurídicos", "Seguros", "Despesas de Transporte e Logística",
        "Material de Escritório", "Serviços de Consultoria", "Energia e Utilidades",
        "Serviços de Contabilidade", "Mobiliário e Equipamento de Escritório",
        "Equipamentos Informáticos"
    ]

    dados = []
    for _ in range(num_samples):
        categoria = random.choice(categorias)
        descricao = f"Exemplo de {categoria.lower()} - Item {_+1}"
        valor = round(random.uniform(100, 10000), 2)
        data = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%d/%m/%Y')
        dados.append([descricao, categoria, valor, data])

    df = pd.DataFrame(dados, columns=['Descrição do Item', 'Categoria', 'Valor', 'Data'])
    return df

def carregar_dados(caminho_csv):
    try:
        df = pd.read_csv(caminho_csv)
        logging.info(f"Dados carregados com sucesso: {caminho_csv}")
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar dados: {str(e)}")
        return None

def preprocess_text(text):
    # O pré-processamento básico será feito pelo TfidfVectorizer
    return text

def treinar_modelo(df, n_splits=5):
    X = df['Descrição do Item'].apply(preprocess_text)
    y = df['Categoria']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('clf', RandomForestClassifier())
    ])

    # Ajuste os parâmetros com base no tamanho do conjunto de dados
    if len(X_train) < 100:
        param_grid = {
            'tfidf__max_features': [500, 1000],
            'tfidf__ngram_range': [(1, 1)],
            'clf__n_estimators': [50],
            'clf__max_depth': [10, None]
        }
    else:
        param_grid = {
            'tfidf__max_features': [1000, 2000],
            'tfidf__ngram_range': [(1, 1), (1, 2)],
            'clf__n_estimators': [100],
            'clf__max_depth': [10, 20, None]
        }

    grid_search = GridSearchCV(pipeline, param_grid, cv=n_splits, n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)

    logging.info("Modelo treinado com sucesso")
    return grid_search, X_test, y_test

def avaliar_modelo(modelo, X_test, y_test):
    y_pred = modelo.predict(X_test)
    return classification_report(y_test, y_pred)

def salvar_modelo(modelo, diretorio_destino):
    os.makedirs(diretorio_destino, exist_ok=True)
    data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    caminho_modelo = os.path.join(diretorio_destino, f'modelo_categorias_{data_atual}.joblib')
    caminho_vectorizer = os.path.join(diretorio_destino, f'tfidf_vectorizer_{data_atual}.joblib')
    
    joblib.dump(modelo, caminho_modelo)
    joblib.dump(modelo.named_steps['tfidf'], caminho_vectorizer)
    
    logging.info(f"Modelo salvo em: {caminho_modelo}")
    logging.info(f"Vectorizer salvo em: {caminho_vectorizer}")
    
    return f'modelo_categorias_{data_atual}.joblib'

def avaliar_modelo_cv(modelo, X, y, cv=5):
    scores = cross_val_score(modelo, X, y, cv=cv, scoring='accuracy')
    return f"Acurácia média: {scores.mean():.2f} (+/- {scores.std() * 2:.2f})"

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

if __name__ == "__main__":
    dados = carregar_dados(CAMINHO_CSV_TREINO)
    if dados is not None:
        modelo, X_test, y_test = treinar_modelo(dados)
        
        print("Melhores parâmetros:", modelo.best_params_)
        print("Avaliação do modelo:")
        relatorio = avaliar_modelo(modelo, X_test, y_test)
        print(relatorio)
        
        print("Avaliação do modelo (validação cruzada):")
        X = dados['Descrição do Item'].apply(preprocess_text)
        y = dados['Categoria']
        cv_score = avaliar_modelo_cv(modelo, X, y)
        print(cv_score)
        
        nome_arquivo = salvar_modelo(modelo.best_estimator_, DIRETORIO_MODELOS)
        
        # Criar métricas para o registro
        metricas = {
            "melhores_parametros": modelo.best_params_,
            "relatorio_classificacao": relatorio,
            "validacao_cruzada": cv_score
        }
        
        # Atualizar o registro de versões
        atualizar_registro_versoes(nome_arquivo, metricas)
    else:
        print("Não foi possível carregar os dados.")