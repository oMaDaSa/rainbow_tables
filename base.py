"""Base comum da dupla. Leia as etapas 2 e 3 de guia.html antes de preencher."""

import hashlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
LISTA = RAIZ / "dados" / "diceware.wordlist.asc"


def carregar_palavras(caminho: Path = LISTA) -> list[str]:
    """TODO B1: devolver as palavras em ordem crescente do código Diceware.

    Aceitar só linhas com código de cinco dígitos de 1 a 6 e uma palavra.
    Ignorar o cabeçalho e a assinatura PGP. Não remover pontuação das palavras.
    Exigir 7.776 códigos distintos e 7.776 palavras distintas; caso contrário,
    levantar ValueError. A primeira palavra deve ser 'a', a última, '@'.
    Caminho inexistente deve manter o FileNotFoundError do Python.
    """
    raise NotImplementedError("B1: implemente carregar_palavras; veja a etapa 2")


def calcular_hash(senha: str) -> str:
    """Hash fornecido no slide 47. Retorna 64 caracteres hexadecimais."""
    return hashlib.sha256(b"GBC083" + senha.encode("utf-8")).hexdigest()


def reduzir(h: str, coluna: int, palavras: list[str], modo: str = "cores") -> str:
    """TODO B2: transformar um hash em uma palavra da lista.

    Convenção do guia: cores usa a coluna; fixa usa sempre a cor zero.
    Mistura: SHA-256 dos bytes UTF-8 do texto f'{cor}:{h}'.
    Índice: inteiro hexadecimal da mistura, módulo len(palavras).
    Essa segunda aplicação de SHA-256 faz parte da redução, não altera H.
    Exigir coluna >= 0, lista não vazia e modo em {'cores', 'fixa'};
    para esses argumentos inválidos, levantar ValueError.
    Os chamadores fornecem h hexadecimal válido, em minúsculas.
    """
    raise NotImplementedError("B2: implemente reduzir; veja a etapa 3")
