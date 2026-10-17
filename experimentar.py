"""Instrumentação pronta; os algoritmos chamados continuam a cargo da dupla.

python experimentar.py --rapido
python experimentar.py
Veja a etapa 8 do guia para interpretar os arquivos.
"""

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from base import LISTA, RAIZ, calcular_hash, carregar_palavras
from busca import buscar, indexar
from construcao import construir

FORMATOS = [(512, 16), (256, 32), (128, 64), (64, 128)]
SEMENTES = [17, 43, 91]
SEMENTE_ALVOS = 2026


def media_ms(valores: list[float]) -> float | str:
    return statistics.mean(valores) * 1000 if valores else ""


def executar(rapido: bool = False) -> Path:
    palavras = carregar_palavras()
    # Alvos independentes da construção; os mesmos em TODOS os cenários.
    quantidade = 20 if rapido else 200
    alvos = random.Random(SEMENTE_ALVOS).sample(palavras, quantidade)
    hashes = [calcular_hash(p) for p in alvos]  # fora do cronômetro da busca
    formatos = [(32, 8)] if rapido else FORMATOS
    sementes = SEMENTES[:1] if rapido else SEMENTES
    instante = datetime.now(timezone.utc)
    pasta = RAIZ / "resultados" / instante.strftime("%Y%m%dT%H%M%S%fZ")
    pasta.mkdir(parents=True)
    metadados = {
        "data_utc": instante.isoformat(), "python": platform.python_version(),
        "sistema": platform.platform(), "processador_reportado": platform.processor(),
        "processadores_logicos": os.cpu_count(),
        "cpu_modelo_preencher": "PREENCHER", "ram_gb_preencher": "PREENCHER",
        "observacoes_carga_energia_preencher": "PREENCHER",
        "lista_sha256": hashlib.sha256(LISTA.read_bytes()).hexdigest(),
        "hash": "SHA-256(b'GBC083' + senha.encode('utf-8')).hexdigest()",
        "reducao": "SHA-256(f'{cor}:{h}'.encode('utf-8')) modulo N; fixa: cor=0",
        "semente_alvos": SEMENTE_ALVOS, "sementes_tabela": sementes,
        "alvos": alvos, "rapido": rapido,
    }
    (pasta / "metadados.json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8")
    campos = ["modo", "altura", "largura", "semente", "alvos", "acertos",
              "taxa_acerto", "construcao_s", "indexacao_s", "buscas_s",
              "sucesso_medio_ms", "falha_media_ms", "tabela_bytes", "finais_distintos"]
    with (pasta / "resumo.csv").open("w", newline="", encoding="utf-8") as resumo, \
         (pasta / "buscas.csv").open("w", newline="", encoding="utf-8") as detalhe:
        escritor = csv.DictWriter(resumo, fieldnames=campos)
        escritor.writeheader()
        buscas = csv.writer(detalhe)
        buscas.writerow(["modo", "altura", "largura", "semente", "alvo_id", "sucesso", "tempo_ms"])
        for modo in ["cores", "fixa"]:
            for altura, largura in formatos:
                for semente in sementes:
                    print(f"{modo}: {altura} x {largura}, semente {semente}", flush=True)
                    inicio = perf_counter()
                    pares = construir(palavras, altura, largura, semente, modo)
                    tempo_construcao = perf_counter() - inicio
                    if len(pares) != altura:
                        raise AssertionError("construir deve preservar todas as linhas")
                    inicio = perf_counter()
                    indice = indexar(pares)
                    tempo_indice = perf_counter() - inicio
                    # Só pares início/fim; metadados estão no arquivo separado.
                    arquivo = pasta / f"tabela_{modo}_{altura}_{largura}_{semente}.json"
                    arquivo.write_text(json.dumps(pares, ensure_ascii=False,
                                                 separators=(",", ":")), encoding="utf-8")
                    sucessos, falhas = [], []
                    for numero, alvo in enumerate(hashes):
                        inicio = perf_counter()
                        resposta = buscar(alvo, palavras, indice, largura, modo)
                        duracao = perf_counter() - inicio
                        # Verificação fora da medição: um retorno incorreto é bug.
                        if resposta is not None and (
                            resposta not in palavras or calcular_hash(resposta) != alvo
                        ):
                            raise AssertionError(f"Busca devolveu candidato inválido: {resposta!r}")
                        ok = resposta is not None
                        (sucessos if ok else falhas).append(duracao)
                        buscas.writerow([modo, altura, largura, semente, numero, int(ok), duracao * 1000])
                    linha = dict(zip(campos, [modo, altura, largura, semente,
                        quantidade, len(sucessos), len(sucessos) / quantidade,
                        tempo_construcao, tempo_indice, sum(sucessos) + sum(falhas),
                        media_ms(sucessos), media_ms(falhas), arquivo.stat().st_size,
                        len(indice)]))
                    escritor.writerow(linha)
                    resumo.flush()
    return pasta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapido", action="store_true", help="Só verificar integração; não usar no relatório")
    args = parser.parse_args()
    try:
        saida = executar(args.rapido)
    except NotImplementedError as erro:
        parser.exit(2, f"Etapa ainda pendente: {erro}\nAbra guia.html e preencha o TODO indicado.\n")
    print(f"Resultados em {saida}")
    print("Complete CPU, RAM e condições em metadados.json antes de comparar máquinas.")
