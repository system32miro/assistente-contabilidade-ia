# Módulo Tax Analyzer

## Visão Geral
O módulo `tax_analyzer.py` é responsável pela análise fiscal e cálculos relacionados a impostos no contexto do Assistente de Contabilidade Português.

## Classes Principais

### RegimeFiscal
Uma classe base para representar diferentes regimes fiscais.

### RegimeGeral(RegimeFiscal)
Implementa as regras fiscais para o regime geral.

### RegimeMadeira(RegimeFiscal)
Implementa as regras fiscais específicas para a Região Autónoma da Madeira.

### RegimeAcores(RegimeFiscal)
Implementa as regras fiscais específicas para a Região Autónoma dos Açores.

### RegimePME(RegimeFiscal)
Implementa as regras fiscais para Pequenas e Médias Empresas (PME).

## Funções Principais

### calcular_iva(valor: float, taxa: float) -> float
Calcula o valor do IVA com base no valor e na taxa fornecidos.

### calcular_irc(lucro: float, taxa: float) -> float
Calcula o valor do IRC com base no lucro e na taxa fornecidos.

### validar_taxa_iva(taxa: float) -> bool
Verifica se a taxa de IVA fornecida é válida de acordo com as regras fiscais portuguesas.

## Uso
Para utilizar as funcionalidades de análise fiscal: