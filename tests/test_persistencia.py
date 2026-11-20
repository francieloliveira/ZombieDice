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
    def test_round_trip_preserva_turno_ordem_eliminacoes_e_ultimo_lancamento(self):
        partida = jogo.Partida(["Ana", "Beto", "Caio"], random=random.Random(42))
        partida.iniciar_turno("Ana")
        resultado = partida.lancar()
        partida.eliminar_jogador("Caio")

        with tempfile.TemporaryDirectory() as diretorio:
            caminho = os.path.join(diretorio, "partida.json")
            persistencia.salvar(partida, resultado, Path(caminho))
            retomada, dados = persistencia.carregar(Path(caminho))

        self.assertEqual(retomada.jogadores, partida.jogadores)
        self.assertEqual(retomada.placar, partida.placar)
        self.assertEqual(retomada.eliminados, ["Caio"])
        self.assertEqual(retomada.jogados, {"Caio"})
        self.assertEqual(retomada.jogador_atual, "Ana")
        self.assertEqual(retomada.turno, partida.turno)
        self.assertEqual(dados, {"cores": resultado["cores"], "faces": resultado["faces"]})
        self.assertEqual(retomada.random.random(), partida.random.random())


if __name__ == "__main__":
    unittest.main()
