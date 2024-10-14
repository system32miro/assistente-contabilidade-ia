# Assistente de Contabilidade IA

Este projeto implementa um assistente de contabilidade baseado em IA que permite o upload e análise de faturas, bem como a interação com um agente de IA para questões contabilísticas.

## Funcionalidades

- Upload e análise automática de faturas em PDF
- Categorização automática de despesas
- Verificação de obrigações fiscais
- Interação com agente IA para questões contabilísticas
- Utilização da API Groq com o modelo Llama 3.2 11B Vision para processamento de linguagem natural e análise de imagens

## Pré-requisitos

- Python 3.8 ou superior
- Conta na Groq API (para obter a chave da API)

## Instalação

1. Clone o repositório:
   ```
   git clone https://github.com/seu-usuario/assistente-contabilidade-ia.git
   ```

2. Navegue até à pasta do projeto:
   ```
   cd assistente-contabilidade-ia
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   Crie um arquivo `.env` na raiz do projeto e adicione sua chave da API Groq:
   ```
   GROQ_API_KEY=sua_chave_api_aqui
   ```

## Configuração da API Groq

Este projeto utiliza a API Groq com o modelo Llama 3.2 11B Vision para processamento de linguagem natural e análise de imagens. Para configurar:

1. Obtenha uma chave de API em [Groq API](https://console.groq.com/)
2. Adicione a chave ao arquivo `.env` conforme descrito acima
3. O modelo Llama 3.2 11B Vision é utilizado automaticamente pela API

## Utilização

1. Execute o ficheiro `main.py`:
   ```
   python main.py
   ```

2. Use o botão "Upload Fatura" para carregar faturas em PDF para análise.
3. Interaja com o assistente digitando mensagens na área de entrada.
4. Siga as instruções no ecrã para realizar ações adicionais após o upload de faturas.

## Estrutura do Projeto

- `main.py`: Ponto de entrada da app
- `gui.py`: Interface gráfica do utilizador
- `pdf_processor.py`: Processamento e extração de texto de faturas em PDF
- `categorizador.py`: Categorização automática de itens de faturas
- `tax_analyzer.py`: Análise fiscal e cálculos relacionados a impostos
- `api_handler.py`: Integração com a API Groq e lógica do assistente IA
- `config.py`: Configurações globais e constantes
- `data.py`: Geração de dados sintéticos para treino do modelo
- `treinar_modelo_categorias.py`: Treino e avaliação do modelo de categorização
- `treino_agendado.py`: Sistema de treino automático e agendado

## Testes

Para executar os testes unitários e de integração, use o comando:
```
python run_tests.py
```

## Treino Agendado

O sistema inclui um módulo de treino agendado (`treino_agendado.py`) que atualiza periodicamente o modelo de categorização com novos dados.

## Contribuições

Contribuições são bem-vindas! Por favor, abra um issue para discutir alterações importantes antes de submeter um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Suporte

Para questões, problemas ou sugestões, por favor abra um issue no GitHub ou contate o mantenedor do projeto.
