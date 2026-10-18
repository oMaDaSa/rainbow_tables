"""Trilha A: cadeias e construção. Etapa 5 do guia."""

import random

from base import calcular_hash, reduzir

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
