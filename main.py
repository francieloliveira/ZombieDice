# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira

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


def mostrar_placar(placar):
    print("#########################################")
    for nome in placar:
        stats = placar[nome]
        print('*** Placar: "%s" \n*** Cerebro: %d Passo: %d Tiro: %d'
              % (nome, stats['cerebro'], stats['passo'], stats['tiro']))
    print("#########################################")


def mostrar_resultado_lancado(resultado):
    print("*** Sorteando 3 dados! ***")
    for indice in range(len(resultado['dados'])):
        print("Dado sorteado: %s" % resultado['cores'][indice])
        print("Face sorteada: %s" % resultado['faces'][indice])


def main():
    qtd_players = ler_qtd_players()
    nomes = ler_nomes(qtd_players)

    partida = jogo.Partida(nomes)

    print("*** Jogadores Cadastrados ***")
    print(partida.jogadores)

    print("*** Iniciando o jogo ***")
    print("*** Inserindo dados no copo ***")
    mostrar_copo(partida.copo)

    while partida.vencedor is None:
        nome = partida.proximo_jogador()
        if nome is None:
            print('O jogo foi terminou!')
            mostrar_placar(partida.placar)
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
                partida.vencedor = nome
                print("Jogador: \"%s\" Venceu!" % nome)
                mostrar_placar(partida.placar)
                break

            mostrar_placar(partida.placar)

            resposta = ler_resposta("Deseja continuar jogando? (s/n): ")
            resposta = resposta.strip().lower()
            if resposta == "n":
                partida.parar_turno(nome)
                print("*** Pontuação contabilizada para \"%s\" ***" % nome)
                mostrar_placar(partida.placar)
                break

    if partida.vencedor is not None:
        print("*** Vencedor: \"%s\" ***" % partida.vencedor)
        mostrar_placar(partida.placar)


if __name__ == '__main__':
    main()
