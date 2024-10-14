import pandas as pd
import random
import string
from datetime import datetime, timedelta

def introduzir_erro_digitacao(texto, probabilidade=0.1):
    if random.random() < probabilidade:
        if len(texto) > 1:
            posicao = random.randint(0, len(texto) - 1)
            caractere = texto[posicao]
            if caractere.isalpha():
                teclado_qwerty = {
                    'q': 'wa', 'w': 'qes', 'e': 'wrd', 'r': 'eft', 't': 'rgy', 'y': 'tuh', 'u': 'yij', 'i': 'uok', 'o': 'iplç', 'p': 'oç',
                    'a': 'qsz', 's': 'awxd', 'd': 'sefc', 'f': 'drgv', 'g': 'fthb', 'h': 'gyjn', 'j': 'huim', 'k': 'jol', 'l': 'kpç',
                    'z': 'asx', 'x': 'zdc', 'c': 'xfv', 'v': 'cgb', 'b': 'vhn', 'n': 'bjm', 'm': 'nk'
                }
                if caractere.lower() in teclado_qwerty:
                    novo_caractere = random.choice(teclado_qwerty[caractere.lower()])
                    if caractere.isupper():
                        novo_caractere = novo_caractere.upper()
                    texto = texto[:posicao] + novo_caractere + texto[posicao + 1:]
    return texto

def gerar_nif():
    return f"{random.choice([1,2,5,6,8,9])}{random.randint(100000000, 999999999):09d}"

def gerar_descricao(categoria):
    descricao_base = ""
    if categoria == "Equipamentos Informáticos":
        items = ["Computador", "Portátil", "Tablet", "Monitor", "Teclado", "Rato", "Impressora", "Scanner", "Webcam", "Disco Rígido Externo", "Router Wi-Fi", "Switch de Rede"]
        marcas = ["Dell", "HP", "Lenovo", "Apple", "Asus", "Acer", "Samsung", "LG", "BenQ", "Logitech", "TP-Link", "D-Link"]
        modelos = ["Pro", "Elite", "Advanced", "Basic", "Ultra", "Slim", "Turbo", "Max"]
        descricao_base = f"{random.choice(items)} {random.choice(marcas)} {random.choice(modelos)} para uso profissional"
    elif categoria == "Serviços de Auditoria":
        tipos = ["financeira", "operacional", "de conformidade", "de sistemas", "de qualidade", "ambiental", "de segurança da informação", "forense", "interna"]
        periodos = ["anual", "semestral", "trimestral", "pontual"]
        normas = ["ISO 9001", "ISO 14001", "ISO 27001", "RGPD", "SOX"]
        descricao_base = f"Serviço de auditoria {random.choice(tipos)} {random.choice(periodos)} conforme {random.choice(normas)}"
    elif categoria == "Serviços de Manutenção":
        items = ["ar condicionado", "elevadores", "sistemas elétricos", "sistemas de segurança", "equipamentos de escritório", "veículos da empresa", "sistemas de climatização", "rede informática"]
        tipos = ["preventiva", "corretiva", "preditiva"]
        periodicidade = ["mensal", "trimestral", "semestral", "anual"]
        descricao_base = f"Manutenção {random.choice(tipos)} {random.choice(periodicidade)} de {random.choice(items)}"
    elif categoria == "Mobiliário e Equipamento de Escritório":
        items = ["secretária", "cadeira ergonómica", "armário de arquivo", "estante", "mesa de reunião", "sofá para receção", "quadro branco", "projetor", "sistema de videoconferência", "cofre"]
        materiais = ["madeira", "metal", "vidro", "plástico", "couro sintético"]
        cores = ["preto", "branco", "cinza", "castanho", "azul"]
        descricao_base = f"{random.choice(items)} em {random.choice(materiais)} {random.choice(cores)} para escritório"
    elif categoria == "Serviços de Contabilidade":
        servicos = ["processamento de salários", "preparação de demonstrações financeiras", "consultoria fiscal", "reconciliação bancária", "elaboração de relatórios financeiros", "preparação de IES", "apoio em auditorias fiscais", "planeamento fiscal"]
        periodos = ["mensal", "trimestral", "anual"]
        descricao_base = f"Serviço de {random.choice(servicos)} {random.choice(periodos)}"
    elif categoria == "Licenciamento de Software":
        softwares = ["Microsoft Office", "Adobe Creative Suite", "AutoCAD", "SAP", "Salesforce", "QuickBooks", "SPSS", "Antivírus Corporativo", "Sage", "Primavera", "PHC"]
        tipos = ["anual", "perpétua", "por utilizador", "por dispositivo", "enterprise", "cloud"]
        versoes = ["2023", "Plus", "Pro", "Enterprise", "Ultimate"]
        descricao_base = f"Licença {random.choice(tipos)} de {random.choice(softwares)} {random.choice(versoes)}"
    elif categoria == "Serviços de Consultoria":
        areas = ["gestão", "recursos humanos", "marketing digital", "estratégia empresarial", "transformação digital", "gestão de projetos", "sustentabilidade", "internacionalização", "inovação", "compliance"]
        duracao = ["pontual", "projeto de 3 meses", "contrato anual"]
        descricao_base = f"Consultoria em {random.choice(areas)} - {random.choice(duracao)}"
    elif categoria == "Material de Escritório":
        items = ["papel A4", "canetas", "agrafadores", "furadores", "pastas de arquivo", "post-its", "marcadores", "clips", "envelopes", "calendários", "agendas", "tinteiros"]
        quantidades = ["caixa de", "pacote de", "conjunto de", "resma de"]
        descricao_base = f"Fornecimento de {random.choice(quantidades)} {random.choice(items)} para escritório"
    elif categoria == "Despesas de Transporte e Logística":
        servicos = ["transporte de mercadorias", "serviços de courier", "aluguer de veículos", "combustível", "portagens", "manutenção de frota", "seguro automóvel", "transporte de colaboradores"]
        detalhes = ["nacional", "internacional", "urbano", "expresso", "económico"]
        descricao_base = f"Despesa com {random.choice(servicos)} - {random.choice(detalhes)}"
    elif categoria == "Serviços de Marketing":
        servicos = ["campanha publicitária", "gestão de redes sociais", "design gráfico", "produção de vídeo", "organização de eventos", "relações públicas", "SEO", "email marketing", "branding"]
        plataformas = ["Facebook", "Instagram", "LinkedIn", "Google Ads", "YouTube", "TikTok"]
        descricao_base = f"Serviço de {random.choice(servicos)} para {random.choice(plataformas)}"
    elif categoria == "Telecomunicações":
        servicos = ["plano de dados móveis", "telefonia fixa", "internet de fibra ótica", "VoIP", "videoconferência", "linha verde", "centralita virtual"]
        operadoras = ["MEO", "NOS", "Vodafone", "NOWO"]
        velocidades = ["100 Mbps", "200 Mbps", "500 Mbps", "1 Gbps"]
        descricao_base = f"Serviço de {random.choice(servicos)} empresarial {random.choice(velocidades)} - {random.choice(operadoras)}"
    elif categoria == "Formação e Desenvolvimento":
        cursos = ["liderança", "gestão de tempo", "competências digitais", "línguas estrangeiras", "segurança no trabalho", "gestão de conflitos", "RGPD", "cibersegurança", "Excel avançado", "gestão de equipas remotas"]
        formatos = ["presencial", "online", "blended"]
        duracao = ["8 horas", "16 horas", "24 horas", "40 horas"]
        descricao_base = f"Formação em {random.choice(cursos)} para colaboradores - {random.choice(formatos)} {random.choice(duracao)}"
    elif categoria == "Serviços Jurídicos":
        servicos = ["assessoria contratual", "resolução de litígios", "propriedade intelectual", "direito laboral", "fusões e aquisições", "recuperação de créditos", "contencioso fiscal", "proteção de dados"]
        tipos_documento = ["parecer", "contrato", "procuração", "acordo"]
        descricao_base = f"Serviço jurídico de {random.choice(servicos)} - elaboração de {random.choice(tipos_documento)}"
    elif categoria == "Seguros":
        tipos = ["seguro de responsabilidade civil", "seguro multirriscos", "seguro de saúde grupal", "seguro de acidentes de trabalho", "seguro de frota automóvel", "seguro de crédito", "seguro de cibersegurança"]
        coberturas = ["básica", "standard", "premium", "all-risk"]
        seguradoras = ["Fidelidade", "Tranquilidade", "Allianz", "Ageas", "Generali"]
        descricao_base = f"Contratação de {random.choice(tipos)} - cobertura {random.choice(coberturas)} ({random.choice(seguradoras)})"
    elif categoria == "Energia e Utilidades":
        servicos = ["eletricidade", "água", "gás natural", "gestão de resíduos", "energias renováveis"]
        fornecedores = ["EDP", "Galp", "Endesa", "Iberdrola", "Goldenergy"]
        tarifas = ["simples", "bi-horária", "tri-horária"]
        descricao_base = f"Fornecimento de {random.choice(servicos)} para instalações - tarifa {random.choice(tarifas)} ({random.choice(fornecedores)})"

    # Adicionar detalhes extras aleatoriamente
    detalhes_extras = [
        f" (NIF: {gerar_nif()})",
        f" - Fatura nº {random.randint(1000, 9999)}/{datetime.now().year}",
        f" - Ref: {random.choice(string.ascii_uppercase)}{random.randint(100, 999)}",
        f" - Cód. {random.choice(string.ascii_uppercase)}{random.randint(1000, 9999)}",
        f" (Período: {random.choice(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])}/{datetime.now().year})",
    ]
    
    descricao = descricao_base + random.choice(detalhes_extras)
    return introduzir_erro_digitacao(descricao)

def gerar_valor():
    base = random.uniform(10, 10000)
    centimos = round(base * 100) / 100  # Arredonda para 2 casas decimais
    return centimos

def gerar_data():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def formatar_valor(valor):
    return f"{valor:.2f} €" if random.random() < 0.5 else f"{valor:.2f}€"

def formatar_data(data):
    formatos = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d.%m.%Y"]
    return data.strftime(random.choice(formatos))

categorias = [
    "Equipamentos Informáticos", "Serviços de Auditoria", "Serviços de Manutenção",
    "Mobiliário e Equipamento de Escritório", "Serviços de Contabilidade",
    "Licenciamento de Software", "Serviços de Consultoria", "Material de Escritório",
    "Despesas de Transporte e Logística", "Serviços de Marketing", "Telecomunicações",
    "Formação e Desenvolvimento", "Serviços Jurídicos", "Seguros", "Energia e Utilidades"
]

data = {
    "Descrição do Item": [],
    "Categoria": [],
    "Valor": [],
    "Data": []
}

for categoria in categorias:
    for _ in range(200):
        descricao = gerar_descricao(categoria)
        data["Descrição do Item"].append(descricao)
        data["Categoria"].append(categoria)
        data["Valor"].append(formatar_valor(gerar_valor()))
        data["Data"].append(formatar_data(gerar_data()))

df = pd.DataFrame(data)
df = df.sample(frac=1).reset_index(drop=True)
df.to_csv("dados_faturas.csv", index=False)

print(f"Gerados {len(df)} exemplos de dados.")
print(df.head())
print("\nDistribuição de categorias:")
print(df['Categoria'].value_counts())
print("\nExemplos de descrições geradas:")
print(df['Descrição do Item'].sample(5))