"""Trilha A: cadeias e construção. Etapa 5 do guia."""

from base import calcular_hash, reduzir

# Uma linha guarda duas PALAVRAS, não o hash final.
Pares = list[tuple[str, str]]


def fim_da_cadeia(inicio: str, palavras: list[str], largura: int,
                  modo: str = "cores") -> str:
    """TODO A1: aplicar exatamente largura passos H -> R e devolver p_t.

    Para t passos, hasheamos p_0 até p_(t-1); p_t é só o final guardado.
    Colunas de redução: 0, 1, ..., t-1. Exigir largura >= 1 (ValueError).
    Não guardar toda a cadeia no retorno.
    """
    raise NotImplementedError("A1: implemente fim_da_cadeia; veja a etapa 5")


def construir(palavras: list[str], altura: int, largura: int, semente: int,
              modo: str = "cores") -> Pares:
    """TODO A2: sortear inícios distintos e devolver os pares início/fim.

    Use random.Random(semente).sample(palavras, altura), nesta ordem.
    Exigir 1 <= altura <= len(palavras) e largura >= 1 (ValueError).
    Cada início gera uma linha. Mantenha linhas que tenham o mesmo final.
    Não usar o gerador aleatório global nem tentar completar a cobertura.
    """
    raise NotImplementedError("A2: implemente construir; veja a etapa 5")
