# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
#
# Testes da lógica do jogo Zombie Dice (módulo jogo.py).
#
# A lógica é testada sem entrada de usuário: a fonte de aleatoriedade é
# injetada (random.Random ou um falso controlado), então todos os testes são
# determinísticos, sem monkeypatch global.

import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import jogo


class FixoRandom(object):
    """Fonte de aleatoriedade controlada: devolve faces/índices em ordem fixa.

    choice(seq) retorna o próximo face da fila. randrange(n) retorna o próximo
    índice da fila. Suficiente para controlar sortear_face e sortear_dados.
    """

    def __init__(self, faces=None, indices=None):
        self.faces = list(faces or [])
        self.indices = list(indices or [])

    def choice(self, seq):
        return self.faces.pop(0)

    def randrange(self, n):
        return self.indices.pop(0)


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
    def test_rejeita_menos_de_dois_jogadores(self):
        with self.assertRaises(ValueError):
            jogo.Partida(['Ana'])

    def test_rejeita_nomes_duplicados(self):
        with self.assertRaises(ValueError):
            jogo.Partida(['Ana', 'Ana'])

    def test_iniciar_turno_e_lancar(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.CEREBRO, jogo.PASSO, jogo.TIRO],
            indices=[0, 1, 2]))
        partida.iniciar_turno('Ana')
        resultado = partida.lancar()
        self.assertEqual(resultado['jogador'], 'Ana')
        self.assertEqual(len(resultado['faces']), 3)
        self.assertEqual(resultado['turno']['cerebro'], 1)
        self.assertEqual(resultado['turno']['passo'], 1)
        self.assertEqual(resultado['turno']['tiro'], 1)
        self.assertIn(resultado['cores'][0], ('Verde', 'Amarelo', 'Vermelho'))
        self.assertEqual(resultado['placar']['Ana'],
                         {'cerebro': 1, 'passo': 1, 'tiro': 1})
        self.assertEqual(resultado['placar']['Bob'],
                         {'cerebro': 0, 'passo': 0, 'tiro': 0})

    def test_tres_tiros_no_turno_eliminam_jogador(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.TIRO, jogo.TIRO, jogo.TIRO],
            indices=[0, 1, 2]))
        partida.iniciar_turno('Ana')
        resultado = partida.lancar()
        self.assertEqual(resultado['turno']['tiro'], 3)
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_ELIMINADO)

    def test_eliminacao_preserva_acumulado_do_turno_no_placar(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.CEREBRO, jogo.PASSO, jogo.TIRO,
                   jogo.TIRO, jogo.TIRO, jogo.PASSO],
            indices=[0, 1, 2, 3]))
        partida.iniciar_turno('Ana')
        partida.lancar()
        partida.lancar()
        partida.eliminar_jogador('Ana')
        self.assertEqual(partida.placar['Ana'],
                         {'cerebro': 1, 'passo': 2, 'tiro': 3})

    def test_tres_tiros_prevalecem_sobre_vitoria_no_mesmo_lancamento(self):
        """13 cérebros e 3 tiros no mesmo turno: eliminação prevalece (R6)."""
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.TIRO, jogo.PASSO, jogo.PASSO,      # lançamento 1
                   jogo.CEREBRO, jogo.TIRO, jogo.TIRO],     # lançamento 2
            indices=[0, 1, 2, 3]))
        partida.iniciar_turno('Ana')
        partida.placar['Ana']['cerebro'] = 12
        partida.lancar()
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_JOGANDO)
        partida.lancar()
        # cérebros >= 13 e tiros == 3 no mesmo lançamento: eliminado, não vencedor
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_ELIMINADO)

    def test_cerebros_do_turno_levam_a_vitoria(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.CEREBRO, jogo.CEREBRO, jogo.CEREBRO],
            indices=[0, 1, 2]))
        partida.iniciar_turno('Ana')
        partida.placar['Ana']['cerebro'] = 10
        while partida.estado_do_jogador() != jogo.STATUS_VITORIA:
            partida.lancar()
        self.assertEqual(partida.estado_do_jogador('Ana'), jogo.STATUS_VITORIA)

    def test_vitoria_preserva_tiros_no_placar_final(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.CEREBRO, jogo.CEREBRO, jogo.TIRO],
            indices=[0, 1, 2]))
        partida.iniciar_turno('Ana')
        partida.placar['Ana']['cerebro'] = 12
        partida.lancar()
        placar = partida.finalizar_vitoria('Ana')
        self.assertEqual(placar['cerebro'], 14)
        self.assertEqual(placar['tiro'], 1)
        self.assertEqual(partida.vencedor, 'Ana')

    def test_parar_turno_contabiliza_cerebros_e_zera_tiros(self):
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.CEREBRO, jogo.CEREBRO, jogo.TIRO],
            indices=[0, 1, 2]))
        partida.iniciar_turno('Ana')
        partida.lancar()
        partida.parar_turno('Ana')
        self.assertEqual(partida.placar['Ana']['cerebro'], 2)
        self.assertEqual(partida.placar['Ana']['tiro'], 0)
        self.assertIsNone(partida.jogador_atual)
        self.assertIn('Ana', partida.jogados)

    def test_parar_turno_devolve_dados_ao_copo(self):
        """Ao parar, os dados saem de mão e o copo fica cheio para o próximo turno."""
        partida = jogo.Partida(['Ana', 'Bob'], random=random.Random(42))
        partida.iniciar_turno('Ana')
        partida.lancar()   # remove 3 dados do copo
        self.assertEqual(len(partida.copo), jogo.TOTAL_DADOS - jogo.DADOS_POR_LANCAMENTO)
        partida.parar_turno('Ana')
        self.assertEqual(len(partida.copo), jogo.TOTAL_DADOS)

    def test_eliminar_jogador_devolve_dados_ao_copo(self):
        """A eliminação também deixa o tubo cheio para o próximo jogador."""
        partida = jogo.Partida(['Ana', 'Bob'], random=random.Random(42))
        partida.iniciar_turno('Ana')
        partida.lancar()   # remove 3 dados do copo
        self.assertEqual(len(partida.copo), jogo.TOTAL_DADOS - jogo.DADOS_POR_LANCAMENTO)
        partida.eliminar_jogador('Ana')
        self.assertEqual(len(partida.copo), jogo.TOTAL_DADOS)

    def test_passos_sao_relancados_completando_com_novos_dados_do_tubo(self):
        """R5: dados em passo são relançados, completando a mão com dados do tubo."""
        partida = jogo.Partida(['Ana', 'Bob'], random=FixoRandom(
            faces=[jogo.PASSO, jogo.CEREBRO, jogo.PASSO,      # lançamento 1: 2 passos
                   jogo.TIRO, jogo.PASSO, jogo.CEREBRO],       # lançamento 2: relança 2 passos + 1 novo
            indices=[0, 1, 2, 3]))
        partida.iniciar_turno('Ana')

        resultado1 = partida.lancar()
        self.assertEqual(len(resultado1['dados']), 3)
        self.assertEqual(resultado1['turno']['passo'], 2)
        self.assertEqual(resultado1['turno']['cerebro'], 1)
        # 2 dados ficam aguardando relançamento
        self.assertEqual(len(partida.dados_passo), 2)

        resultado2 = partida.lancar()
        # o lançamento seguinte rola exatamente 3 dados (passos salvos + novos do tubo)
        self.assertEqual(len(resultado2['dados']), 3)
        self.assertEqual(resultado2['turno']['tiro'], 1)
        # o copo foi consumido: 3 no lançamento 1 + 1 novo para completar os 3 no lançamento 2
        self.assertEqual(len(partida.copo), 13 - 3 - 1)

    def test_fonte_aleatoria_injetada_torna_lancar_deterministico(self):
        seed = 1234
        p1 = jogo.Partida(['Ana', 'Bob'], random=random.Random(seed))
        p2 = jogo.Partida(['Ana', 'Bob'], random=random.Random(seed))
        p1.iniciar_turno('Ana')
        p2.iniciar_turno('Ana')
        self.assertEqual(p1.lancar()['faces'], p2.lancar()['faces'])
        self.assertEqual(p1.lancar()['faces'], p2.lancar()['faces'])

    def test_jogador_eliminado_nao_é_sorteado_novamente(self):
        partida = jogo.Partida(['Ana', 'Bob', 'Zeca'], random=random.Random(42))
        partida.iniciar_turno('Ana')
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
        partida = jogo.Partida(['Ana', 'Bob'], random=random.Random(42))
        partida.iniciar_turno('Ana')
        partida.parar_turno('Ana')
        partida.iniciar_turno('Bob')
        partida.parar_turno('Bob')
        self.assertIsNone(partida.proximo_jogador())


if __name__ == '__main__':
    unittest.main()
