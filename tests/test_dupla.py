"""Casos pequenos: primeiro testar cada trilha; depois a integração real."""

import random
import unittest
from unittest.mock import patch

from base import calcular_hash, carregar_palavras, reduzir
from busca import buscar, indexar
from construcao import construir, fim_da_cadeia


def hash_brinquedo(p):
    return {"A": "01", "B": "02", "C": "03", "D": "04", "X": "ff"}[p]


def reducao_brinquedo(h, coluna, palavras, modo="cores"):
    return {("01", 0): "B", ("02", 1): "C", ("03", 2): "D"}.get((h, coluna), "X")


class TestConstrucao(unittest.TestCase):
    def test_tres_passos(self):
        with patch("construcao.calcular_hash", side_effect=hash_brinquedo), \
             patch("construcao.reduzir", side_effect=reducao_brinquedo):
            self.assertEqual(fim_da_cadeia("A", list("ABCDX"), 3), "D")

    def test_preserva_finais_repetidos(self):
        with patch("construcao.fim_da_cadeia", return_value="fim"):
            pares = construir(list("ABCD"), 4, 2, 17)
        self.assertEqual(len(pares), 4)
        self.assertEqual([p[0] for p in pares], random.Random(17).sample(list("ABCD"), 4))
        self.assertEqual([p[1] for p in pares], ["fim"] * 4)

    def test_argumentos(self):
        for altura, largura in [(0, 1), (3, 1), (1, 0)]:
            with self.assertRaises(ValueError):
                construir(["A", "B"], altura, largura, 17)
        with self.assertRaises(ValueError):
            fim_da_cadeia("A", ["A"], 0)


class TestBusca(unittest.TestCase):
    def test_indice(self):
        self.assertEqual(indexar([("A", "Z"), ("B", "Z"), ("C", "Y")]),
                         {"Z": ["A", "B"], "Y": ["C"]})

    def test_todas_posicoes(self):
        with patch("busca.calcular_hash", side_effect=hash_brinquedo), \
             patch("busca.reduzir", side_effect=reducao_brinquedo):
            for p in "ABC":
                self.assertEqual(buscar(hash_brinquedo(p), list("ABCDX"), {"D": ["A"]}, 3), p)

    def test_falso_candidato_e_inicio_seguinte(self):
        with patch("busca.calcular_hash", side_effect=hash_brinquedo), \
             patch("busca.reduzir", side_effect=reducao_brinquedo):
            # Final candidato não é prova. X vem antes de A de propósito.
            self.assertEqual(buscar("02", list("ABCDX"), {"D": ["X", "A"]}, 3), "B")
            self.assertIsNone(buscar("02", list("ABCDX"), {"D": ["X"]}, 3))

    def test_vazia_e_largura(self):
        self.assertIsNone(buscar("00", ["A"], {}, 1))
        with self.assertRaises(ValueError):
            buscar("00", ["A"], {}, 0)


class TestIntegracao(unittest.TestCase):
    def test_alvo_fora_da_cobertura(self):
        palavras = carregar_palavras()
        pares = construir(palavras, 4, 1, 17)
        inicios = {inicio for inicio, _ in pares}
        ausente = next(p for p in palavras if p not in inicios)
        self.assertIsNone(buscar(calcular_hash(ausente), palavras, indexar(pares), 1))

    def test_hashes_realmente_presentes(self):
        palavras = carregar_palavras()
        for modo in ["cores", "fixa"]:
            pares = construir(palavras, 8, 5, 17, modo)
            self.assertEqual(pares, construir(palavras, 8, 5, 17, modo))
            indice = indexar(pares)
            for inicio, fim in pares:
                atual = inicio
                for coluna in range(5):
                    alvo = calcular_hash(atual)
                    resposta = buscar(alvo, palavras, indice, 5, modo)
                    self.assertIsNotNone(resposta)
                    self.assertEqual(calcular_hash(resposta), alvo)
                    atual = reduzir(alvo, coluna, palavras, modo)
                self.assertEqual(atual, fim)

    def test_um_passo(self):
        palavras = carregar_palavras()
        pares = construir(palavras, 4, 1, 17)
        indice = indexar(pares)
        for inicio, _ in pares:
            self.assertEqual(buscar(calcular_hash(inicio), palavras, indice, 1), inicio)


if __name__ == "__main__":
    unittest.main()
