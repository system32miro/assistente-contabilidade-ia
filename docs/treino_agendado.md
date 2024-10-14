# Módulo Treino Agendado

## Visão Geral
O módulo `treino_agendado.py` implementa um sistema de treino automático e agendado para o modelo de categorização.

## Funções Principais

### executar_treino_agendado()
Função principal que executa o processo de treino agendado.

**Responsabilidades:**
- Carrega os dados de treino
- Treina um novo modelo
- Avalia o desempenho do modelo
- Salva o modelo com versionamento
- Registra métricas de desempenho
- Atualiza o registro de versões do modelo

### salvar_modelo_versionado(modelo, diretorio: str) -> str
Salva o modelo treinado com um nome de arquivo versionado.

**Parâmetros:**
- `modelo`: O modelo treinado a ser salvo.
- `diretorio`: O diretório onde o modelo será salvo.

**Retorna:**
- O nome do arquivo do modelo salvo.

### registrar_metricas(y_true, y_pred, caminho_arquivo: str) -> dict
Calcula e registra as métricas de desempenho do modelo.

**Parâmetros:**
- `y_true`: Etiquetas verdadeiras.
- `y_pred`: Previsões do modelo.
- `caminho_arquivo`: Caminho para o arquivo onde as métricas serão salvas.

**Retorna:**
- Um dicionário contendo as métricas calculadas.

### atualizar_registro_versoes(nome_arquivo: str, metricas: dict)
Atualiza o registro de versões do modelo com informações sobre a nova versão.

**Parâmetros:**
- `nome_arquivo`: Nome do arquivo do modelo salvo.
- `metricas`: Métricas de desempenho do modelo.

## Uso
Este módulo é configurado para ser executado periodicamente (por exemplo, diariamente) para manter o modelo de categorização atualizado com os dados mais recentes.

## Notas
- O agendamento do treino é configurado usando a biblioteca `schedule`.
- As métricas e o registro de versões são salvos em arquivos JSON para fácil acompanhamento do histórico de treinamento.