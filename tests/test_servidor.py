"""Testes das ações autoritativas do servidor, sem navegador."""

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servidor import ErroAcao, ServidorPartidas


class TestServidorPartidas(unittest.TestCase):
    def setUp(self):
        self.servidor = ServidorPartidas(rng=random.Random(23))
        self.sala = self.servidor.criar("Ana")
        self.servidor.entrar(self.sala.codigo, "Beto")
        self.servidor.entrar(self.sala.codigo, "Caio")

    def test_estado_completo_tem_tres_jogadores_e_placar(self):
        estado = self.sala.estado()
        self.assertEqual(estado["jogadores"], ["Ana", "Beto", "Caio"])
        self.assertIn(estado["jogador_atual"], estado["jogadores"])
        self.assertEqual(set(estado["placar"]), set(estado["jogadores"]))
        self.assertIn("copo", estado)
        self.assertIn("rng", estado)

    def test_jogador_fora_da_vez_e_recusado_sem_mudar_estado(self):
        atual = self.sala.partida.jogador_atual
        outro = next(nome for nome in self.sala.nomes if nome != atual)
        antes = self.sala.estado()
        with self.assertRaisesRegex(ErroAcao, "não é a vez"):
            self.servidor.agir(self.sala, outro, "rolar")
        self.assertEqual(self.sala.estado(), antes)

    def test_acao_valida_atualiza_estado_serializavel(self):
        atual = self.sala.partida.jogador_atual
        estado = self.servidor.agir(self.sala, atual, "rolar")
        self.assertEqual(estado["resultado"]["jogador"], atual)
        self.assertEqual(len(estado["resultado"]["faces"]), 3)
        self.assertEqual(len(estado["resultado"]["cores"]), 3)
        self.assertEqual(len(estado["placar"]), 3)


if __name__ == "__main__":
    unittest.main()
