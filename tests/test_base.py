import tempfile
import unittest
from pathlib import Path

from base import LISTA, calcular_hash, carregar_palavras, reduzir


class TestHash(unittest.TestCase):
    def test_slide(self):
        self.assertEqual(calcular_hash("1234"),
            "5042f15f93d4f75df9cdff09d062d607eaa0140a930b9023c43ca7cc58609b8f")

    def test_sem_normalizacao(self):
        self.assertNotEqual(calcular_hash("a"), calcular_hash("a\n"))
        self.assertNotEqual(calcular_hash("a"), calcular_hash("A"))


class TestLista(unittest.TestCase):
    def test_lista_completa(self):
        palavras = carregar_palavras()
        self.assertEqual(len(palavras), 7776)
        self.assertEqual(len(set(palavras)), 7776)
        self.assertEqual(palavras[:3], ["a", "a&p", "a's"])
        self.assertEqual(palavras[-1], "@")

    def test_ordem_e_pgp(self):
        linhas = LISTA.read_text(encoding="utf-8").splitlines()
        entradas = [l for l in linhas if len(l.split()) == 2 and
                    len(l.split()[0]) == 5 and set(l.split()[0]) <= set("123456")]
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "embaralhada.asc"
            arquivo.write_text("Cabecalho PGP\n" + "\n".join(reversed(entradas)) +
                               "\n-----END PGP SIGNATURE-----", encoding="utf-8")
            self.assertEqual(carregar_palavras(arquivo), carregar_palavras())

    def test_incompleta_e_duplicada(self):
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "invalida.asc"
            for texto in ["11111 a\n", LISTA.read_text(encoding="utf-8") + "\n11111 a\n"]:
                arquivo.write_text(texto, encoding="utf-8")
                with self.assertRaises(ValueError):
                    carregar_palavras(arquivo)


class TestReducao(unittest.TestCase):
    def test_vetor_comum_da_dupla(self):
        palavras = carregar_palavras()
        h = calcular_hash("1234")
        self.assertEqual([reduzir(h, c, palavras) for c in range(3)],
                         ["dixie", "ark", "creed"])

    def test_determinismo_dominio(self):
        palavras = ["a", "b", "c", "d", "e", "f", "g"]
        for modo in ["cores", "fixa"]:
            for coluna in range(20):
                h = calcular_hash(str(coluna))
                resultado = reduzir(h, coluna, palavras, modo)
                self.assertIn(resultado, palavras)
                self.assertEqual(resultado, reduzir(h, coluna, palavras, modo))

    def test_cor_fixa(self):
        palavras = [str(i) for i in range(100)]
        h = calcular_hash("a")
        self.assertEqual(reduzir(h, 0, palavras), reduzir(h, 23, palavras, "fixa"))

    def test_cores_tem_efeito(self):
        palavras = [str(i) for i in range(100)]
        resultados = {reduzir(calcular_hash("a"), c, palavras) for c in range(20)}
        # Não exigimos que TODAS as colunas produzam palavras distintas.
        self.assertGreater(len(resultados), 1)

    def test_argumentos(self):
        for coluna, palavras, modo in [(-1, ["a"], "cores"), (0, [], "cores"), (0, ["a"], "outro")]:
            with self.assertRaises(ValueError):
                reduzir(calcular_hash("a"), coluna, palavras, modo)


if __name__ == "__main__":
    unittest.main()
