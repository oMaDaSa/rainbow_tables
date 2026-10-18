"""Leitura da lista Diceware, hash da aula e redução por coluna."""

import hashlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
LISTA = RAIZ / "dados" / "diceware.wordlist.asc"


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
