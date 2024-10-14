# Assistente de Contabilidade Português

## Visão Geral
Este projeto implementa um assistente de contabilidade especializado na legislação portuguesa. Ele oferece funcionalidades como processamento de faturas, categorização automática de despesas e lembretes de prazos fiscais.

## Novas Funcionalidades: Sistema de Categorização Automática

### Descrição
O sistema agora inclui um modelo de aprendizado de máquina para categorização automática de itens de fatura. Esta funcionalidade utiliza técnicas de processamento de linguagem natural (NLP) e aprendizado de máquina para classificar automaticamente as despesas em categorias predefinidas.

### Componentes Principais
1. **Pré-processamento de Texto**: Implementado na função `preprocess_text()`, que limpa e prepara o texto para análise.
2. **Carregamento de Dados**: A função `carregar_dados()` lê e prepara os dados de treinamento.
3. **Treinamento do Modelo**: Realizado pela função `treinar_modelo()`, que utiliza um pipeline de TfidfVectorizer e RandomForestClassifier.
4. **Categorização**: A função `categorizar_item()` utiliza o modelo treinado para prever a categoria de novos itens.

### Como Funciona
1. O sistema carrega ou treina um modelo de categorização durante a inicialização.
2. Ao processar uma fatura, cada item é automaticamente categorizado.
3. A categorização é integrada ao fluxo de análise de faturas, fornecendo sugestões de categoria para cada item.

### Benefícios
- Agiliza o processo de categorização de despesas.
- Melhora a consistência na classificação de itens.
- Reduz erros humanos no processo de categorização.

### Uso
O sistema de categorização é utilizado automaticamente durante o processamento de faturas. Não é necessária nenhuma ação adicional do usuário para ativar esta funcionalidade.

## Instalação e Execução
(Mantenha as instruções existentes de instalação e execução)

## Dependências
(Atualize a lista de dependências, incluindo as novas bibliotecas necessárias para o sistema de categorização)

## Contribuição
(Mantenha as instruções existentes para contribuição)

## Licença
(Mantenha as informações de licença existentes)
