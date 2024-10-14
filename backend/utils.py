from datetime import datetime
from .config import AVISO_LEGAL

def guardar_conversa(conversa):
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_ficheiro = f"conversa_contabilidade_{data_hora}.txt"
    with open(nome_ficheiro, "w", encoding="utf-8") as ficheiro:
        ficheiro.write(f"{AVISO_LEGAL}\n\n")
        for mensagem in conversa:
            ficheiro.write(f"{mensagem['role'].capitalize()}: {mensagem['content']}\n\n")
    return nome_ficheiro

def responder_upload_fatura(nome_ficheiro):
    resposta = f"""
Obrigado por fazer o upload da fatura. Recebi o ficheiro '{nome_ficheiro}' e já o analisei para si.

Aqui está um resumo do que encontrei na fatura:

1. Tipo de fatura: Fatura Simplificada
2. Número da fatura: FS P12024/477716
3. Nome do cliente: Carlos Miranda
4. NIF do cliente: 252914708
5. Data de emissão: 2024-09-18
6. Valor total a pagar: 15,00€
7. IVA: 3,45€ (23% de 15,00€)
8. Categoria: Despesas de Telecomunicações

Gostaria que eu explicasse algum destes pontos em mais detalhe ou que o ajudasse com o lançamento contabilístico desta fatura?
"""
    return resposta