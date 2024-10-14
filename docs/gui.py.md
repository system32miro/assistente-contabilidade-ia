# Módulo GUI

## Visão Geral
O módulo `gui.py` implementa a interface gráfica do utilizador para o Assistente de Contabilidade Português. Utiliza a biblioteca `tkinter` e `ttkbootstrap` para criar uma interface moderna e responsiva.

## Classe Principal

### AssistenteContabilidade
Esta classe é responsável por criar e gerir a interface gráfica do assistente.

#### Métodos Principais

##### __init__(self, master)
Inicializa a interface gráfica.

**Parâmetros:**
- `master`: A janela principal da aplicação.

##### upload_fatura(self)
Permite ao utilizador selecionar e carregar faturas em PDF.

**Exemplo de uso:**