"""Trilha B: índice e busca. Etapa 6 do guia."""

from base import calcular_hash, reduzir

Indice = dict[str, list[str]]  # final -> TODOS os inícios que chegam nele


def indexar(pares: list[tuple[str, str]]) -> Indice:
    """TODO C1: agrupar inícios pelo final; preservar repetições de final."""
    raise NotImplementedError("C1: implemente indexar; veja a etapa 6")


def buscar(alvo: str, palavras: list[str], indice: Indice, largura: int,
           modo: str = "cores") -> str | None:
    """TODO C2: buscar um hash sem receber a senha que originou o alvo.

    Tentar posições de t-1 até 0. Em cada hipótese, caminhar para a direita
    usando as cores daquela posição até t-1. Consultar o final no índice.
    Reconstruir os inícios candidatos e comparar H(p) com o alvo antes de R.
    Só devolver p após confirmar o hash; continuar após candidatos falsos.
    Se nenhuma hipótese confirmar, devolver None. Exigir largura >= 1.
    Não percorrer o dicionário inteiro para completar buscas sem sucesso.
    """
    raise NotImplementedError("C2: implemente buscar; veja a etapa 6")
