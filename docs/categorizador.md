# Módulo Categorizador

## Visão Geral
O módulo `categorizador.py` é responsável pela categorização automática de itens de faturas utilizando técnicas de aprendizado de máquina e processamento de linguagem natural.

## Funções Principais

### carregar_modelo(caminho_modelo: str) -> tuple
Carrega o modelo de categorização e o vectorizador TF-IDF a partir de ficheiros salvos.

**Parâmetros:**
- `caminho_modelo`: Caminho para o ficheiro do modelo.

**Retorna:**
- Uma tupla contendo o modelo carregado e o vectorizador TF-IDF.

### categorizar_item(descricao: str, modelo, vectorizer) -> dict
Categoriza um item de fatura com base na sua descrição.

**Parâmetros:**
- `descricao`: Descrição do item a ser categorizado.
- `modelo`: Modelo de categorização carregado.
- `vectorizer`: Vectorizador TF-IDF carregado.

**Retorna:**
- Um dicionário contendo a categoria prevista e a categoria fiscal correspondente.

**Exemplo de uso:**