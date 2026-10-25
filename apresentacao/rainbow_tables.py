"""Rainbow Tables - GBC083.
Matheus Dantas Santana e Vanessa Dias Ferreira.
Execução: python rainbow_tables.py (Python 3.10+, sem pacotes externos).
"""

import csv
import hashlib
import json
import random
import statistics
from pathlib import Path
from time import perf_counter

RAIZ = Path(__file__).resolve().parent
LISTA = RAIZ / "diceware.wordlist.asc"
if not LISTA.is_file():
    LISTA = RAIZ.parent / "dados" / "diceware.wordlist.asc"
FORMATOS = [(512, 16), (256, 32), (128, 64), (64, 128)]
SEMENTES = [17, 43, 91]

def carregar_palavras(caminho: Path = LISTA) -> list[str]:
    """Devolver as palavras em ordem crescente do código Diceware."""

    codigo_para_palavra = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        campos = linha.split()
        if len(campos) != 2:
            continue
        codigo, palavra = campos
        if len(codigo) != 5 or any(digito not in "123456" for digito in codigo):
            continue
        if codigo in codigo_para_palavra:
            raise ValueError(f"Código Diceware duplicado: {codigo}")
        codigo_para_palavra[codigo] = palavra

    palavras = [codigo_para_palavra[codigo] for codigo in sorted(codigo_para_palavra)]

    if len(set(palavras)) != 7776:
        raise ValueError("A lista deve conter 7.776 códigos e palavras distintos")
    if palavras[0] != "a" or palavras[-1] != "@":
        raise ValueError("A lista deve começar em 'a' e terminar em '@'")

    return palavras


def calcular_hash(senha: str) -> str:
    return hashlib.sha256(b"GBC083" + senha.encode("utf-8")).hexdigest()


def reduzir(h: str, coluna: int, palavras: list[str], modo: str = "cores") -> str:
    """Transformar um hash em uma palavra da lista."""

    if coluna < 0 or not palavras or modo not in {"cores", "fixa"}:
        raise ValueError("Exigidos coluna >= 0, lista não vazia e modo cores ou fixa")

    cor = coluna if modo == "cores" else 0

    mistura = hashlib.sha256(f"{cor}:{h}".encode("utf-8")).hexdigest()
    posicao = int(mistura, 16) % len(palavras)

    return palavras[posicao]

# Uma linha guarda duas PALAVRAS, não o hash final.
Pares = list[tuple[str, str]]


def fim_da_cadeia(inicio: str, palavras: list[str], largura: int, modo: str = "cores") -> str:
    """Aplicar exatamente largura passos H -> R e devolver p_t."""

    if largura < 1:
        raise ValueError("A largura deve ser pelo menos 1")

    atual = inicio

    for coluna in range(largura):
        h = calcular_hash(atual)
        atual = reduzir(h, coluna, palavras, modo)

    return atual


def construir(palavras: list[str], altura: int, largura: int, semente: int, modo: str = "cores") -> Pares:
    """Sortear inícios distintos e devolver os pares início/fim."""
    if not 1 <= altura <= len(palavras) or largura < 1:
        raise ValueError("Exigidos 1 <= altura <= tamanho da lista e largura >= 1")

    inicios = random.Random(semente).sample(palavras, altura)
    pares = []

    for inicio in inicios:
        fim = fim_da_cadeia(inicio, palavras, largura, modo)
        pares.append((inicio, fim))

    return pares

Indice = dict[str, list[str]]  # final -> TODOS os inícios que chegam nele


def indexar(pares: list[tuple[str, str]]) -> Indice:
    """Agrupar inícios pelo final; preservar repetições de final."""
    indice: Indice = {}
    for inicio, fim in pares:
        if fim not in indice:
            indice[fim] = []
        indice[fim].append(inicio)
    return indice


def buscar(alvo: str, palavras: list[str], indice: Indice, largura: int,
           modo: str = "cores") -> str | None:
    """Testar posições e confirmar o hash ao reconstruir os candidatos."""
    if largura < 1:
        raise ValueError("A largura deve ser pelo menos 1")

    for k in range(largura - 1, -1, -1):
        hash_atual = alvo
        for j in range(k, largura):
            palavra = reduzir(hash_atual, j, palavras, modo)
            if j < largura - 1:
                hash_atual = calcular_hash(palavra)

        final_candidato = palavra
        for inicio in indice.get(final_candidato, []):
            atual = inicio
            for coluna in range(largura):
                h = calcular_hash(atual)
                if h == alvo:
                    return atual
                atual = reduzir(h, coluna, palavras, modo)

    return None

def experimentar(formatos=FORMATOS, sementes=SEMENTES,
                 quantidade=200, saida=None):
    """Comparar os formatos usando os mesmos alvos independentes."""
    palavras = carregar_palavras()
    alvos = random.Random(2026).sample(palavras, quantidade)
    hashes = [calcular_hash(p) for p in alvos]
    resultados = []
    for modo in ["cores", "fixa"]:
        for altura, largura in formatos:
            for semente in sementes:
                print(f"{modo}: {altura} x {largura}, semente {semente}", flush=True)
                inicio = perf_counter()
                pares = construir(palavras, altura, largura, semente, modo)
                construcao_s = perf_counter() - inicio
                inicio = perf_counter()
                indice = indexar(pares)
                indexacao_s = perf_counter() - inicio
                tabela_bytes = len(json.dumps(
                    pares, ensure_ascii=False, separators=(",", ":")
                ).encode("utf-8"))
                sucessos, falhas = [], []
                for alvo in hashes:
                    inicio = perf_counter()
                    resposta = buscar(alvo, palavras, indice, largura, modo)
                    tempo = perf_counter() - inicio
                    if resposta is not None:
                        if calcular_hash(resposta) != alvo:
                            raise AssertionError("A busca retornou uma senha incorreta")
                        sucessos.append(tempo)
                    else:
                        falhas.append(tempo)
                resultados.append({
                    "modo": modo, "altura": altura, "largura": largura,
                    "semente": semente, "alvos": quantidade,
                    "acertos": len(sucessos), "taxa_acerto": len(sucessos) / quantidade,
                    "construcao_s": construcao_s, "indexacao_s": indexacao_s,
                    "buscas_s": sum(sucessos) + sum(falhas),
                    "sucesso_medio_ms": statistics.mean(sucessos) * 1000 if sucessos else "",
                    "falha_media_ms": statistics.mean(falhas) * 1000 if falhas else "",
                    "tabela_bytes": tabela_bytes, "finais_distintos": len(indice),
                })
    destino = Path(saida) if saida is not None else RAIZ / "resultados.csv"
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(resultados[0]))
        escritor.writeheader()
        escritor.writerows(resultados)
    print(f"Resultados em {destino}")
    return resultados


if __name__ == "__main__":
    experimentar()
