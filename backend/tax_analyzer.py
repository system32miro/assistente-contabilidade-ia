from dataclasses import dataclass
from typing import Dict, List, Tuple
import logging
import os
from datetime import datetime

@dataclass
class TaxRate:
    standard: float
    intermediate: float
    reduced: float
    exempt: float = 0.0

@dataclass
class TaxRegime:
    name: str
    vat: TaxRate
    irc: float
    description: str

class TaxAnalyzer:
    def __init__(self):
        self.tax_regimes: Dict[str, TaxRegime] = {
            "geral": TaxRegime(
                name="Regime Geral",
                vat=TaxRate(standard=23.0, intermediate=13.0, reduced=6.0),
                irc=21.0,
                description="Regime fiscal geral aplicável à maioria das empresas em Portugal."
            ),
            "madeira": TaxRegime(
                name="Regime da Madeira",
                vat=TaxRate(standard=22.0, intermediate=12.0, reduced=5.0),
                irc=14.7,
                description="Regime fiscal especial aplicável na Região Autónoma da Madeira."
            ),
            "acores": TaxRegime(
                name="Regime dos Açores",
                vat=TaxRate(standard=18.0, intermediate=9.0, reduced=4.0),
                irc=16.8,
                description="Regime fiscal especial aplicável na Região Autónoma dos Açores."
            ),
            "pme": TaxRegime(
                name="Regime PME",
                vat=TaxRate(standard=23.0, intermediate=13.0, reduced=6.0),
                irc=17.0,
                description="Regime fiscal para Pequenas e Médias Empresas com taxa de IRC reduzida."
            )
        }
        self.vat_categories = {
            "standard": ["serviços", "consultoria", "equipamentos", "software"],
            "intermediate": ["hotelaria", "restauração"],
            "reduced": ["alimentação", "livros", "medicamentos"],
            "exempt": ["saúde", "educação", "serviços financeiros"]
        }
        self.category_to_tax_mapping = {
            "Serviços de Marketing": "standard",
            "Formação e Desenvolvimento": "exempt",
            "Telecomunicações": "standard",
            "Serviços de Manutenção": "standard",
            "Serviços de Auditoria": "standard",
            "Licenciamento de Software": "standard",
            "Serviços Jurídicos": "standard",
            "Seguros": "exempt",
            "Despesas de Transporte e Logística": "standard",
            "Material de Escritório": "standard",
            "Serviços de Consultoria": "standard",
            "Energia e Utilidades": "standard",
            "Serviços de Contabilidade": "standard",
            "Mobiliário e Equipamento de Escritório": "standard",
            "Equipamentos Informáticos": "standard",
        }

        # Configuração do logging
        self.logger = logging.getLogger('TaxAnalyzer')
        self.logger.setLevel(logging.DEBUG)
        
        # Criar diretório de logs se não existir
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configurar o handler para arquivo
        log_file = os.path.join(log_dir, f'tax_calculations_{datetime.now().strftime("%Y%m%d")}.log')
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Definir o formato do log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Adicionar o handler ao logger
        self.logger.addHandler(file_handler)

    def get_tax_regime(self, regime_name: str) -> TaxRegime:
        regime = self.tax_regimes.get(regime_name.lower(), self.tax_regimes["geral"])
        self.logger.info(f"Regime fiscal selecionado: {regime.name}")
        return regime

    def validate_vat_rate(self, category: str, applied_rate: float, regime: TaxRegime) -> bool:
        for rate_type, categories in self.vat_categories.items():
            if any(cat in category.lower() for cat in categories):
                expected_rate = getattr(regime.vat, rate_type)
                is_valid = abs(applied_rate - expected_rate) < 0.01
                self.logger.info(f"Validação de taxa de IVA: Categoria={category}, Taxa Aplicada={applied_rate}%, Taxa Esperada={expected_rate}%, Válido={is_valid}")
                return is_valid
        self.logger.warning(f"Categoria não reconhecida para validação de IVA: {category}")
        return False

    def calculate_vat(self, item: Dict[str, any], regime_name: str = "geral") -> Tuple[float, float]:
        regime = self.get_tax_regime(regime_name)
        amount = item.get('valor', 0)
        category = item.get('categoria', '').lower()
        
        for rate_type, categories in self.vat_categories.items():
            if any(cat in category for cat in categories):
                rate = getattr(regime.vat, rate_type)
                break
        else:
            rate = regime.vat.standard
            self.logger.warning(f"Categoria não reconhecida. Usando taxa padrão para: {category}")
        
        vat_amount = amount * (rate / 100)
        
        if not self.validate_vat_rate(category, rate, regime):
            self.logger.error(f"Taxa de IVA inválida ({rate}%) para a categoria: {category}")
            raise ValueError(f"Taxa de IVA inválida ({rate}%) para a categoria: {category}")
        
        self.logger.info(f"Cálculo de IVA: Valor={amount}€, Categoria={category}, Taxa={rate}%, IVA={vat_amount}€")
        return vat_amount, rate

    def calculate_irc(self, total_income: float, expenses: float, regime_name: str = "geral") -> Tuple[float, float]:
        regime = self.get_tax_regime(regime_name)
        taxable_profit = max(0, total_income - expenses)
        irc_amount = taxable_profit * (regime.irc / 100)
        
        if irc_amount < 0:
            self.logger.error(f"Cálculo de IRC inválido: valor negativo. Rendimento={total_income}€, Despesas={expenses}€")
            raise ValueError("O valor do IRC não pode ser negativo.")
        if irc_amount > taxable_profit:
            self.logger.error(f"Cálculo de IRC inválido: valor maior que o lucro tributável. IRC={irc_amount}€, Lucro Tributável={taxable_profit}€")
            raise ValueError("O valor do IRC não pode ser maior que o lucro tributável.")
        
        self.logger.info(f"Cálculo de IRC: Rendimento={total_income}€, Despesas={expenses}€, Lucro Tributável={taxable_profit}€, Taxa={regime.irc}%, IRC={irc_amount}€")
        return irc_amount, regime.irc

    def get_applicable_vat_rates(self, regime_name: str = "geral") -> List[str]:
        regime = self.get_tax_regime(regime_name)
        rates = [rate for rate in ["standard", "intermediate", "reduced", "exempt"] 
                 if getattr(regime.vat, rate) > 0]
        self.logger.info(f"Taxas de IVA aplicáveis para {regime.name}: {', '.join(rates)}")
        return rates

    def get_tax_category(self, category: str) -> str:
        tax_category = self.category_to_tax_mapping.get(category, "standard")
        self.logger.info(f"Categoria fiscal para '{category}': {tax_category}")
        return tax_category

    def analyze_invoice(self, invoice: Dict[str, any], regime_name: str = "geral") -> Dict[str, any]:
        self.logger.info(f"Iniciando análise de fatura: {invoice}")
        try:
            category = invoice.get('categoria', 'Não especificada')
            tax_category = self.get_tax_category(category)
            vat_amount, vat_rate = self.calculate_vat(invoice, regime_name)
            regime = self.get_tax_regime(regime_name)
            
            analysis = {
                "invoice_total": invoice.get('valor', 0),
                "vat_amount": vat_amount,
                "vat_rate": vat_rate,
                "net_amount": invoice.get('valor', 0) - vat_amount,
                "tax_regime": regime.name,
                "category": category,
                "tax_category": tax_category,
                "irc_rate": regime.irc
            }
            
            if analysis["net_amount"] < 0:
                self.logger.error(f"Análise de fatura inválida: valor líquido negativo. Análise={analysis}")
                raise ValueError("O valor líquido da fatura não pode ser negativo.")
            
            self.logger.info(f"Análise de fatura concluída: {analysis}")
            return analysis
        except ValueError as e:
            self.logger.error(f"Erro na análise de fatura: {str(e)}")
            return {"error": str(e)}

# Exemplo de uso:
if __name__ == "__main__":
    analyzer = TaxAnalyzer()
    
    # Exemplo de análise de fatura
    invoice = {
        "valor": 1000,
        "categoria": "Serviços de Consultoria"
    }
    analysis = analyzer.analyze_invoice(invoice, "geral")
    print("Análise da fatura:")
    for key, value in analysis.items():
        print(f"{key}: {value}")

    # Exemplo de cálculo de IRC
    total_income = 100000
    expenses = 70000
    try:
        irc, irc_rate = analyzer.calculate_irc(total_income, expenses, "pme")
        print(f"\nCálculo de IRC para PME:")
        print(f"Rendimento total: {total_income}€")
        print(f"Despesas: {expenses}€")
        print(f"IRC a pagar: {irc:.2f}€ (taxa: {irc_rate}%)")
    except ValueError as e:
        print(f"Erro no cálculo do IRC: {e}")

    # Listar taxas de IVA aplicáveis nos Açores
    rates = analyzer.get_applicable_vat_rates("acores")
    print(f"\nTaxas de IVA aplicáveis nos Açores: {', '.join(rates)}")

    # Teste de validação com categoria inválida
    invalid_invoice = {
        "valor": 500,
        "categoria": "Categoria Inválida"
    }
    invalid_analysis = analyzer.analyze_invoice(invalid_invoice, "geral")
    print("\nAnálise de fatura com categoria inválida:")
    print(invalid_analysis)