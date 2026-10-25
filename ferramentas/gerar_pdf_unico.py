"""Criar a entrega em PDF horizontal a partir de um HTML local.

Código e PDF ficam em apresentacao/, dados em dados/ e resultados em relatorio/.
"""

import ast
from collections import defaultdict
import csv
import hashlib
from html import escape
import io
import json
import keyword
import math
from pathlib import Path
import statistics
import subprocess
import sys
import tokenize

RAIZ = Path(__file__).resolve().parents[1]
FONTES = RAIZ / "apresentacao"
RELATORIO = RAIZ / "relatorio"
HTML = RELATORIO / "apresentacao.html"
BUILD = RAIZ / ".verificacao" / "pdf-unico"
REPO_URL = "https://github.com/oMaDaSa/rainbow_tables/tree/main/apresentacao"
sys.path.insert(0, str(RAIZ / ".verificacao" / "html-deps"))
sys.path.insert(0, str(RAIZ / ".verificacao" / "pdf-deps"))

CSS = r'''
@page { size: 1280px 720px; margin: 0; }
* { box-sizing: border-box; }
:root { --navy:#173047; --green:#176f61; --orange:#be642f; --muted:#526575; --paper:#fbfcfd; }
html, body { margin:0; color:var(--navy); font-family:"Segoe UI",Arial,sans-serif; }
body { background:#dce3e8; }
.slide { width:1280px; height:720px; padding:44px 64px 48px; position:relative;
  background:var(--paper); break-after:page; overflow:hidden; }
.slide:last-child { break-after:auto; }
.eyebrow { margin:0 0 10px; color:var(--green); text-transform:uppercase;
  letter-spacing:2px; font-size:16px; font-weight:650; }
h1 { font-size:43px; line-height:1.13; font-weight:650; margin:0 0 24px; letter-spacing:-.7px; }
h2 { font-size:27px; line-height:1.2; margin:0 0 13px; font-weight:650; }
p, li { font-size:23px; line-height:1.42; margin:0 0 20px; }
ul, ol { padding-left:29px; margin:0; }
li { padding-left:5px; margin-bottom:18px; }
strong { font-weight:650; }
.small { font-size:18px; line-height:1.4; color:var(--muted); }
.note { font-size:17px; line-height:1.4; color:var(--muted); margin-top:16px; }
.columns { display:grid; grid-template-columns:1.1fr 1fr; gap:58px; align-items:start; }
.chart-layout { display:grid; grid-template-columns:780px 1fr; gap:36px; align-items:center; }
.rule { border-top:1px solid #d6e0e6; padding-top:21px; }
.stat { font-size:65px; font-weight:650; line-height:1; color:var(--green); margin:10px 0 10px; }
.stat.orange { color:var(--orange); }
table { width:100%; border-collapse:collapse; font-variant-numeric:tabular-nums; }
th { background:var(--navy); color:white; text-align:left; font-weight:600; }
th,td { padding:12px 14px; font-size:20px; line-height:1.2; vertical-align:top; }
td { border-bottom:1px solid #d9e3e8; }
tbody tr:nth-child(even) { background:#edf3f6; }
table.compact th,table.compact td { font-size:18px; padding:12px 11px; }
table.seed th,table.seed td { font-size:18px; padding:4px 12px; }
.legend { display:flex; gap:28px; font-size:18px; color:var(--muted); margin-top:8px; }
.legend span:first-child { color:var(--green); }
.legend span:last-child { color:var(--orange); }
.footer { position:absolute; bottom:21px; left:64px; right:64px; display:flex;
 justify-content:space-between; font-size:14px; color:#73818d; border-top:1px solid #dbe4e9; padding-top:10px; }
.cover { background:var(--navy); color:white; padding:64px 76px; }
.cover .eyebrow { color:#9bd4c5; margin-bottom:65px; }
.cover h1 { font-size:74px; letter-spacing:-2px; line-height:1.04; margin-bottom:26px; max-width:940px; }
.cover .subtitle { font-size:29px; color:#d1e1eb; max-width:900px; }
.cover .authors { margin-top:85px; font-size:24px; line-height:1.55; }
.cover .small { color:#c1d3de; }
.cover .footer { color:#acc3d0; border-color:#3f586b; }
.chain { font-family:Consolas,monospace; font-size:40px; letter-spacing:-1px;
 margin:38px 0; padding:27px 0; border-top:1px solid #b7c9d3; border-bottom:1px solid #b7c9d3; }
.chain em { font-family:"Segoe UI",sans-serif; font-size:20px; font-style:normal; color:var(--muted); padding:0 12px; }
.hash { font-family:Consolas,monospace; font-size:21px; line-height:1.5; overflow-wrap:anywhere; }
.terminal { font-family:Consolas,monospace; background:#edf3f6; padding:24px; font-size:21px; line-height:1.7; white-space:pre-wrap; }
.formula { font-family:Consolas,monospace; font-size:23px; line-height:1.6; padding:20px 0; }
.code-slide { padding-top:29px; }
.code-slide .eyebrow { font-size:14px; margin-bottom:6px; }
.code-slide h1 { font-size:31px; margin-bottom:9px; }
.code-slide .code-desc { font-size:17px; color:var(--muted); margin-bottom:13px; line-height:1.25; }
.listing { background:#f0f4f7; padding:14px 18px 14px 0; border-top:3px solid var(--green); }
.code-line { display:flex; font-family:Consolas,monospace; font-size:17px; line-height:22px;
  white-space:pre; font-variant-ligatures:none; }
.ln { display:inline-block; width:52px; flex:0 0 52px; text-align:right; padding-right:16px; color:#8494a0; user-select:none; }
.src { display:block; white-space:pre; }
.kw { color:#74419d; font-weight:600; }.str { color:#176f61; }.com { color:#697d8a; }.num { color:#9f5426; }
a { color:var(--green); text-decoration:none; }
.repo-link { display:block; overflow-wrap:anywhere; font-size:18px; line-height:1.45; margin:12px 0; }
@media screen { .slide { margin:28px auto; box-shadow:0 3px 24px #152d4526; } }
@media print { body { background:white; } .slide { margin:0; box-shadow:none; } }
'''


def num(x, casas=1):
    return f"{x:,.{casas}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def tabela(headers, rows, classe=""):
    return '<table class="' + classe + '"><thead><tr>' + ''.join(
        '<th>' + escape(str(v)).replace('\n', '<br>') + '</th>' for v in headers
    ) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(
        '<td>' + escape(str(v)).replace('\n', '<br>') + '</td>' for v in row
    ) + '</tr>' for row in rows) + '</tbody></table>'


def anexo(nome):
    if nome == "resultados.csv":
        return RELATORIO / nome
    if nome == "diceware.wordlist.asc":
        return RAIZ / "dados" / nome
    return FONTES / nome


def medias_csv():
    with (RELATORIO / "resultados.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 24 and sum(int(r["alvos"]) for r in rows) == 4800
    grupos = defaultdict(list)
    for r in rows:
        grupos[(r["modo"], int(r["altura"]), int(r["largura"]))].append(r)
    medias = []
    campos = ["acertos", "taxa_acerto", "construcao_s", "indexacao_s", "buscas_s",
              "sucesso_medio_ms", "falha_media_ms", "tabela_bytes", "finais_distintos"]
    for (modo, m, t), grupo in grupos.items():
        item = dict(modo=modo, m=m, t=t)
        item.update({k: statistics.mean(float(r[k]) for r in grupo) for k in campos})
        item["consulta_ms"] = item["buscas_s"] * 1000 / 200
        medias.append(item)
    return rows, medias


def grafico(medias, barras):
    w, h = 780, 425
    left, bottom, plotw, ploth = 70, 346, 680, 290
    maximo = 80 if barras else max(40, math.ceil(max(x["consulta_ms"] for x in medias) / 10) * 10)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">']
    for i in range(5):
        y = bottom - ploth*i/4
        svg.append(f'<line x1="{left}" y1="{y}" x2="{left+plotw}" y2="{y}" stroke="#d5e0e6"/>')
        svg.append(f'<text x="{left-13}" y="{y+7}" text-anchor="end" font-size="19" fill="#526575">{int(maximo*i/4)}</text>')
    svg.append(f'<text x="0" y="25" font-size="20" fill="#526575">{"Acertos (%)" if barras else "Tempo (ms)"}</text>')
    for j,(modo,cor) in enumerate([("cores", "#176f61"),("fixa", "#be642f")]):
        pontos=[]
        for i,r in enumerate(x for x in medias if x["modo"] == modo):
            centro=left+plotw*(i+.5)/4
            valor=r["taxa_acerto"]*100 if barras else r["consulta_ms"]
            y=bottom-ploth*valor/maximo
            if barras:
                x=centro-43+j*44
                svg.append(f'<rect x="{x}" y="{y}" width="37" height="{bottom-y}" fill="{cor}"/>')
                tx=x+18.5;ty=y-12
            else:
                pontos.append((centro,y))
                svg.append(f'<circle cx="{centro}" cy="{y}" r="5" fill="{cor}"/>')
                baixo=valor<3
                tx=centro+((-24 if j==0 else 24) if baixo else 0)
                ty=y-15 if baixo or j==1 else y+27
            svg.append(f'<text x="{tx}" y="{ty}" text-anchor="middle" font-size="19" font-weight="600" fill="{cor}">{num(valor,1 if barras else 2)}</text>')
            if j==0:
                svg.append(f'<text x="{centro}" y="{bottom+35}" text-anchor="middle" font-size="20" fill="#173047">{r["m"]}×{r["t"]}</text>')
        if pontos:
            svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pontos)+f'" fill="none" stroke="{cor}" stroke-width="3"/>')
    svg.append('</svg>')
    return ''.join(svg)


def colorir(codigo):
    linhas=codigo.splitlines()
    intervalos=defaultdict(list)
    for tk in tokenize.generate_tokens(io.StringIO(codigo).readline):
        classe = ('str' if tk.type==tokenize.STRING else 'com' if tk.type==tokenize.COMMENT
                  else 'num' if tk.type==tokenize.NUMBER else 'kw' if tk.type==tokenize.NAME and keyword.iskeyword(tk.string) else '')
        if not classe: continue
        for linha in range(tk.start[0],tk.end[0]+1):
            if linha>len(linhas): continue
            a=tk.start[1] if linha==tk.start[0] else 0
            b=tk.end[1] if linha==tk.end[0] else len(linhas[linha-1])
            if b>a: intervalos[linha].append((a,b,classe))
    resultado=[]
    for n,linha in enumerate(linhas,1):
        pos=0;partes=[]
        for a,b,c in sorted(intervalos[n]):
            partes.extend([escape(linha[pos:a]), f'<span class="{c}">'+escape(linha[a:b])+'</span>']);pos=b
        partes.append(escape(linha[pos:]));resultado.append(''.join(partes))
    return resultado


def criar_html():
    rows, medias = medias_csv()
    codigo=(FONTES/"rainbow_tables.py").read_text(encoding="utf-8")
    ast.parse(codigo)
    meta=json.loads((RELATORIO/"metadados.json").read_text(encoding="utf-8"))
    assert meta["status"] == "concluido" and not meta["rapido"]
    assert hashlib.sha256(codigo.encode()).hexdigest()==meta["codigo_sha256"]
    resultado=subprocess.run([sys.executable,"-B","testar_busca.py"], cwd=FONTES,
                             capture_output=True,text=True,encoding="utf-8",check=True).stdout
    assert "80/80" in resultado and "None (correto)" in resultado
    BUILD.mkdir(parents=True,exist_ok=True)
    (BUILD/"testes.txt").write_text(resultado,encoding="utf-8")
    slides=[]

    def slide(titulo, conteudo, secao="", classe="", descricao=""):
        header=(f'<p class="eyebrow">{escape(secao)}</p>' if secao else '')+f'<h1>{titulo}</h1>'
        if descricao: header+=f'<p class="code-desc">{escape(descricao)}</p>'
        slides.append((classe,header+conteudo))

    slide("Rainbow Tables", '''<p class="subtitle">Implementação, testes e análise experimental<br>com senhas Diceware</p>
      <div class="authors">Matheus Dantas Santana<br>Vanessa Dias Ferreira</div>
      <p class="small">Professor Ivan Sendin<br>Universidade Federal de Uberlândia, 25 de outubro de 2026</p>''',
      "Segurança da Informação / GBC083", "cover")

    slide("Objetivo e espaço de senhas", '''<div class="columns"><div><p class="stat">7.776</p>
      <h2>senhas possíveis</h2><p>Cada senha é uma entrada da lista Diceware original, sem o código numérico e sem quebra de linha.</p>
      <p class="small">Combinações de duas palavras não foram avaliadas.</p></div><div>
      <p>O experimento compara tabelas altas e estreitas com tabelas baixas e largas.</p>
      <p>Medimos a proporção de senhas recuperadas, o tempo das consultas e o tamanho dos pares guardados.</p>
      <p class="small rule">Uma redução fixa funciona como comparação para observar o efeito das cores.</p></div></div>''', "01 / Proposta")

    slide("A cadeia guarda só os extremos", '''<p>Exemplo real com três passos de hash e redução, começando na entrada <strong>a</strong>.</p>
      <div class="chain">a <em>H, R₀</em> iowa <em>H, R₁</em> pork <em>H, R₂</em> opt</div>
      <div class="columns"><div><h2>Par armazenado</h2><p class="formula">("a", "opt")</p>
      <p>As palavras intermediárias são recalculadas quando uma busca precisa conferir a cadeia.</p></div>
      <div><h2>O papel das cores</h2><p>H usa SHA-256 com o prefixo GBC083. R escolhe uma palavra a partir do hash e da coluna.</p>
      <p class="small">Nessa linha, os candidatos comparados por H são a, iowa e pork. O extremo opt isolado não acrescenta cobertura.</p></div></div>''', "02 / Implementação")

    slide("Busca e confirmação do candidato", '''<div class="columns"><div><ol>
      <li>Receber o hash e testar em qual coluna da cadeia ele pode estar.</li>
      <li>Continuar até um final e consultar o índice de pares.</li>
      <li>Refazer cada cadeia candidata e comparar seus hashes com o alvo.</li></ol></div><div>
      <h2>O final não é uma prova</h2><p>Vários inícios podem levar ao mesmo final. O índice preserva todos eles.</p>
      <p>A senha só é devolvida depois de confirmar seu hash. Um candidato incorreto não encerra a busca.</p>
      <p class="small rule">No exemplo, consultar H("iowa") na cadeia a–opt recupera iowa. Não há varredura extra da lista para completar falhas.</p></div></div>''', "02 / Implementação")

    slide("Experimento e computador utilizado", '<div class="columns"><div>'+tabela(
      ["Parâmetro","Valor"],[["Formatos m×t","512×16, 256×32, 128×64, 64×128"],["Sementes da tabela","17, 43 e 91"],["Alvos por cenário","200, com semente 2026"],["Modos","Cores e redução fixa"]],"compact")+
      '<p class="note">Os mesmos alvos, sorteados independentemente da construção, são usados nos 24 cenários. São 4.800 consultas.</p></div><div>'+tabela(
      ["Componente","Configuração"],[["Processador","Ryzen 7 5700X, 8 núcleos / 16 processadores lógicos"],["Memória RAM","16 GiB"],["Sistema","Windows 11"],["Python","3.14.7"]],"compact")+
      '<p class="note">Todos os formatos fazem 8.192 passos na construção. Repetições impedem garantir cobertura integral só por essa contagem.</p></div></div>', "03 / Testes experimentais")

    slide("Verificações funcionais", '<div class="columns"><div>'+tabela(["Caso","Resultado"],
      [["Hash do exemplo do professor","Valor esperado confirmado"],["Inícios com final repetido","Ambos preservados no índice"],["Hashes presentes nas cadeias","80 de 80 recuperados"],["Alvo fora da cobertura","None, sem senha incorreta"]],"compact")+
      '</div><div><h2>O que foi conferido</h2><p>As 80 consultas percorrem todas as cinco posições de oito cadeias, nos dois modos.</p>'
      '<p>O caso ausente usa largura 1: escolhemos uma entrada que não está entre os inícios da tabela.</p>'
      '<p class="small">O código completo dessas verificações está no apêndice. Esses casos de correção não são usados para estimar eficácia.</p></div></div>', "04 / Testes de correção")

    slide("Recuperação dos alvos", '<div class="chart-layout"><div>'+grafico(medias,True)+
      '<div class="legend"><span>Cores</span><span>Redução fixa</span></div></div><div><p class="stat">52,7%<br>a 59,8%</p>'
      '<p>de recuperação média com cores.</p><p class="small">A redução fixa ficou entre 13,7% e 37,0%. Os valores são médias das três sementes.</p>'
      '<p class="small rule">A amostra mede recuperação de 200 alvos. Ela não mede a cobertura exata das 7.776 entradas.</p></div></div>', "05 / Eficácia")

    slide("Eficácia e armazenamento", tabela(["Modo","Formato","Acertos / 200","Taxa (%)","Finais distintos","Disco (bytes)"],
      [[x["modo"],f'{x["m"]}×{x["t"]}',num(x["acertos"]),num(x["taxa_acerto"]*100),num(x["finais_distintos"]),num(x["tabela_bytes"],0)] for x in medias],"compact")+
      '<p class="note">Médias das três sementes. Disco é o tamanho do JSON dos pares início/fim. A RAM do processo não foi medida. Finais distintos não indicam, sozinhos, a cobertura da tabela.</p>', "05 / Eficácia")

    seedrows=[]
    for m,t in [(512,16),(256,32),(128,64),(64,128)]:
        for s in [17,43,91]:
            cs=next(r for r in rows if r["modo"]=="cores" and int(r["altura"])==m and int(r["semente"])==s)
            fx=next(r for r in rows if r["modo"]=="fixa" and int(r["altura"])==m and int(r["semente"])==s)
            seedrows.append([f'{m}×{t}',s,cs["acertos"],num(float(cs["taxa_acerto"])*100),fx["acertos"],num(float(fx["taxa_acerto"])*100)])
    slide("Variação entre as sementes",tabela(["Formato","Semente","Acertos cores","Cores (%)","Acertos fixa","Fixa (%)"],seedrows,"seed")+
      '<p class="note">Em cores, 256×32 variou de 55% a 66%, e 512×16 de 55% a 61%. A diferença entre as médias 59,8% e 58,8% não demonstra superioridade geral de um formato.</p>', "05 / Eficácia")

    cs=[x for x in medias if x["modo"]=="cores"]
    fator=cs[-1]["consulta_ms"]/cs[0]["consulta_ms"]
    economia=(1-cs[-1]["tabela_bytes"]/cs[0]["tabela_bytes"])*100
    slide("Tempo médio por consulta",'<div class="chart-layout"><div>'+grafico(medias,False)+
      '<div class="legend"><span>Cores</span><span>Redução fixa</span></div></div><div>'
      f'<p class="stat orange">{num(fator)}×</p><p>mais tempo por consulta em cores ao passar de 512×16 para 64×128.</p>'
      '<p class="small">Cadeias longas exigem testar mais posições e recalcular trechos maiores. Falhas esgotam as hipóteses, enquanto acertos podem encerrar a busca antes.</p></div></div>',"06 / Eficiência")

    slide("Custos de construção e de busca",tabela(["Modo","Formato","Construção\n(ms)","Índice\n(ms)","Total buscas\n(s)","Consulta\n(ms)","Sucesso\n(ms)","Falha\n(ms)"],
      [[x["modo"],f'{x["m"]}×{x["t"]}',num(x["construcao_s"]*1000,2),num(x["indexacao_s"]*1000,3),num(x["buscas_s"],3),num(x["consulta_ms"],2),num(x["sucesso_medio_ms"],2),num(x["falha_media_ms"],2)] for x in medias],"compact")+
      '<p class="note">Médias das três sementes. Total soma 200 buscas por tabela, e consulta é total/200. Sucesso e falha são médias das médias condicionais de cada semente. Construção e índice são custos iniciais, medidos separadamente.</p>',"06 / Eficiência")

    slide("Análise dos resultados",f'''<div class="columns"><div><h2>As cores reduzem fusões</h2>
      <p>Com redução fixa, repetir uma palavra repete a continuação. Com cores, o caminho também depende da coluna.</p>
      <p>As cores não eliminam coincidências. Se duas cadeias chegam à mesma palavra na mesma coluna, compartilham a continuação.</p>
      <p class="small">Essas colisões de redução não exigem colisões criptográficas de SHA-256.</p></div><div>
      <h2>Menos pares, mais reconstrução</h2><p>De 512×16 para 64×128, em cores, o armazenamento caiu <strong>{num(economia)}%</strong> e a consulta ficou <strong>{num(fator)} vezes</strong> mais lenta.</p>
      <p class="small">Só as continuações de uma busca que esgota as posições podem exigir t(t−1)/2 aplicações de H, além das reduções e reconstruções candidatas.</p></div></div>''',"07 / Análise")

    slide("Conclusão e limites",'''<p style="font-size:35px;line-height:1.3;max-width:1050px">Nos cenários medidos, as cores preservaram melhor a recuperação. Aumentar a largura reduziu o arquivo e elevou o tempo de busca.</p>
      <div class="columns rule"><div><h2>Escolha do formato</h2><p>Tabelas altas favorecem consultas rápidas. Tabelas baixas e largas economizam armazenamento.</p>
      <p class="small">Para 7.776 candidatos, busca direta é viável. A utilidade da pré-computação depende da reutilização.</p></div><div>
      <h2>Alcance do experimento</h2><p>Uma entrada Diceware por senha, quatro formatos, três sementes e 200 alvos.</p>
      <p class="small">Os tempos vêm de uma medição por cenário. Não estimamos variação temporal. O prefixo comum permite reutilizar a tabela, enquanto sais distintos exigem tabelas compatíveis.</p></div></div>''',"08 / Conclusão")

    slide("Código e reprodução",'''<div class="columns"><div><h2>Execução</h2><p>Python 3.10 ou superior, somente biblioteca padrão.</p>
      <pre class="terminal">python rainbow_tables.py\npython testar_busca.py</pre>
      <p class="small">No repositório, a lista fica em dados/. Ao extrair os anexos do PDF, deixe a lista ao lado dos códigos.</p></div><div>
      <h2>Apresentação e códigos no GitHub</h2>
      <a class="repo-link" href="https://github.com/oMaDaSa/rainbow_tables/tree/main/apresentacao">github.com/oMaDaSa/rainbow_tables/tree/main/apresentacao</a>
      <p class="small">A pasta reúne este PDF, rainbow_tables.py e testar_busca.py. As páginas seguintes também contêm os dois códigos completos.</p>
      <p class="small">Programa, testes, lista e CSV permanecem anexados ao próprio PDF para reprodução.</p></div></div>
      <p class="note rule">Fontes: Ivan Sendin, Rainbow Tables, GBC083/UFU, slides 32-36 e 46-47. Arnold G. Reinhold, <a href="https://theworld.com/~reinhold/diceware.wordlist.asc">Diceware Word List</a>, cópia obtida em 16/10/2026.</p>''',"09 / Referências e execução")

    for arquivo,secao,descricao in [
        ("rainbow_tables.py","Apêndice A / Implementação completa","O arquivo está inteiro e na ordem de execução. Os números à esquerda não fazem parte do Python."),
        ("testar_busca.py","Apêndice B / Testes funcionais","Verificações reproduzíveis de hash, índice, candidatos presentes e alvo ausente."),
    ]:
        texto=(FONTES/arquivo).read_text(encoding="utf-8")
        coloridas=colorir(texto)
        total=(len(coloridas)+22)//23
        for inicio in range(0,len(coloridas),23):
            bloco=coloridas[inicio:inicio+23]
            linhas=''.join(f'<div class="code-line"><span class="ln">{inicio+i+1:03d}</span><span class="src">{linha}</span></div>' for i,linha in enumerate(bloco))
            slide(f'{arquivo} ({inicio//23+1}/{total})','<div class="listing" data-file="'+arquivo+'">'+linhas+'</div>',secao,"code-slide",descricao)

    total=len(slides)
    corpo=''.join(f'<section class="slide {classe}" data-slide="{i}">{body}<footer class="footer"><span>GBC083 · Rainbow Tables</span><span>{i:02d} / {total:02d}</span></footer></section>' for i,(classe,body) in enumerate(slides,1))
    HTML.write_text('<!doctype html><html lang="pt-BR"><meta charset="utf-8"><title>Rainbow Tables — Implementação, testes e análise</title><style>'+CSS+'</style><body>'+corpo+'</body></html>',encoding="utf-8")
    return total


def renderizar(total):
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter
    edge=Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    draft=BUILD/"apresentacao_sem_anexos.pdf"
    with sync_playwright() as p:
        config={"headless":True,"args":["--disable-gpu"]}
        if edge.is_file():
            config["executable_path"]=str(edge)
        browser=p.chromium.launch(**config)
        page=browser.new_page(viewport={"width":1280,"height":720})
        page.goto(HTML.as_uri(),wait_until="load")
        page.emulate_media(media="print")
        page.evaluate("document.fonts.ready")
        problemas=page.evaluate('''() => [...document.querySelectorAll('.slide')].flatMap(s => {
          const r=s.getBoundingClientRect(); const bad=[];
          if(s.scrollHeight>s.clientHeight+1) bad.push({slide:s.dataset.slide,problema:'altura',valor:s.scrollHeight});
          for(const e of s.querySelectorAll('.src, p, li, table, .listing, svg')) {
            const b=e.getBoundingClientRect();
            if(b.right>r.right-40 || b.bottom>r.bottom-47) bad.push({slide:s.dataset.slide,problema:'limite',tag:e.tagName,texto:e.textContent.slice(0,70)});
          } return bad;
        })''')
        for nome in ["rainbow_tables.py","testar_busca.py"]:
            texto=page.locator(f'.listing[data-file="{nome}"] .src').all_text_contents()
            assert '\n'.join(texto)+'\n'==(FONTES/nome).read_text(encoding="utf-8"),nome
        (BUILD/"layout.json").write_text(json.dumps(problemas,ensure_ascii=False,indent=2),encoding="utf-8")
        assert not problemas,problemas
        page.pdf(path=str(draft),print_background=True,prefer_css_page_size=True)
        browser.close()
    reader=PdfReader(draft)
    assert len(reader.pages)==total
    writer=PdfWriter(clone_from=reader)
    writer.add_metadata({"/Title":"Rainbow Tables — Implementação, testes e análise", "/Author":"Matheus Dantas Santana e Vanessa Dias Ferreira"})
    for nome in ["rainbow_tables.py","testar_busca.py","resultados.csv","diceware.wordlist.asc"]:
        writer.add_attachment(nome,anexo(nome).read_bytes())
    destino=FONTES/"Rainbow_Tables_Matheus_Vanessa.pdf"
    with destino.open("wb") as f:writer.write(f)
    final=PdfReader(destino)
    assert len(final.pages)==total
    for nome in ["rainbow_tables.py","testar_busca.py","resultados.csv","diceware.wordlist.asc"]:
        assert final.attachments[nome][0]==anexo(nome).read_bytes()
    print(f"PDF: {destino}\nPaginas: {total}\nAnexos internos: 4\nLayout sem transbordamento")


if __name__=="__main__":
    renderizar(criar_html())
