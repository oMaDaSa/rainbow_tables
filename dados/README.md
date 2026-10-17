# Lista Diceware usada na aula

Arquivo: `diceware.wordlist.asc`, lista original de Arnold G. Reinhold.

- Link do slide 46: `http://world.std.com/~reinhold/diceware.wordlist.asc`.
- Cópia obtida por HTTPS em [theworld.com](https://theworld.com/~reinhold/diceware.wordlist.asc), em 16/10/2026.
- O arquivo foi preservado com cabeçalho e assinatura PGP, sem traduzir ou limpar palavras.
- SHA-256 dos bytes desta cópia: `3cd6164a99e95381f8620aec782a933545bcd5833fa331d267a6829f6665256e`.
- Conteúdo verificado: 7.776 códigos distintos de cinco dígitos entre 1 e 6; 7.776 palavras distintas. Primeiro par: `11111 a`; último: `66666 @`.

O SHA-256 acima permite conferir se os dois computadores usam a mesma cópia. Esta preparação não verificou criptograficamente a assinatura PGP. Não acrescentamos uma licença própria ao arquivo de terceiros.

Para conferir no PowerShell, a partir da pasta do trabalho:

```powershell
Get-FileHash dados/diceware.wordlist.asc -Algorithm SHA256
```
