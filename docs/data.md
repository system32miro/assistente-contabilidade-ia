# Módulo Data

## Visão Geral
O módulo `data.py` é responsável pela geração de dados sintéticos para treino e teste do modelo de categorização. Ele cria um conjunto de dados realista de itens de fatura com suas respetivas categorias.

## Funções Principais

### introduzir_erro_digitacao(texto: str, probabilidade: float = 0.1) -> str
Introduz erros de digitação aleatórios no texto fornecido.

**Parâmetros:**
- `texto`: O texto original.
- `probabilidade`: A probabilidade de introduzir um erro (padrão: 0.1).

**Retorna:**
- O texto com possíveis erros de digitação.

### gerar_descricao(categoria: str) -> str
Gera uma descrição aleatória para um item de fatura baseado na categoria.

**Parâmetros:**
- `categoria`: A categoria do item.

**Retorna:**
- Uma descrição gerada aleatoriamente.

### gerar_valor() -> float
Gera um valor aleatório para um item de fatura.

**Retorna:**
- Um valor float aleatório.

### gerar_data() -> datetime
Gera uma data aleatória dentro do último ano.

**Retorna:**
- Um objeto datetime.

### formatar_valor(valor: float) -> str
Formata um valor float para uma string de moeda.

**Parâmetros:**
- `valor`: O valor a ser formatado.

**Retorna:**
- Uma string formatada como moeda.

### formatar_data(data: datetime) -> str
Formata um objeto datetime para uma string de data.

**Parâmetros:**
- `data`: O objeto datetime a ser formatado.

**Retorna:**
- Uma string de data formatada.

## Uso
Este módulo é utilizado para gerar dados de treino e teste para o modelo de categorização. Quando executado diretamente, ele cria um arquivo CSV com dados sintéticos de faturas.

## Notas
- Os dados gerados incluem descrições de itens, categorias, valores e datas.
- São introduzidos erros de digitação aleatórios para simular dados do mundo real.
- O arquivo gerado é salvo como "dados_faturas.csv" no diretório atual.