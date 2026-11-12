
import os
from dotenv import load_dotenv

load_dotenv()

from pipeline.llm_pipeline import chamar_gemini

backup = os.getenv("GEMINI_API_KEY_BACKUP")

if not backup:
    raise RuntimeError("Chave Gemini backup não encontrada.")

# Simula chave principal inválida apenas neste processo.
os.environ["GEMINI_API_KEY"] = "chave_principal_invalida_teste"
os.environ["GEMINI_API_KEY_BACKUP"] = backup

# Usa o modelo configurado no projeto.
print(
    "Modelo:",
    os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
)
print("Testando principal inválida → backup real...")

try:
    resposta, modelo = chamar_gemini(
        "Responda exclusivamente com um objeto JSON válido",
        'Retorne exatamente este JSON: {"status": "OK"}',
        max_output_tokens=1000,
    )

    print("SUCESSO:", resposta)
    print("Modelo:", modelo)

except Exception as erro:
    print("FALHA:", type(erro).__name__)
    print(str(erro)[:600])
    raise
