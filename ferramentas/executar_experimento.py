"""Executar os cenários e registrar as condições para reproduzir os resultados."""

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import random
import sys

RAIZ = Path(__file__).resolve().parents[1]
PROGRAMA = RAIZ / "apresentacao" / "rainbow_tables.py"


def hardware():
    modelo = platform.processor() or "Não identificado"
    ram = None
    if sys.platform == "win32":
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as chave:
            modelo = winreg.QueryValueEx(chave, "ProcessorNameString")[0].strip()
        kib = ctypes.c_ulonglong()
        if ctypes.windll.kernel32.GetPhysicallyInstalledSystemMemory(ctypes.byref(kib)):
            ram = kib.value / 1024 ** 2
    return {"cpu_modelo": modelo, "ram_instalada_gib": ram,
            "processadores_logicos": os.cpu_count()}


def executar(destino=None, rapido=False):
    spec = importlib.util.spec_from_file_location("rainbow_experimento", PROGRAMA)
    rt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rt)
    instante = datetime.now(timezone.utc)
    pasta = destino or RAIZ / "resultados" / instante.strftime("%Y%m%dT%H%M%SZ")
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    formatos = [(32, 8)] if rapido else rt.FORMATOS
    sementes = [17] if rapido else rt.SEMENTES
    quantidade = 20 if rapido else 200
    palavras = rt.carregar_palavras()
    meta = {
        "data_utc": instante.isoformat(), "python": platform.python_version(),
        "sistema": platform.platform(), **hardware(),
        "codigo_sha256": hashlib.sha256(PROGRAMA.read_bytes()).hexdigest(),
        "lista_sha256": hashlib.sha256(rt.LISTA.read_bytes()).hexdigest(),
        "formatos": formatos, "sementes_tabela": sementes, "semente_alvos": 2026,
        "alvos": random.Random(2026).sample(palavras, quantidade),
        "modos": ["cores", "fixa"], "rapido": rapido,
        "repeticoes_temporais": 1, "cronometro": "time.perf_counter",
        "hash": "SHA-256(b'GBC083' + senha.encode('utf-8')).hexdigest()",
        "reducao": "SHA-256(f'{cor}:{h}'.encode('utf-8')) modulo 7776; fixa: cor=0",
        "status": "em_execucao",
    }
    arquivo = pasta / "metadados.json"
    arquivo.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = rt.experimentar(formatos, sementes, quantidade, pasta / "resultados.csv")
    meta.update(status="concluido", cenarios_concluidos=len(rows),
                consultas_concluidas=sum(r["alvos"] for r in rows))
    arquivo.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Metadados em {arquivo}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, help="Pasta de resultados; omitir cria uma rodada nova")
    parser.add_argument("--rapido", action="store_true", help="Só conferir integração, sem uso no relatório")
    args = parser.parse_args()
    executar(args.saida, args.rapido)
