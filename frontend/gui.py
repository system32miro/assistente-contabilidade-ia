import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog, ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import logging
from datetime import date, datetime
from backend.api_handler import gerar_resposta
from backend.pdf_processor import extrair_texto_pdf, validar_pdf, detect_invoice_layout, extrair_dados_estruturados
from backend.config import AVISO_LEGAL
from backend.categorizador import categorizar_item
from backend.fiscal_obligations import GestorObrigacoesFiscais, carregar_obrigacoes_de_arquivo, save_obligations, load_obligations
import json
import queue
import os
from sklearn.preprocessing import LabelEncoder
import re
import time

class AssistenteContabilidade:
    def __init__(self, master, guardar_conversa_func, modelo, vectorizer):
        self.master = master
        self.guardar_conversa = guardar_conversa_func
        self.modelo = modelo
        self.vectorizer = vectorizer
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.modelo.classes_)
        
        # Configuração do logging específico para categorização
        self.logger_categorizacao = logging.getLogger('categorizacao')
        self.logger_categorizacao.setLevel(logging.INFO)
        fh = logging.FileHandler('logs/categorizacao.log')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger_categorizacao.addHandler(fh)

        master.title("Assistente de Contabilidade Português")
        master.geometry("1000x700")

        self.style = ttk.Style(theme="superhero")

        self.conversa = [
            {"role": "system", "content": "És um assistente de contabilidade especializado na legislação portuguesa. Respondes sempre em português de Portugal e forneces informações precisas sobre contabilidade e fiscalidade em Portugal."}
        ]

        self.categorias = ["Geral", "IRS", "IRC", "IVA", "Obrigações Declarativas"]

        self.fila_processamento = queue.Queue()
        self.processamento_ativo = False

        self.gestor_obrigacoes = GestorObrigacoesFiscais()
        self.criar_widgets()
        self.carregar_obrigacoes_iniciais()

        self.pdf_last_modified = {}
        self.verificar_atualizacoes_thread = threading.Thread(target=self.verificar_atualizacoes_periodicas, daemon=True)
        self.verificar_atualizacoes_thread.start()

        # Iniciar a conversa após a criação dos widgets
        self.iniciar_conversa()

    def criar_widgets(self):
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Criar um notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=YES)

        # Aba de chat
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")

        self.criar_widgets_chat()

        # Aba de obrigações fiscais
        self.obrigacoes_fiscais_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.obrigacoes_fiscais_frame, text="Obrigações Fiscais")

        # Aba de obrigações declarativas
        self.obrigacoes_declarativas_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.obrigacoes_declarativas_frame, text="Obrigações Declarativas")

        self.criar_widgets_obrigacoes()

        # Adicione esta linha no final do método
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.pack(fill=X, pady=(10, 0))

    def criar_widgets_chat(self):
        self.chat_area = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.chat_area.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

        input_frame = ttk.Frame(self.chat_frame)
        input_frame.pack(fill=X, padx=10, pady=10)

        self.input_field = ttk.Entry(input_frame)
        self.input_field.pack(side=LEFT, fill=X, expand=YES)
        self.input_field.bind("<Return>", self.enviar_mensagem)

        send_button = ttk.Button(input_frame, text="Enviar", command=self.enviar_mensagem, style="success.TButton")
        send_button.pack(side=RIGHT, padx=(5, 0))

        button_frame = ttk.Frame(self.chat_frame)
        button_frame.pack(fill=X, padx=10, pady=10)

        ttk.Button(button_frame, text="Guardar Conversa", command=self.guardar_conversa_gui, style="info.TButton").pack(side=LEFT, padx=2)
        ttk.Button(button_frame, text="Carregar Conversa", command=self.carregar_conversa, style="warning.TButton").pack(side=LEFT, padx=2)
        ttk.Button(button_frame, text="Nova Conversa", command=self.nova_conversa, style="danger.TButton").pack(side=LEFT, padx=2)
        ttk.Button(button_frame, text="Upload Fatura", command=self.upload_fatura, style="primary.Outline.TButton").pack(side=LEFT, padx=2)
        ttk.Button(button_frame, text="Atualizar Obrigações", command=self.atualizar_obrigacoes_fiscais, style="success.Outline.TButton").pack(side=LEFT, padx=2)

    def criar_widgets_obrigacoes(self):
        # Obrigações Fiscais
        self.obrigacoes_fiscais_tree = ttk.Treeview(self.obrigacoes_fiscais_frame, columns=("Nome", "Prazo", "Descrição"), show="headings")
        self.obrigacoes_fiscais_tree.heading("Nome", text="Nome")
        self.obrigacoes_fiscais_tree.heading("Prazo", text="Prazo")
        self.obrigacoes_fiscais_tree.heading("Descrição", text="Descrição")
        self.obrigacoes_fiscais_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Obrigações Declarativas
        self.obrigacoes_declarativas_tree = ttk.Treeview(self.obrigacoes_declarativas_frame, columns=("Nome", "Prazo", "Descrição"), show="headings")
        self.obrigacoes_declarativas_tree.heading("Nome", text="Nome")
        self.obrigacoes_declarativas_tree.heading("Prazo", text="Prazo")
        self.obrigacoes_declarativas_tree.heading("Descrição", text="Descrição")
        self.obrigacoes_declarativas_tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def carregar_obrigacoes_iniciais(self):
        caminho_pdf_fiscal = os.path.join("data", "Obrigacoes_pagamento.pdf")
        caminho_pdf_declarativo = os.path.join("data", "Obrigacoes_declarativas.pdf")

        logging.info(f"Tentando carregar obrigações de: {caminho_pdf_fiscal} e {caminho_pdf_declarativo}")

        obrigacoes_carregadas = False

        if os.path.exists(caminho_pdf_fiscal):
            obrigacoes_fiscais = carregar_obrigacoes_de_arquivo(caminho_pdf_fiscal)
            for ob in obrigacoes_fiscais:
                self.gestor_obrigacoes.adicionar_obrigacao(ob)
            logging.info(f"Carregadas {len(obrigacoes_fiscais)} obrigações fiscais")
            obrigacoes_carregadas = True
        else:
            logging.error(f"Arquivo não encontrado: {caminho_pdf_fiscal}")

        if os.path.exists(caminho_pdf_declarativo):
            obrigacoes_declarativas = carregar_obrigacoes_de_arquivo(caminho_pdf_declarativo)
            for ob in obrigacoes_declarativas:
                self.gestor_obrigacoes.adicionar_obrigacao(ob)
            logging.info(f"Carregadas {len(obrigacoes_declarativas)} obrigações declarativas")
            obrigacoes_carregadas = True
        else:
            logging.error(f"Arquivo não encontrado: {caminho_pdf_declarativo}")

        if obrigacoes_carregadas:
            self.atualizar_lista_obrigacoes()
            logging.info("Lista de obrigações atualizada")
        else:
            logging.warning("Nenhuma obrigação foi carregada")

    def atualizar_lista_obrigacoes(self):
        logging.info("Iniciando atualização da lista de obrigações")
        # Limpar as listas atuais
        for tree in [self.obrigacoes_fiscais_tree, self.obrigacoes_declarativas_tree]:
            for i in tree.get_children():
                tree.delete(i)

        # Adicionar obrigações às respectivas listas
        obrigacoes_fiscais = 0
        obrigacoes_declarativas = 0
        for ob in self.gestor_obrigacoes.obrigacoes:
            if ob.tipo == "fiscal":
                self.obrigacoes_fiscais_tree.insert("", "end", values=(ob.nome, ob.prazo.strftime("%d/%m/%Y"), ob.descricao))
                obrigacoes_fiscais += 1
            elif ob.tipo == "declarativa":
                self.obrigacoes_declarativas_tree.insert("", "end", values=(ob.nome, ob.prazo.strftime("%d/%m/%Y"), ob.descricao))
                obrigacoes_declarativas += 1

        logging.info(f"Atualizadas {obrigacoes_fiscais} obrigações fiscais e {obrigacoes_declarativas} obrigações declarativas na interface")

    def atualizar_chat(self, mensagem, sender=None):
        self.chat_area.config(state='normal')
        if sender:
            self.chat_area.insert(tk.END, f"{sender}: ", "bold")
        
        partes = re.split(r'(\*\*.*?\*\*)', mensagem)
        for parte in partes:
            if parte.startswith('**') and parte.endswith('**'):
                texto_negrito = parte.strip('*')
                self.chat_area.insert(tk.END, texto_negrito, "bold")
            else:
                self.chat_area.insert(tk.END, parte)
        
        self.chat_area.insert(tk.END, "\n\n")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def enviar_mensagem(self, event=None):
        mensagem = self.input_field.get().strip()
        if not mensagem:
            messagebox.showwarning("Aviso", "Por favor, insira uma mensagem.")
            return

        logging.info(f"Enviando mensagem: {mensagem}")
        self.atualizar_chat(mensagem, "Você")
        self.conversa.append({"role": "user", "content": mensagem})
        self.input_field.delete(0, tk.END)

        resposta = gerar_resposta(self.conversa)
        if resposta:
            self.atualizar_chat(resposta)
            self.conversa.append({"role": "assistant", "content": resposta})
        else:
            self.atualizar_chat("Desculpe, não foi possível gerar uma resposta. Por favor, tente novamente.")

    def upload_fatura(self):
        logging.info("A iniciar upload de fatura(s)")
        ficheiros = filedialog.askopenfilenames(filetypes=[("Ficheiros PDF", "*.pdf"), ("Todos os ficheiros", "*.*")])
        if not ficheiros:
            logging.info("Upload de fatura(s) cancelado pelo utilizador")
            return

        for ficheiro in ficheiros:
            self.fila_processamento.put(ficheiro)

        self.atualizar_chat(f"Adicionadas {len(ficheiros)} fatura(s) à fila de processamento.")
        
        if not self.processamento_ativo:
            self.iniciar_processamento()

    def iniciar_processamento(self):
        self.processamento_ativo = True
        threading.Thread(target=self.processar_fila).start()

    def processar_fila(self):
        total_faturas = self.fila_processamento.qsize()
        
        progress_geral = ttk.Progressbar(self.progress_frame, orient="horizontal", length=200, mode="determinate", maximum=total_faturas)
        progress_geral.pack(fill=X, padx=5, pady=5)
        
        label_geral = ttk.Label(self.progress_frame, text="Progresso geral: 0%")
        label_geral.pack(padx=5)

        progress_individual = ttk.Progressbar(self.progress_frame, orient="horizontal", length=200, mode="determinate", maximum=100)
        progress_individual.pack(fill=X, padx=5, pady=5)
        
        label_individual = ttk.Label(self.progress_frame, text="Processando: ")
        label_individual.pack(padx=5)

        faturas_processadas = 0
        while not self.fila_processamento.empty():
            ficheiro = self.fila_processamento.get()
            nome_ficheiro = os.path.basename(ficheiro)
            label_individual.config(text=f"Processando: {nome_ficheiro}")
            
            self.processar_fatura(ficheiro, progress_individual)
            self.fila_processamento.task_done()
            
            faturas_processadas += 1
            progresso = (faturas_processadas / total_faturas) * 100
            progress_geral['value'] = faturas_processadas
            label_geral.config(text=f"Progresso geral: {progresso:.1f}%")
            self.master.update_idletasks()

        progress_geral.destroy()
        label_geral.destroy()
        progress_individual.destroy()
        label_individual.destroy()

        self.processamento_ativo = False
        self.atualizar_chat("Processamento de todas as faturas concluído.")

    def categorizar_item_fatura(self, descricao):
        try:
            if isinstance(descricao, str):
                descricao_lower = descricao.lower()
                descricao_vetorizada = self.vectorizer.transform([descricao_lower])
                categoria_prevista = self.modelo.predict(descricao_vetorizada)[0]
                self.logger_categorizacao.info(f"Item: '{descricao}' - Categoria: {categoria_prevista}")
                return categoria_prevista
            else:
                raise ValueError(f"A descrição deve ser uma string, não {type(descricao)}")
        except Exception as e:
            self.logger_categorizacao.error(f"Erro ao categorizar item: {str(e)}")
            return "Erro na categorização"

    def processar_fatura(self, ficheiro, progress):
        if not validar_pdf(ficheiro):
            self.atualizar_chat(f"Aviso: O ficheiro '{os.path.basename(ficheiro)}' não é um PDF válido. A ignorar.")
            return

        logging.info(f"A processar fatura: {ficheiro}")
        self.atualizar_chat(f"A processar fatura: {os.path.basename(ficheiro)}")

        try:
            progress['value'] = 10
            self.master.update_idletasks()
            
            texto_fatura = extrair_texto_pdf(ficheiro)

            if texto_fatura.startswith("Erro"):
                self.atualizar_chat(f"Erro no processamento da fatura '{os.path.basename(ficheiro)}': {texto_fatura}")
                return

            if not texto_fatura:
                self.atualizar_chat(f"Não foi possível extrair texto da fatura '{os.path.basename(ficheiro)}'. O ficheiro pode estar vazio ou corrompido.")
                return

            progress['value'] = 30
            self.master.update_idletasks()
            
            layout_info = detect_invoice_layout(texto_fatura)
            
            progress['value'] = 50
            self.master.update_idletasks()
            
            dados_estruturados = extrair_dados_estruturados(texto_fatura, layout_info)
            
            categoria_geral = self.categorizar_item_fatura(texto_fatura)
            dados_estruturados['categoria_geral_prevista'] = categoria_geral

            obrigacoes_relevantes = self.verificar_obrigacoes_relevantes(dados_estruturados)

            progress['value'] = 70
            self.master.update_idletasks()

            prompt = f"""Analise esta fatura e forneça um resumo conciso com as seguintes informações:

1. Tipo de fatura
2. Número da fatura
3. Nome do cliente (se disponível)
4. NIF do cliente (se disponível)
5. Data de emissão
6. Valor total a pagar
7. Valor total do IVA
8. Categoria geral da fatura
9. Método de pagamento (se disponível)

Itens faturados (apenas se houver informações detalhadas):
- Liste apenas os itens com descrição e quantidade disponíveis

Obrigações fiscais relevantes:
{obrigacoes_relevantes}

Notas importantes:
- Inclua apenas se houver informações críticas ou ações necessárias

Texto completo da fatura para referência:

{texto_fatura[:4000]}"""

            self.conversa.append({"role": "user", "content": prompt})
            
            resposta = gerar_resposta(self.conversa)
            if resposta:
                self.atualizar_chat(f"Análise da fatura '{os.path.basename(ficheiro)}':")
                self.atualizar_chat(resposta)
                self.conversa.append({"role": "assistant", "content": resposta})
                
                self.salvar_analise_fatura(ficheiro, resposta)
            else:
                self.atualizar_chat(f"Desculpe, não foi possível processar a fatura '{os.path.basename(ficheiro)}'. Por favor, tente novamente.")

            progress['value'] = 100
            self.master.update_idletasks()

        except Exception as e:
            logging.error(f"Erro ao processar fatura '{ficheiro}': {str(e)}", exc_info=True)
            self.atualizar_chat(f"Erro ao processar a fatura '{os.path.basename(ficheiro)}': {str(e)}")

    def verificar_obrigacoes_relevantes(self, dados_estruturados):
        obrigacoes_relevantes = []
        data_emissao_str = dados_estruturados.get('data_emissao')
        
        if data_emissao_str:
            try:
                data_emissao = datetime.strptime(data_emissao_str, "%Y-%m-%d")
                
                # Verificar obrigações próximas à data de emissão
                proximas_obrigacoes = self.gestor_obrigacoes.obter_proximas_obrigacoes(dias=30)
                for obrigacao in proximas_obrigacoes:
                    if abs((obrigacao.prazo - data_emissao.date()).days) <= 30:
                        obrigacoes_relevantes.append(f"{obrigacao.nome} - {obrigacao.prazo.strftime('%d/%m/%Y')}")
            except ValueError:
                logging.error(f"Formato de data inválido: {data_emissao_str}")
        else:
            logging.warning("Data de emissão não encontrada nos dados estruturados")

        # Verificar obrigações específicas com base na categoria
        categoria = dados_estruturados.get('categoria_geral_prevista', '')
        if "IVA" in categoria:
            obrigacoes_relevantes.append("Lembre-se de incluir esta fatura na próxima declaração de IVA.")
        elif "IRC" in categoria:
            obrigacoes_relevantes.append("Esta fatura pode ser relevante para o cálculo do IRC.")
        
        if obrigacoes_relevantes:
            return "Obrigações fiscais relevantes:\n" + "\n".join(obrigacoes_relevantes)
        else:
            return "Não foram identificadas obrigações fiscais específicas relacionadas a esta fatura."

    def salvar_analise_fatura(self, caminho_fatura, analise):
        nome_arquivo = os.path.splitext(os.path.basename(caminho_fatura))[0] + "_analise.json"
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(analise, f, ensure_ascii=False, indent=4)
        self.atualizar_chat(f"Análise da fatura salva em {nome_arquivo}")

    def guardar_conversa_gui(self):
        if len(self.conversa) <= 1:
            messagebox.showinfo("Aviso", "Não há conversa para guardar.")
            return

        nome_ficheiro = self.guardar_conversa(self.conversa)
        if nome_ficheiro:
            messagebox.showinfo("Conversa Guardada", f"Conversa guardada em {nome_ficheiro}")
        else:
            messagebox.showerror("Erro", "Não foi possível guardar a conversa.")

    def carregar_conversa(self):
        ficheiro = filedialog.askopenfilename(filetypes=[("Ficheiros de texto", "*.txt")])
        if not ficheiro:
            return

        try:
            with open(ficheiro, "r", encoding="utf-8") as f:
                conteudo = f.read()
            
            self.nova_conversa()  # Limpa a conversa atual
            self.atualizar_chat(f"Conversa carregada de {ficheiro}\n")
            self.atualizar_chat(conteudo)

            # Reconstruir a conversa a partir do ficheiro
            linhas = conteudo.split("\n")
            for i in range(0, len(linhas), 3):  # Cada mensagem ocupa 2 linhas + 1 linha em branco
                if i+1 < len(linhas):
                    role = linhas[i].split(":")[0].lower()
                    content = linhas[i].split(":", 1)[1].strip() if ":" in linhas[i] else ""
                    self.conversa.append({"role": role, "content": content})
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a conversa: {str(e)}")

    def nova_conversa(self):
        self.conversa = [
            {
                "role": "system",
                "content": (
                    "Atuas como um assistente especializado em contabilidade, com foco na legislação portuguesa. "
                    "As tuas respostas devem ser sempre em português de Portugal e fornecer informações rigorosas e atualizadas "
                    "sobre contabilidade e fiscalidade aplicáveis em Portugal."
                )
            }
        ]
        self.atualizar_chat("Nova conversa iniciada. Como posso ajudar?")

    def mudar_categoria(self, event):
        categoria = self.categoria_var.get()
        self.atualizar_chat(f"Categoria alterada para {categoria}. Como posso ajudar com questões de {categoria}?")

    def iniciar_conversa(self):
        self.atualizar_chat("Bem-vindo ao Assistente de Contabilidade Português!")
        self.atualizar_chat(AVISO_LEGAL)
        self.atualizar_chat("Como posso ajudar você hoje?")

    def verificar_atualizacoes_periodicas(self):
        while True:
            self.verificar_atualizacoes_pdfs(silencioso=True)
            time.sleep(3600)  # Verifica a cada hora

    def verificar_atualizacoes_pdfs(self, silencioso=False):
        caminho_pdf_fiscal = os.path.join("data", "Obrigacoes_pagamento.pdf")
        caminho_pdf_declarativo = os.path.join("data", "Obrigacoes_declarativas.pdf")
        
        atualizacoes = []

        for caminho in [caminho_pdf_fiscal, caminho_pdf_declarativo]:
            if os.path.exists(caminho):
                ultima_modificacao = os.path.getmtime(caminho)
                if caminho not in self.pdf_last_modified or ultima_modificacao > self.pdf_last_modified[caminho]:
                    atualizacoes.append(caminho)
                    self.pdf_last_modified[caminho] = ultima_modificacao

        if atualizacoes and not silencioso:
            self.oferecer_atualizacao(atualizacoes)
        elif atualizacoes and silencioso:
            self.atualizar_obrigacoes_fiscais(silencioso=True)

    def oferecer_atualizacao(self, arquivos_atualizados):
        mensagem = "Os seguintes arquivos de obrigações fiscais foram atualizados:\n\n"
        mensagem += "\n".join(arquivos_atualizados)
        mensagem += "\n\nDeseja reprocessar as obrigações fiscais?"

        if messagebox.askyesno("Atualizações Detectadas", mensagem):
            self.atualizar_obrigacoes_fiscais()

    def atualizar_obrigacoes_fiscais(self, silencioso=False):
        caminho_pdf_fiscal = os.path.join("data", "Obrigacoes_pagamento.pdf")
        caminho_pdf_declarativo = os.path.join("data", "Obrigacoes_declarativas.pdf")

        if not os.path.exists(caminho_pdf_fiscal) or not os.path.exists(caminho_pdf_declarativo):
            if not silencioso:
                messagebox.showerror("Erro", "Arquivos de obrigações fiscais não encontrados.")
            return

        try:
            obrigacoes_fiscais = carregar_obrigacoes_de_arquivo(caminho_pdf_fiscal)
            obrigacoes_declarativas = carregar_obrigacoes_de_arquivo(caminho_pdf_declarativo)

            self.gestor_obrigacoes = GestorObrigacoesFiscais()  # Resetar o gestor
            for ob in obrigacoes_fiscais + obrigacoes_declarativas:
                self.gestor_obrigacoes.adicionar_obrigacao(ob)

            caminho_json = os.path.join("data", "obrigacoes_fiscais.json")
            save_obligations(self.gestor_obrigacoes, caminho_json)

            self.atualizar_lista_obrigacoes()
            if not silencioso:
                messagebox.showinfo("Sucesso", "Obrigações fiscais e declarativas atualizadas com sucesso.")
                self.atualizar_chat("Obrigações fiscais e declarativas atualizadas. Verifique as abas correspondentes para ver as atualizações.")
        except Exception as e:
            if not silencioso:
                messagebox.showerror("Erro", f"Erro ao atualizar obrigações: {str(e)}")
            logging.error(f"Erro ao atualizar obrigações: {str(e)}")

    def exibir_obrigacoes_fiscais(self):
        proximas_obrigacoes = self.gestor_obrigacoes.obter_proximas_obrigacoes()
        janela_obrigacoes = tk.Toplevel(self.master)
        janela_obrigacoes.title("Próximas Obrigações Fiscais")
        
        texto_obrigacoes = scrolledtext.ScrolledText(janela_obrigacoes, wrap=tk.WORD, width=60, height=20)
        texto_obrigacoes.pack(padx=10, pady=10)
        
        for ob in proximas_obrigacoes:
            texto_obrigacoes.insert(tk.END, f"{ob.tipo.capitalize()}: {ob.nome}\n")
            texto_obrigacoes.insert(tk.END, f"Data: {ob.prazo.strftime('%d/%m/%Y')}\n")
            texto_obrigacoes.insert(tk.END, f"Descrição: {ob.descricao}\n\n")
        
        texto_obrigacoes.config(state=tk.DISABLED)

    def responder(self, pergunta):
        if "obrigações fiscais" in pergunta.lower():
            proximas_obrigacoes = self.gestor_obrigacoes.obter_proximas_obrigacoes()
            resposta = "Próximas obrigações fiscais e declarativas:\n"
            for ob in proximas_obrigacoes:
                resposta += f"{ob.tipo.capitalize()}: {ob.nome} - {ob.prazo.strftime('%d/%m/%Y')} - {ob.descricao}\n"
            return resposta
        # ... (resto do código existente)