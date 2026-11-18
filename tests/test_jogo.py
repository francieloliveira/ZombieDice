# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
#
# Testes da lógica do jogo Zombie Dice (módulo jogo.py).
#
# A lógica é testada sem entrada de usuário: sortear_face é substituído por
# falsificações fixas (monkeypatch), então todos os testes são determinísticos.

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jogo


class TestCopo(unittest.TestCase):
    def test_tem_13_dados(self):
        self.assertEqual(len(jogo.novo_copo()), jogo.TOTAL_DADOS)

    def test_quantidade_por_cor(self):
        copo = jogo.novo_copo()
        self.assertEqual(copo.count(jogo.DADO_VERDE), jogo.QUANTIDADE_VERDE)
        self.assertEqual(copo.count(jogo.DADO_AMARELO), jogo.QUANTIDADE_AMARELO)
        self.assertEqual(copo.count(jogo.DADO_VERMELHO), jogo.QUANTIDADE_VERMELHO)

    def test_sortear_dados_remove_do_copo(self):
        copo = jogo.novo_copo()
        dados, copo = jogo.sortear_dados(copo)
        self.assertEqual(len(dados), jogo.DADOS_POR_LANCAMENTO)
        self.assertEqual(len(copo), jogo.TOTAL_DADOS - jogo.DADOS_POR_LANCAMENTO)

    def test_reabastece_copo_quando_ficam_poucos_dados(self):
        copo = jogo.novo_copo()
        for _ in range(4):
            _, copo = jogo.sortear_dados(copo)
        self.assertEqual(len(copo), 1)
        dados, copo = jogo.sortear_dados(copo)
        self.assertEqual(len(dados), jogo.DADOS_POR_LANCAMENTO)
        self.assertEqual(len(copo), jogo.TOTAL_DADOS - jogo.DADOS_POR_LANCAMENTO)


class TestFaces(unittest.TestCase):
    def test_sortear_face_retorna_simbolo_valido(self):
        for dado in (jogo.DADO_VERDE, jogo.DADO_AMARELO, jogo.DADO_VERMELHO):
            self.assertIn(jogo.sortear_face(dado),
                          (jogo.CEREBRO, jogo.PASSO, jogo.TIRO))

    def test_classificar_face(self):
        self.assertEqual(jogo.classificar_face(jogo.CEREBRO), 'cerebro')
        self.assertEqual(jogo.classificar_face(jogo.PASSO), 'passo')
        self.assertEqual(jogo.classificar_face(jogo.TIRO), 'tiro')
        with self.assertRaises(ValueError):
            jogo.classificar_face('X')

    def test_cor_do_dado(self):
        self.assertEqual(jogo.cor_do_dado(jogo.DADO_VERDE), 'Verde')
        self.assertEqual(jogo.cor_do_dado(jogo.DADO_AMARELO), 'Amarelo')
        self.assertEqual(jogo.cor_do_dado(jogo.DADO_VERMELHO), 'Vermelho')


class TestPartida(unittest.TestCase):
    def _mock_faces(self, faces):
        """Substitui sortear_face por uma fila de faces fixas; devolve a original."""
        original = jogo.sortear_face
        fila = list(faces)

        def falso(dado):
            return fila.pop(0) if fila else jogo.PASSO
        jogo.sortear_face = falso
        return original

    def test_rejeita_menos_de_dois_jogadores(self):
        with self.assertRaises(ValueError):
            jogo.Partida(['Ana'])

    def test_rejeita_nomes_duplicados(self):
        with self.assertRaises(ValueError):
            jogo.Partida(['Ana', 'Ana'])

    def test_iniciar_turno_e_lancar(self):
        partida = jogo.Partida(['Ana', 'Bob'])
        original = self._mock_faces([jogo.CEREBRO, jogo.PASSO, jogo.TIRO])
        try:
            partida.iniciar_turno('Ana')
            resultado = partida.lancar()
        finally:
            jogo.sortear_face = original
        self.assertEqual(resultado['jogador'], 'Ana')
        self.assertEqual(len(resultado['faces']), 3)
        self.assertEqual(resultado['turno']['cerebro'], 1)
        self.assertEqual(resultado['turno']['passo'], 1)
        self.assertEqual(resultado['turno']['tiro'], 1)
        self.assertIn(resultado['cores'][0], ('Verde', 'Amarelo', 'Vermelho'))

    def test_tres_tiros_no_turno_eliminam_jogador(self):
        partida = jogo.Partida(['Ana', 'Bob'])
        original = self._mock_faces([jogo.TIRO, jogo.TIRO, jogo.TIRO])
        try:
            partida.iniciar_turno('Ana')
            resultado = partida.lancar()
        finally:
            jogo.sortear_face = original
        self.assertEqual(resultado['turno']['tiro'], 3)
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_ELIMINADO)

    def test_cerebros_do_turno_levam_a_vitoria(self):
        partida = jogo.Partida(['Ana', 'Bob'])
        original = self._mock_faces([jogo.CEREBRO] * 15)
        try:
            partida.iniciar_turno('Ana')
            while partida.estado_do_jogador() != jogo.STATUS_VITORIA:
                partida.lancar()
        finally:
            jogo.sortear_face = original
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_VITORIA)

    def test_parar_turno_contabiliza_cerebros_e_zera_tiros(self):
        partida = jogo.Partida(['Ana', 'Bob'])
        original = self._mock_faces([jogo.CEREBRO, jogo.CEREBRO, jogo.TIRO])
        try:
            partida.iniciar_turno('Ana')
            partida.lancar()
        finally:
            jogo.sortear_face = original
        partida.parar_turno('Ana')
        self.assertEqual(partida.placar['Ana']['cerebro'], 2)
        self.assertEqual(partida.placar['Ana']['tiro'], 0)
        self.assertIsNone(partida.jogador_atual)
        self.assertIn('Ana', partida.jogados)

    def test_jogador_eliminado_nao_é_sorteado_novamente(self):
        partida = jogo.Partida(['Ana', 'Bob', 'Zeca'])
        original = self._mock_faces([jogo.TIRO, jogo.TIRO, jogo.TIRO])
        try:
            partida.iniciar_turno('Ana')
            partida.lancar()
        finally:
            jogo.sortear_face = original
        partida.eliminar_jogador('Ana')
        nomes = []
        while True:
            nome = partida.proximo_jogador()
            if nome is None:
                break
            partida.iniciar_turno(nome)
            partida.parar_turno(nome)
            nomes.append(nome)
        self.assertEqual(sorted(nomes), ['Bob', 'Zeca'])

    def test_proximo_jogador_devolve_none_quando_acabam(self):
        partida = jogo.Partida(['Ana', 'Bob'])
        partida.iniciar_turno('Ana')
        partida.parar_turno('Ana')
        partida.iniciar_turno('Bob')
        partida.parar_turno('Bob')
        self.assertIsNone(partida.proximo_jogador())


if __name__ == '__main__':
    unittest.main()
