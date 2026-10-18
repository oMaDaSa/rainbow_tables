# Rainbow Tables — guia do trabalho em dupla

Abra [guia.html](guia.html) no navegador. Ele explica o trabalho a partir do [PDF da aula](aulaRT.pdf), acompanha a implementação em Python e mostra como dividir o código entre vocês.

As funções da base conjunta (B1/B2 em `base.py`) e da parte A (A1/A2 em `construcao.py`) estão implementadas. A **parte B continua reservada à outra pessoa**: `busca.py` mantém o esqueleto original, com C1/C2 por preencher. Os rótulos B1/B2 pertencem à base comum, não à parte B de busca.

## Estado atual — 18/10/2026

- Conjunto: leitura validada das 7.776 entradas Diceware, hash do professor e redução nos modos cores/fixa.
- Parte A: cadeia com exatamente t passos H→R e construção de m pares início/fim, com inícios distintos, semente reproduzível e finais repetidos preservados.
- Parte B: índice e busca pendentes com a outra pessoa. O arquivo `busca.py` está igual à versão inicial do repositório.
- Verificação deste escopo: **13 testes**, sendo dez da base e três da construção. Os testes de busca e integração dependem da parte B; os experimentos e o relatório ficam para depois de integrar as duas partes.

Para conferir apenas o que está implementado:

```powershell
python -m unittest tests.test_base tests.test_dupla.TestConstrucao -v
```

O código segue os laços, listas e dicionários apresentados no guia, sem dependências externas. As alterações permanecem locais, sem commit ou publicação remota.

## Começar

Abra esta pasta, `rainbow_tables`, no VS Code. No terminal dela, com Python 3.10+:

```powershell
python -m unittest tests.test_base.TestHash -v
```

Os dois testes iniciais devem passar. Nenhum pacote externo precisa ser instalado. A lista Diceware original já está em `dados/`, com procedência documentada. O guia e o código funcionam offline após instalar as ferramentas.

## Divisão e sequência

1. Juntos: etapas 0–4; leitura e redução na base comum concluídas.
2. Pessoa A: etapa 5, construção concluída; `python -m unittest tests.test_dupla.TestConstrucao -v`.
3. Pessoa B: etapa 6, índice e busca a implementar pela outra pessoa; `python -m unittest tests.test_dupla.TestBusca -v`.
4. Juntos: juntar as partes, rodar os testes e fazer os experimentos. Aproveitem para acompanhar o código do colega.

Depois que a parte B estiver pronta:

```powershell
python -m unittest tests.test_base -v
python -m unittest tests.test_dupla.TestIntegracao -v
python -m unittest discover -v
python experimentar.py --rapido
python experimentar.py
```

Antes de implementar os TODOs, testes dessas funções mostram `NotImplementedError`; não são pulados nem considerados aprovados. Ao completar a implementação, os **20 testes** devem passar. O modo rápido é uma conferência de integração; a rodada completa produz 24 cenários e 4.800 consultas. Cada execução grava uma pasta nova em `resultados/`.

## Convenções e limites

- Senha principal: uma das 7.776 entradas, sem código dos dados nem quebra de linha.
- H: SHA-256 de `b"GBC083" + senha.encode("utf-8")`, hexadecimal.
- R: mistura SHA-256 de `f"{cor}:{h}"`, inteiro hexadecimal módulo N; cor é a coluna ou zero no modo fixo.
- Largura t: t passos H→R; linha guarda palavras p₀ e pₜ. O hash de pₜ não faz parte dessa linha.
- Finais repetidos preservam todos os inícios. Busca só retorna senha após confirmar o hash.
- Experimentos: formatos 512×16, 256×32, 128×64, 64×128; sementes 17, 43 e 91; 200 alvos independentes, semente 2026; modos cores e fixa.
- Armazenamento medido: bytes do JSON de pares, não RAM. Metadados incluem campos de CPU/RAM/condições para preencher.
- Duas palavras são uma extensão orientada, não implementada no esqueleto nem no medidor.

## Compartilhar e continuar

A etapa 9 explica criar um repositório **nesta pasta**, convidar o colega, trabalhar em branches e revisar PRs. Nenhum repositório remoto foi criado. `resultados/` é ignorado; copiem uma rodada completa e seus metadados preenchidos para `relatorio/` quando quiserem versionar as evidências selecionadas.

O progresso marcado no HTML é individual, local ao navegador e não é sincronizado com o colega. Para registrar continuidade compartilhada, usem commits e uma nota objetiva no PR ou neste README, indicando TODOs concluídos e testes executados.

## Verificar o material fornecido

```powershell
python ferramentas/verificar_material.py
```

Esse comando usa somente a biblioteca padrão e confere estrutura, links locais, integridade da lista, sintaxe Python, nomes dos TODOs, quantidade de testes e vetores numéricos do guia. Ele não certifica a implementação dos alunos; para isso, executem os testes progressivos.

Nas revisões do guia, manter a explicação em português natural, como alguém acompanhando os colegas no trabalho. Evitar slogans, frases de efeito, avisos repetidos e tom de cobrança. Explicar os termos novos no contexto em que aparecem, sem infantilizar a leitura.

Na preparação do roteiro, uma referência temporária passou nos 20 testes e executou o modo rápido e os 24 cenários completos (4.800 consultas), conferindo contagens e arquivos gerados. Essa implementação não faz parte da entrega; os resultados de referência não são resultados da dupla. A página foi conferida no Edge em desktop (1.440 px) e celular (390 px), incluindo interação da cadeia, cópia, formatos e persistência das marcações. O PDF da aula foi preservado.
