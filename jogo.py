# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
#
# Lógica do jogo Zombie Dice.
#
# Este módulo contém apenas regras e estado da partida. Não faz entrada nem
# saída de usuário (sem input/print): a camada de entrada (main.py) é quem
# lê do teclado e imprime na tela. Assim a lógica pode ser testada sozinha.

import random

# Símbolos das faces dos dados (R2)
CEREBRO = 'C'
PASSO = 'P'
TIRO = 'T'

# Faces de cada tipo de dado (R3).
# Verde: mais cérebros; Vermelho: mais tiros; Amarelo: equilibrado.
DADO_VERDE = (CEREBRO, PASSO, CEREBRO, TIRO, PASSO, CEREBRO)      # 3C 2P 1T
DADO_AMARELO = (TIRO, PASSO, CEREBRO, TIRO, PASSO, CEREBRO)       # 2C 2P 2T
DADO_VERMELHO = (TIRO, PASSO, TIRO, CEREBRO, PASSO, TIRO)         # 1C 2P 3T

QUANTIDADE_VERDE = 6
QUANTIDADE_AMARELO = 4
QUANTIDADE_VERMELHO = 3
TOTAL_DADOS = QUANTIDADE_VERDE + QUANTIDADE_AMARELO + QUANTIDADE_VERMELHO  # 13 (R1)

DADOS_POR_LANCAMENTO = 3          # R4: sempre 3 dados por lançamento
PONTUACAO_VITORIA = 13            # 13 cérebros vencem o jogo
TIROS_PARA_ELIMINAR = 3           # R6: 3 tiros no turno eliminam o jogador

STATUS_JOGANDO = 'jogando'
STATUS_ELIMINADO = 'eliminado'
STATUS_VITORIA = 'vencedor'


def novo_copo():
    """Cria o tubo com os 13 dados (R1): 6 verdes, 4 amarelos e 3 vermelhos."""
    copo = []
    copo.extend([DADO_VERDE] * QUANTIDADE_VERDE)
    copo.extend([DADO_AMARELO] * QUANTIDADE_AMARELO)
    copo.extend([DADO_VERMELHO] * QUANTIDADE_VERMELHO)
    return copo


def reabastecer_copo(copo):
    """Devolve um copo cheio quando não há dados suficientes para o lançamento."""
    if len(copo) >= DADOS_POR_LANCAMENTO:
        return copo
    return novo_copo()


def sortear_dados(copo, quantidade=DADOS_POR_LANCAMENTO):
    """Sorteia `quantidade` dados do copo e os remove dele (R4).

    Retorna uma tupla (dados_sorteados, copo_atualizado). Quando o copo
    ficar com menos dados do que o pedido, o tubo é reabastecido primeiro.
    """
    copo = reabastecer_copo(copo)
    sorteados = []
    for _ in range(quantidade):
        indice = random.randrange(len(copo))
        sorteados.append(copo.pop(indice))
    return sorteados, copo


def sortear_face(dado):
    """Sorteia uma face de um dado. Retorna 'C', 'P' ou 'T'."""
    return random.choice(dado)


def classificar_face(face):
    """Classifica uma face em 'cerebro', 'passo' ou 'tiro'."""
    if face == CEREBRO:
        return 'cerebro'
    if face == PASSO:
        return 'passo'
    if face == TIRO:
        return 'tiro'
    raise ValueError("face inválida: %r" % (face,))


def cor_do_dado(dado):
    """Retorna o nome da cor de um dado ('Verde', 'Amarelo' ou 'Vermelho')."""
    if dado is DADO_VERDE:
        return 'Verde'
    if dado is DADO_AMARELO:
        return 'Amarelo'
    if dado is DADO_VERMELHO:
        return 'Vermelho'
    return 'desconhecido'


class Partida(object):
    """Estado e regras de uma partida de Zombie Dice."""

    def __init__(self, nomes_jogadores):
        nomes = list(nomes_jogadores)
        if len(nomes) < 2:
            raise ValueError("são necessários pelo menos 2 jogadores")
        visto = set()
        for nome in nomes:
            if nome in visto:
                raise ValueError("jogador duplicado: %r" % (nome,))
            visto.add(nome)
        self.jogadores = nomes
        self.placar = {}
        for nome in nomes:
            self.placar[nome] = {'cerebro': 0, 'passo': 0, 'tiro': 0}
        self.copo = novo_copo()
        self.vencedor = None
        self.eliminados = []
        self.jogados = set()
        self.jogador_atual = None
        self.turno = {'cerebro': 0, 'passo': 0, 'tiro': 0}

    def proximo_jogador(self):
        """Escolhe aleatoriamente o próximo jogador que ainda pode jogar.

        Não retorna eliminados (§4: eliminado não volta a jogar) nem quem
        já teve turno. Devolve None quando não resta jogador disponível.
        """
        if self.vencedor is not None:
            return None
        disponiveis = [n for n in self.jogadores
                       if n not in self.eliminados and n not in self.jogados]
        if not disponiveis:
            return None
        return random.choice(disponiveis)

    def iniciar_turno(self, nome):
        """Inicia o turno de `nome` e zera os acumuladores do turno."""
        if nome not in self.placar:
            raise KeyError("jogador não encontrado: %r" % (nome,))
        if self.vencedor is not None:
            raise RuntimeError("já há um vencedor na partida")
        if nome in self.eliminados:
            raise RuntimeError("jogador eliminado não pode jogar: %r" % (nome,))
        self.jogador_atual = nome
        self.turno = {'cerebro': 0, 'passo': 0, 'tiro': 0}
        return nome

    def lancar(self):
        """Executa um lançamento de 3 dados para o jogador da vez.

        Retorna um dicionário com o resultado (não imprime nada).
        """
        if self.jogador_atual is None:
            raise RuntimeError("não há turno iniciado")
        dados, self.copo = sortear_dados(self.copo)
        faces = [sortear_face(dado) for dado in dados]
        for face in faces:
            self.turno[classificar_face(face)] += 1
        return {
            'jogador': self.jogador_atual,
            'dados': dados,
            'faces': faces,
            'cores': [cor_do_dado(dado) for dado in dados],
            'turno': dict(self.turno),
        }

    def estado_do_jogador(self, nome=None):
        """'vencedor', 'eliminado' ou 'jogando' para `nome` (da vez se omitido)."""
        if nome is None:
            nome = self.jogador_atual
        stats = self.placar[nome]
        cerebro = stats['cerebro']
        tiro = stats['tiro']
        if nome == self.jogador_atual:
            cerebro += self.turno['cerebro']
            tiro += self.turno['tiro']
        if cerebro >= PONTUACAO_VITORIA:
            return STATUS_VITORIA
        if tiro >= TIROS_PARA_ELIMINAR:
            return STATUS_ELIMINADO
        return STATUS_JOGANDO

    def parar_turno(self, nome=None):
        """Encerra o turno de `nome` (da vez se omitido).

        Aplica a R7: os cérebros do turno são contabilizados no placar e os
        tiros do turno são zerados. O jogador deixa de ser o da vez.
        """
        if nome is None:
            nome = self.jogador_atual
        self.placar[nome]['cerebro'] += self.turno['cerebro']
        self.placar[nome]['tiro'] = 0
        self.turno = {'cerebro': 0, 'passo': 0, 'tiro': 0}
        self.jogador_atual = None
        self.jogados.add(nome)
        return dict(self.placar[nome])

    def eliminar_jogador(self, nome=None):
        """Marca `nome` como eliminado (R6/§4): não joga mais nesta partida."""
        if nome is None:
            nome = self.jogador_atual
        if nome not in self.eliminados:
            self.eliminados.append(nome)
        self.turno = {'cerebro': 0, 'passo': 0, 'tiro': 0}
        self.jogador_atual = None
        self.jogados.add(nome)
