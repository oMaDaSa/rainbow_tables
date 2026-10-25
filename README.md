# Rainbow Tables

Trabalho de Segurança da Informação (GBC083), Universidade Federal de Uberlândia.

**Autores:** Matheus Dantas Santana e Vanessa Dias Ferreira.
**Professor:** Ivan Sendin.

A implementação compara formatos de Rainbow Tables com senhas de uma entrada Diceware, usando reduções por coluna e uma redução fixa para comparação.

## Apresentação e códigos

A pasta [apresentacao/](https://github.com/oMaDaSa/rainbow_tables/tree/main/apresentacao) contém:

- [Apresentação em PDF](apresentacao/Rainbow_Tables_Matheus_Vanessa.pdf): implementação explicada, testes, gráficos, análises e código completo.
- [rainbow_tables.py](apresentacao/rainbow_tables.py): implementação e experimento completo.
- [testar_busca.py](apresentacao/testar_busca.py): verificações funcionais apresentadas no PDF.

A entrega ao professor é **um único PDF**. Ele também inclui os códigos, a lista e o CSV como anexos internos.

## Executar

Python 3.10 ou superior. Os algoritmos e os testes usam somente a biblioteca padrão.

Na raiz do repositório:

```bash
python apresentacao/testar_busca.py
python -m unittest discover -v
python apresentacao/rainbow_tables.py
```

O último comando executa 24 cenários e 4.800 consultas, e gera `apresentacao/resultados.csv`. A lista é localizada automaticamente em `dados/`. Esse arquivo novo não substitui a rodada do relatório, preservada em `relatorio/resultados.csv`.

Para executar uma nova rodada com metadados:

```bash
python ferramentas/executar_experimento.py
```

Os resultados são gravados em uma pasta nova de `resultados/`. O argumento `--rapido` executa apenas uma conferência curta de integração, que não deve ser usada no relatório. Para atualizar explicitamente a rodada oficial, use `--saida relatorio`.

## Organização

| Pasta | Conteúdo |
| --- | --- |
| `apresentacao/` | PDF final e os dois códigos apresentados |
| `dados/` | Lista Diceware original e sua procedência |
| `relatorio/` | CSV da rodada oficial e metadados |
| `ferramentas/` | Execução documentada do experimento |
| `tests/` | Testes automatizados da implementação |
| `referencias/` | Material do professor com enunciado e hash de referência |

## Experimento

- Domínio: 7.776 entradas Diceware; uma entrada por senha. Duas palavras não foram avaliadas.
- Formatos: 512×16, 256×32, 128×64 e 64×128; todos com 8.192 passos de construção.
- Modos: cores por coluna e redução fixa.
- Sementes das tabelas: 17, 43 e 91. Os mesmos 200 alvos são sorteados com semente 2026, independentemente da construção.
- Ambiente da rodada publicada: Ryzen 7 5700X, 16 GiB de RAM, Windows 11, Python 3.14.7.
- Eficácia: proporção de alvos recuperados. Eficiência: tempos de construção, índice e busca; tamanho dos pares serializados em JSON.

As tabelas do PDF são médias das três sementes. O CSV preserva cada cenário separadamente, e os metadados identificam o código e a lista usados. A taxa amostral não é a cobertura exata do dicionário, e o tamanho do JSON não é consumo de RAM.

## Referências

- Ivan Sendin. [Rainbow Tables](referencias/aulaRT.pdf), material de GBC083/UFU. Slides 46 e 47 apresentam a proposta e o hash.
- Arnold G. Reinhold. [Diceware Word List](https://theworld.com/~reinhold/diceware.wordlist.asc). O SHA-256 da cópia usada está em [relatorio/metadados.json](relatorio/metadados.json), no campo `lista_sha256`.
