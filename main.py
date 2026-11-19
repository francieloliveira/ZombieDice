# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira

import random

import jogo


def ler_resposta(mensagem):
    """Lê uma linha do teclado (camada de entrada)."""
    return input(mensagem)


def ler_inteiro(mensagem, minimo):
    """Lê um número inteiro >= minimo do teclado."""
    while True:
        valor = ler_resposta(mensagem)
        try:
            numero = int(valor)
        except ValueError:
            print("Informe um número válido.")
            continue
        if numero < minimo:
            print("O valor deve ser pelo menos %d." % minimo)
            continue
        return numero


def ler_qtd_players():
    """Solicita a quantidade total de players (deve ser maior que 2)."""
    return ler_inteiro('Informe a quantidade de Players \n', 2)


def ler_nomes(qtd_players):
    """Solicita os nomes dos players, sem duplicatas."""
    print("*** Cadastro de Players ***")
    nomes = []
    while len(nomes) < qtd_players:
        plr = ler_resposta('Nome do ' + str(len(nomes) + 1) + 'º Player: \n')
        if plr in nomes:
            print('Player já existe! Informe outro nome.\n')
        else:
            nomes.append(plr)
        if len(nomes) < qtd_players:
            print("Precisa adicionar mais %d" % (qtd_players - len(nomes)))
    return nomes


def mostrar_copo(copo):
    for indice in range(len(copo)):
        print("Index: %d Dado: %s" % (indice, copo[indice]))


def mostrar_placar(partida):
    """Mostra o placar de todos os jogadores.

    Para o jogador da vez, soma os acumulados do turno em andamento
    (cérebros, passos e tiros ainda não contabilizados) ao placar, de modo
    que a tela reflita o estado real depois de cada lançamento — o mesmo
    comportamento observável do terminal antes da separação da lógica.
    """
    print("#########################################")
    for nome in partida.placar:
        stats = partida.placar[nome]
        if partida.jogador_atual == nome:
            turno = partida.turno
        else:
            turno = {'cerebro': 0, 'passo': 0, 'tiro': 0}
        cerebro = stats['cerebro'] + turno['cerebro']
        passo = stats['passo'] + turno['passo']
        tiro = stats['tiro'] + turno['tiro']
        print('*** Placar: "%s" \n*** Cerebro: %d Passo: %d Tiro: %d'
              % (nome, cerebro, passo, tiro))
    print("#########################################")


def mostrar_resultado_lancado(resultado):
    print("*** Sorteando 3 dados! ***")
    for indice in range(len(resultado['dados'])):
        print("Dado sorteado: %s" % resultado['cores'][indice])
        print("Face sorteada: %s" % resultado['faces'][indice])


def main():
    qtd_players = ler_qtd_players()
    nomes = ler_nomes(qtd_players)

    partida = jogo.Partida(nomes, random=random.Random())

    print("*** Jogadores Cadastrados ***")
    print(partida.jogadores)

    print("*** Iniciando o jogo ***")
    print("*** Inserindo dados no copo ***")
    mostrar_copo(partida.copo)

    while partida.vencedor is None:
        nome = partida.proximo_jogador()
        if nome is None:
            print('O jogo foi terminou!')
            mostrar_placar(partida)
            break

        partida.iniciar_turno(nome)
        print("*** Jogador atual: \"%s\" ***" % nome)

        while True:
            resultado = partida.lancar()
            mostrar_resultado_lancado(resultado)

            estado = partida.estado_do_jogador(nome)
            if estado == jogo.STATUS_ELIMINADO:
                print("Jogador: \"%s\" Perdeu!" % nome)
                partida.eliminar_jogador(nome)
                break
            if estado == jogo.STATUS_VITORIA:
                # Contabiliza os cérebros do turno no placar antes de encerrar.
                partida.parar_turno(nome)
                partida.vencedor = nome
                print("Jogador: \"%s\" Venceu!" % nome)
                mostrar_placar(partida)
                break

            mostrar_placar(partida)

            resposta = ler_resposta("Deseja continuar jogando? (s/n): ")
            resposta = resposta.strip().lower()
            if resposta == "n":
                partida.parar_turno(nome)
                print("*** Pontuação contabilizada para \"%s\" ***" % nome)
                mostrar_placar(partida)
                break

    if partida.vencedor is not None:
        print("*** Vencedor: \"%s\" ***" % partida.vencedor)
        mostrar_placar(partida)


if __name__ == '__main__':
    main()
