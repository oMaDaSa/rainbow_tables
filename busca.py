"""Trilha B: índice e busca. Etapa 6 do guia."""

from base import calcular_hash, reduzir

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
    """Buscar um hash sem receber a senha que originou o alvo.

    Tentar posições de t-1 até 0. Em cada hipótese, caminhar para a direita
    usando as cores daquela posição até t-1. Consultar o final no índice.
    Reconstruir os inícios candidatos e comparar H(p) com o alvo antes de R.
    Só devolver p após confirmar o hash; continuar após candidatos falsos.
    Se nenhuma hipótese confirmar, devolver None. Exigir largura >= 1.
    Não percorrer o dicionário inteiro para completar buscas sem sucesso.
    """
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
