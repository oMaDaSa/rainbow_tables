"""Confere o material didático; não implementa nem aprova os TODOs dos alunos."""

import ast
import hashlib
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

RAIZ = Path(__file__).resolve().parents[1]


class Estrutura(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.links = []
        self.passos = []
        self.idioma = None
        self.codigos = []
        self.em_codigo = False

    def handle_starttag(self, tag, attrs):
        dados = dict(attrs)
        if tag == "html":
            self.idioma = dados.get("lang")
        if "id" in dados:
            self.ids.append(dados["id"])
        if tag == "a" and "href" in dados:
            self.links.append(dados["href"])
        if "data-step" in dados:
            self.passos.append(dados["data-step"])
        if tag == "code":
            self.em_codigo = True

    def handle_endtag(self, tag):
        if tag == "code":
            self.em_codigo = False

    def handle_data(self, data):
        if self.em_codigo:
            self.codigos.append(data)


def verificar():
    pagina = (RAIZ / "guia.html").read_text(encoding="utf-8")
    html = Estrutura()
    html.feed(pagina)
    assert html.idioma == "pt-BR"
    assert len(html.ids) == len(set(html.ids)), "IDs HTML repetidos"
    assert len(html.passos) == len(set(html.passos)) == 11
    for link in html.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        if url.path:
            assert (RAIZ / unquote(url.path)).exists(), f"Link local ausente: {link}"
        elif url.fragment:
            assert url.fragment in html.ids, f"Âncora ausente: {link}"
    assert "ETAPAS_SEGUINTES" not in pagina, "Guia incompleto"
    assert not re.search(r'<(?:script|link|img)[^>]+(?:src|href)=[\"\']https?://', pagina), "Recurso externo obrigatório"

    lista = RAIZ / "dados" / "diceware.wordlist.asc"
    assert hashlib.sha256(lista.read_bytes()).hexdigest() == "3cd6164a99e95381f8620aec782a933545bcd5833fa331d267a6829f6665256e"
    pares = [l.split() for l in lista.read_text(encoding="utf-8").splitlines()
             if re.fullmatch(r"[1-6]{5}\s+\S+", l)]
    assert len(pares) == len({p[0] for p in pares}) == len({p[1] for p in pares}) == 7776
    assert pares[0] == ["11111", "a"] and pares[-1] == ["66666", "@"]
    h = hashlib.sha256(b"GBC0831234").hexdigest()
    assert h in pagina
    palavras = [p[1] for p in pares]
    vetor = [palavras[int(hashlib.sha256(f"{c}:{h}".encode()).hexdigest(), 16) % 7776]
             for c in range(3)]
    assert vetor == ["dixie", "ark", "creed"]
    assert 7776 ** 2 == 60466176

    testes = 0
    for arquivo in RAIZ.rglob("*.py"):
        if any(p in arquivo.parts for p in [".venv", "resultados", ".verificacao"]):
            continue
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"), filename=str(arquivo))
        if arquivo.parent.name == "tests":
            testes += sum(isinstance(n, ast.FunctionDef) and n.name.startswith("test_")
                          for n in ast.walk(arvore))
    assert testes == 20, f"Quantidade de testes mudou: {testes}"
    contratos = {"base.py": ["carregar_palavras", "calcular_hash", "reduzir"],
                 "construcao.py": ["fim_da_cadeia", "construir"],
                 "busca.py": ["indexar", "buscar"]}
    for nome, funcoes in contratos.items():
        arvore = ast.parse((RAIZ / nome).read_text(encoding="utf-8"))
        existentes = {n.name for n in arvore.body if isinstance(n, ast.FunctionDef)}
        assert set(funcoes) <= existentes, f"Contrato ausente: {nome}"
    print(f"Material conferido: {len(html.passos)} etapas, {len(html.links)} links, "
          f"{len(pares)} entradas Diceware, {testes} testes progressivos.")
    print("Os TODOs dos alunos NÃO foram executados por esta verificação.")


if __name__ == "__main__":
    verificar()
