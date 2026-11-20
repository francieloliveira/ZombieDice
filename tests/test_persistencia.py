"""Testes da persistência usada pela GUI, sem abrir janela."""

import os
import random
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jogo
import persistencia


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.caminho = Path(os.path.join(self.dir.name, "partida.json"))

    def _meio_do_turno(self):
        """Partida de Ana no meio do turno, com o último lançamento na mão.

        É o caso do aceite: interromper, sair e voltar com o estado idêntico.
        """
        partida = jogo.Partida(["Ana", "Beto", "Caio"], random=random.Random(42))
        partida.iniciar_turno("Ana")
        resultado = partida.lancar()
        return partida, resultado

    def test_round_trip_preserva_turno_e_ultimo_lancamento(self):
        partida, resultado = self._meio_do_turno()

        persistencia.salvar(partida, resultado, self.caminho)
        retomada, dados = persistencia.carregar(self.caminho)

        self.assertEqual(retomada.jogadores, partida.jogadores)
        self.assertEqual(retomada.placar, partida.placar)
        self.assertEqual(retomada.jogador_atual, "Ana")
        self.assertEqual(retomada.turno, partida.turno)
        # Copo e dados em passo são o que garante o R5 depois de retomar.
        self.assertEqual(retomada.copo, partida.copo)
        self.assertEqual(retomada.dados_passo, partida.dados_passo)
        self.assertEqual(dados, {"cores": resultado["cores"], "faces": resultado["faces"]})
        self.assertEqual(retomada.random.random(), partida.random.random())

    def test_retomada_lanca_igual_a_partida_original(self):
        partida, resultado = self._meio_do_turno()
        persistencia.salvar(partida, resultado, self.caminho)
        retomada, _ = persistencia.carregar(self.caminho)

        da_original = partida.lancar()
        da_retomada = retomada.lancar()

        self.assertEqual(da_retomada["faces"], da_original["faces"])
        self.assertEqual(da_retomada["cores"], da_original["cores"])
        self.assertEqual(retomada.turno, partida.turno)

    def test_round_trip_preserva_eliminacao_e_jogados(self):
        partida = jogo.Partida(["Ana", "Beto", "Caio"], random=random.Random(7))
        partida.iniciar_turno("Caio")
        partida.lancar()
        partida.eliminar_jogador("Caio")   # eliminado no próprio turno, após três tiros

        persistencia.salvar(partida, None, self.caminho)
        retomada, dados = persistencia.carregar(self.caminho)

        self.assertEqual(retomada.eliminados, ["Caio"])
        self.assertEqual(retomada.jogados, {"Caio"})
        self.assertEqual(retomada.placar, partida.placar)
        self.assertIsNone(retomada.jogador_atual)
        self.assertIsNone(dados)

    def test_nao_grava_partida_com_vencedor(self):
        partida = jogo.Partida(["Ana", "Beto"], random=random.Random(3))
        partida.iniciar_turno("Ana")
        partida.finalizar_vitoria("Ana")
        persistencia.salvar(partida, None, self.caminho)
        self.assertFalse(self.caminho.exists())

    def test_nao_grava_partida_com_vencedor_por_cima_de_save_existente(self):
        partida, resultado = self._meio_do_turno()
        persistencia.salvar(partida, resultado, self.caminho)
        self.assertTrue(self.caminho.exists())

        partida.finalizar_vitoria("Ana")
        persistencia.salvar(partida, resultado, self.caminho)
        self.assertFalse(self.caminho.exists())


if __name__ == "__main__":
    unittest.main()
