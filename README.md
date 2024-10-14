# Assistente de Contabilidade IA

Este projeto implementa um assistente de contabilidade baseado em IA que permite o upload e análise de faturas, bem como a interação com um agente de IA para questões contabilísticas.

## Funcionalidades

- Upload e análise automática de faturas
- Categorização de despesas
- Verificação de obrigações fiscais
- Interação com agente IA para questões contabilísticas
- Utilização da API Groq para processamento de linguagem natural

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

Este projeto utiliza a API Groq para processamento de linguagem natural. Para configurar:

1. Obtenha uma chave de API em [Groq API](https://console.groq.com/)
2. Adicione a chave ao arquivo `.env` conforme descrito acima
3. O modelo utilizado é o `mixtral-8x7b-32768`, que é carregado automaticamente no código

## Utilização

1. Execute o ficheiro `main.py`:
   ```
   python main.py
   ```

2. Use o botão "Upload Fatura" para carregar faturas para análise.
3. Interaja com o assistente digitando mensagens na área de entrada.
4. Siga as instruções no ecrã para realizar ações adicionais após o upload de faturas.

## Estrutura do Projeto

- `main.py`: Ponto de entrada do aplicativo
- `gui.py`: Interface gráfica do usuário
- `fatura_processor.py`: Processamento e análise de faturas
- `ia_agent.py`: Integração com a API Groq e lógica do assistente IA

## Contribuições

Contribuições são bem-vindas! Por favor, abra um issue para discutir alterações importantes antes de submeter um pull request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Suporte

Para questões, problemas ou sugestões, por favor abra um issue no GitHub ou contate o mantenedor do projeto.
