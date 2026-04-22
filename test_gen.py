import subprocess
import time

def run_test(option):
    # Option 1: Bradesco, 2: Nubank, 3: Unibanco
    # Input sequence:
    # Option
    # Cedente
    # Sacado
    # CPF/CNPJ
    # Valor
    # Data Vencimento
    # Nosso Numero
    # Agencia
    # Conta
    # Numero Documento
    
    inputs = [
        str(option),
        "Empresa de Teste LTDA",
        "Fulano de Tal",
        "123.456.789-00",
        "1500.50",
        "2026-12-31",
        "12345",
        "123",
        "45678",
        "DOC123"
    ]
    
    input_str = "\n".join(inputs) + "\n"
    
    process = subprocess.Popen(
        ["java", "-jar", "target/boleto-builder-system-1.0.0.jar"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=input_str)
    return stdout

print("--- TESTE BRADESCO ---")
print(run_test(1))
print("\n--- TESTE NUBANK ---")
print(run_test(2))
print("\n--- TESTE UNIBANCO ---")
print(run_test(3))
