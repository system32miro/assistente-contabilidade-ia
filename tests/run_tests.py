import unittest
from tests.test_categorizador import TestCategorizador
from main import teste_integracao_categorizacao

if __name__ == "__main__":
    # Executar testes unitários
    unittest.main(verbosity=2, exit=False)

    # Executar teste de integração
    print("\nExecutando teste de integração:")
    teste_integracao_categorizacao()