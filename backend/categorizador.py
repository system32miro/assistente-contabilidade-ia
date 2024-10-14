import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import os
import logging
import scipy.sparse as sp

def carregar_modelo(caminho_modelo):
    try:
        modelo = joblib.load(caminho_modelo)
        caminho_vectorizer = caminho_modelo.replace('modelo_categorias', 'tfidf_vectorizer')
        
        if os.path.exists(caminho_vectorizer):
            vectorizer = joblib.load(caminho_vectorizer)
        else:
            logging.warning(f"Arquivo do vectorizer não encontrado: {caminho_vectorizer}")
            vectorizer = None

        logging.info(f"Modelo carregado com sucesso de: {caminho_modelo}")
        return modelo, vectorizer
    except Exception as e:
        logging.error(f"Erro ao carregar modelo de {caminho_modelo}: {str(e)}")
        return None, None

def categorizar_item(descricao, modelo, vectorizer):
    try:
        # Converter a descrição para minúsculas antes de vetorizar
        descricao_lower = descricao.lower()
        descricao_vetorizada = vectorizer.transform([descricao_lower])
        
        # Converter csr_matrix para array denso se necessário
        if sp.issparse(descricao_vetorizada):
            descricao_vetorizada = descricao_vetorizada.toarray()
        
        categoria_prevista = modelo.predict(descricao_vetorizada)[0]
        return {"categoria": categoria_prevista}
    except Exception as e:
        logging.error(f"Erro ao categorizar item: {str(e)}")
        return {"erro": str(e)}
def obter_categoria_fiscal(categoria):
    # Implementar lógica para mapear categoria para categoria fiscal
    # Por exemplo:
    mapeamento = {
        'categoria1': 'fiscal1',
        'categoria2': 'fiscal2',
        # Adicionar mais mapeamentos conforme necessário
    }
    return mapeamento.get(categoria, 'fiscal_padrao')

# Exemplo de uso
if __name__ == "__main__":
    diretorio_modelo = 'caminho/para/o/diretorio/do/modelo'
    modelo, vectorizer = carregar_modelo(diretorio_modelo)
    
    if modelo and vectorizer:
        descricao_teste = "Serviço de consultoria em gestão de projetos"
        resultado = categorizar_item(descricao_teste, modelo, vectorizer)
        print(f"Descrição: {descricao_teste}")
        print(f"Categoria: {resultado.get('categoria', 'Erro')}")
        print(f"Categoria Fiscal: {resultado.get('tax_category', 'Erro')}")
    else:
        print("Não foi possível carregar o modelo ou o vectorizer.")
