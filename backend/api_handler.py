import requests
from requests.exceptions import RequestException, Timeout, HTTPError
import json
import logging
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

API_KEY = os.getenv('GROQ_API_KEY')
API_URL = 'https://api.groq.com/openai/v1/chat/completions'

def gerar_resposta(mensagens):
    logging.info(f"Gerando resposta para {len(mensagens)} mensagens")
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    dados = {
        'model': 'llama-3.2-90b-text-preview',
        'messages': mensagens,
        'max_tokens': 500
    }
    
    try:
        resposta = requests.post(API_URL, json=dados, headers=headers, timeout=30)
        resposta.raise_for_status()
        conteudo = resposta.json()
        logging.info("Resposta gerada com sucesso")
        return conteudo['choices'][0]['message']['content']
    except Timeout:
        erro = "Tempo limite excedido ao conectar-se à API."
        logging.error(erro)
        return erro
    except HTTPError as http_err:
        erro = f"Erro HTTP ao conectar-se à API: {http_err}"
        logging.error(erro)
        return erro
    except RequestException as req_err:
        erro = f"Erro na requisição à API: {req_err}"
        logging.error(erro)
        return erro
    except KeyError as key_err:
        erro = f"Erro ao processar a resposta da API: {key_err}"
        logging.error(erro)
        return erro
    except json.JSONDecodeError as json_err:
        erro = f"Erro ao decodificar a resposta JSON da API: {json_err}"
        logging.error(erro)
        return erro
    except Exception as e:
        erro = f"Erro inesperado ao gerar resposta: {e}"
        logging.error(erro)
        return erro

def inicializar_api():
    if not API_KEY:
        raise ValueError("A chave da API Groq não foi configurada. Verifique o arquivo .env")
    logging.info("API Groq inicializada com sucesso")
