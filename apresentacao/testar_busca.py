"""Verificações funcionais apresentadas no PDF. Execute: python testar_busca.py"""
from rainbow_tables import (
    calcular_hash, carregar_palavras, construir, indexar, buscar, reduzir,
)

palavras = carregar_palavras()
assert calcular_hash("1234") == (
    "5042f15f93d4f75df9cdff09d062d607eaa0140a930b9023c43ca7cc58609b8f"
)
print("Hash do professor: OK")

assert indexar([("A", "Z"), ("B", "Z")]) == {"Z": ["A", "B"]}
print("Finais repetidos preservados: OK")

consultas = 0
for modo in ["cores", "fixa"]:
    pares = construir(palavras, 8, 5, 17, modo)
    indice = indexar(pares)
    for inicio, _ in pares:
        atual = inicio
        for coluna in range(5):
            alvo = calcular_hash(atual)
            resposta = buscar(alvo, palavras, indice, 5, modo)
            assert resposta is not None and calcular_hash(resposta) == alvo
            consultas += 1
            atual = reduzir(alvo, coluna, palavras, modo)
print(f"Hashes presentes nas cadeias: {consultas}/{consultas}")

pares = construir(palavras, 4, 1, 17)
inicios = {inicio for inicio, _ in pares}
ausente = next(p for p in palavras if p not in inicios)
assert buscar(calcular_hash(ausente), palavras, indexar(pares), 1) is None
print("Alvo fora da cobertura: None (correto)")
