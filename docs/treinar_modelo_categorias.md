# Módulo Treinar Modelo Categorias

## Visão Geral
O módulo `treinar_modelo_categorias.py` é responsável pelo treinamento e avaliação do modelo de categorização automática de itens de fatura.

## Funções Principais

### carregar_dados(caminho_csv: str) -> tuple
Carrega e prepara os dados de treino a partir de um ficheiro CSV.

**Parâmetros:**
- `caminho_csv`: Caminho para o ficheiro CSV contendo os dados de treino.

**Retorna:**
- Uma tupla contendo os dados de treino (X) e as etiquetas (y).

### treinar_modelo(X_train, y_train) -> tuple
Treina o modelo de categorização utilizando TfidfVectorizer e RandomForestClassifier.

**Parâmetros:**
- `X_train`: Dados de treino.
- `y_train`: Etiquetas de treino.

**Retorna:**
- Uma tupla contendo o modelo treinado e o vectorizador.

### avaliar_modelo(modelo, vectorizer, X_test, y_test) -> dict
Avalia o desempenho do modelo treinado.

**Parâmetros:**
- `modelo`: Modelo treinado.
- `vectorizer`: Vectorizador TF-IDF.
- `X_test`: Dados de teste.
- `y_test`: Etiquetas de teste.

**Retorna:**
- Um dicionário contendo métricas de avaliação (precisão, recall, f1-score).

### gerar_dados()
Gera dados de exemplo para treino e teste do modelo.

## Uso
Este módulo é utilizado para treinar e avaliar o modelo de categorização. Pode ser executado diretamente para realizar um ciclo completo de treinamento e avaliação.

## Notas
- Certifique-se de que o ficheiro CSV de treino está atualizado e contém dados representativos.
- O modelo treinado é salvo no diretório especificado em `config.py`.