# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
# TODO Verificar lista de dados jogados (introduzido o clear no perder(verificar))
# TODO Verificar o Dicionario Players (necessidade)
# TODO Verificar incio de nova rodada (sem término prematuro) "passar a vez sem retirar?"

import random

cerebro = 0
passo = 0
tiro = 0
dic_players = {}
placar = {}
copo = []
dadoVerde = ('CPCTPC')
dadoAmarelo = ('TPCTPC')
dadoVermelho = ('TPTCPT')
corDado: str = ''
WIN = False
dadosSorteados = []


def addDadosCopo() -> None:
    """
    Função para Adicionar 13 dados ao Copo.

    :return: None
    """
    for i in range(6):
        copo.append(dadoVerde)
    for i in range(4):
        copo.append(dadoAmarelo)
    for i in range(3):
        copo.append(dadoVermelho)
    return None


def mostraCopo() -> None:
    """
    Função para Mostrar Copo.

    :return: None
    """
    for i in range(len(copo)):
        print(f"Index: {i} Copo: {copo[i]}")
    return None


def sortearDadoVerde() -> str:
    """
    Função para Sortear face do dado Verde.

    :return: Retorna a face do dado Sorteado Verde
    """
    face_sorteado_verde = random.choice(dadoVerde)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_verde))
    return face_sorteado_verde


def sortearDadoAmarelo() -> str:
    """
    Função para Sortear face do dado Amarelo.

    :return: Retorna a face do dado Sorteado Amarelo
    """
    face_sorteado_amarelo = random.choice(dadoAmarelo)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_amarelo))
    return face_sorteado_amarelo


def sortearDadoVermelho() -> str:
    """
    Função para Sortear face do dado Vermelho

    :return: Retorna a face do dado Sorteado Vermelho
    """
    face_sorteado_vermelho = random.choice(dadoVermelho)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_vermelho))
    return face_sorteado_vermelho


def playerPerdeu(plyr_loser: str) -> None:
    """
    Identifica que o Player perdeu.

    :param plyr_loser: Nome do usuário que perdeu.
    :return: None
    """
    # print('Usuário a ser removido:', plyr_loser)
    print('Dicionario Players', dic_players)
    # dic_players.pop(player)
    print(f"Jogador {plyr_loser} perdeu!")
    return None


def jogadorVenceu(plyr_win: str) -> bool:
    """
    Condição de Vitória do jogo é atingida.

    :param plyr_win: Recebe o nome do Player vencedor.
    :return: Variável WIN para encerrar a partida.
    """
    print(f"Jogador {plyr_win} Venceu")
    win = True
    return win


def sortear3Dados(lista_dados_copo: list) -> list:
    """
    Sorteia 3 dados e retira-os da lista de dados a serem sorteados novamente.
    
    :param lista_dados_copo: Recebe o Copo para ser sorteado 3 dados dele
    :return: Retorna lista dos 3 dados sorteados
    """
    for i in range(3):
        rnd = random.randint(0, int(len(lista_dados_copo)) - int(1))
        dado = lista_dados_copo[rnd]
        dadosSorteados.append(dado)
        lista_dados_copo.remove(dado)
    print("dadosSorteados: ", dadosSorteados)
    print("Copo com dados removidos:", lista_dados_copo)
    return list(dadosSorteados)


def showPlacar() -> None:
    """
    Mostra o placar dos jogadores

    :return: None
    """
    placar[playerName] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}
    print('placar:', placar)
    return None


# Solicita a quantidade Total de Players
qtdPlayers = input('Informe a quantidade de Players \n')

# Solicita quantidade de usuários superior a 2
while int(qtdPlayers) < 2:
    print("A quantidade de Usuários deve ser maior que 2!")
    qtdPlayers = input('Informe a quantidade de Players \n')

# Enquanto a quantidade de players estiver menor que a quantidade Total de Players
print("*** Cadastro de Players ***")
while int(len(dic_players) + 1) <= int(qtdPlayers):
    plr = input('Nome do ' + str(len(dic_players) + 1) + 'º Player: \n')
    if plr in dic_players:
        print('Player já existe! Informe outro nome.\n')
    else:
        dic_players[plr] = cerebro, passo, tiro
    if int(len(dic_players) + 1) <= int(qtdPlayers):
        print(f"Precisa adicionar mais {int(qtdPlayers) - int(len(dic_players))}")
    else:
        break

print(dic_players)

print("*** Iniciando o jogo ***")

# Add 13 dados no copo
print("*** Inserindo dados no copo ***")
addDadosCopo()

# Mostra Copo
mostraCopo()

while not WIN or not list(dic_players.keys()):
    if not list(dic_players.keys()):
        print('O jogo foi terminado prematuramente')
        break
    # Sorteia um novo jogador e começa o jogo
    playerName = random.choice(list(dic_players.keys()))
    print(f"Jogador atual:{playerName}")
    lastPlayed = playerName
    dic_players.pop(playerName)

    cerebro = 0
    passo = 0
    tiro = 0

    while True:
        # Se copo estiver com 2 ou menos preencha novamente
        if len(copo) <= 2:
            print('*** O Copo está vazio! ***')
            dadosSorteados.clear()
            copo.clear()
            addDadosCopo()
            dadosSorteados = sortear3Dados(copo)
        else:
            dadosSorteados = sortear3Dados(copo)

        # for i in range(3):
        for i in range(len(dadosSorteados)):
            # Dado Verde
            if dadosSorteados[i] == 'CPCTPC':
                corDado = 'Verde'
                faceSorteadoVerde = sortearDadoVerde()
                # Adiciona valor da face sorteada no placar
                if faceSorteadoVerde == 'C':
                    cerebro += 1
                elif faceSorteadoVerde == 'P':
                    passo += 1
                    # while faceSorteadoVerde == 'P':
                    #     print("Precisa sortear novamente")
                    #     faceSorteadoVerde = sortearDadoVerde()
                    #     if faceSorteadoVerde == 'C':
                    #         cerebro += 1
                    #         break
                    #     if faceSorteadoVerde == 'T':
                    #         tiro += 1
                    #         break
                else:
                    tiro += 1

            # Dado Amarelo
            elif dadosSorteados == 'TPCTPC':
                corDado = 'Amarelo'
                faceSorteadoAmarelo = sortearDadoAmarelo()

                # Adiciona valor da face sorteada no placar
                if faceSorteadoAmarelo == 'C':
                    cerebro += 1
                elif faceSorteadoAmarelo == 'P':
                    passo += 1
                    # while faceSorteadoAmarelo == 'P':
                    #     print("Precisa sortear novamente")
                    #     faceSorteadoAmarelo = sortearDadoAmarelo()
                    #     if faceSorteadoAmarelo == 'C':
                    #         cerebro += 1
                    #         break
                    #     if faceSorteadoAmarelo == 'T':
                    #         tiro += 1
                    #         break
                else:
                    tiro += 1

            # Dado Vermelho
            else:
                corDado = 'Vermelho'
                faceSorteadoVermelho = sortearDadoVermelho()

                # Adiciona valor da face sorteada no placar
                if faceSorteadoVermelho == 'C':
                    cerebro += 1
                elif faceSorteadoVermelho == 'P':
                    passo += 1
                    # while faceSorteadoVermelho == 'P':
                    #     print("Precisa sortear novamente")
                    #     faceSorteadoVermelho = sortearDadoVermelho()
                    #     if faceSorteadoVermelho == 'C':
                    #         cerebro += 1
                    #         break
                    #     if faceSorteadoVermelho == 'T':
                    #         tiro += 1
                    #         break
                else:
                    tiro += 1

        # placar[playerAtual] = cerebro, passo, tiro
        # placar[playerName] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}
        # print('placar:', placar)
        showPlacar()

        # Condição de Derrota
        if placar[playerName]['tiro'] >= 3:
            playerPerdeu(playerName)
            # testando o clear do copo e da lista
            dadosSorteados.clear()
            copo.clear()
            break

        # Condição de Vitória
        if placar[playerName]['cerebro'] >= 13:
            WIN = jogadorVenceu(playerName)
            # print(placar)
            showPlacar()
            break

        # Deseja continuar?
        if input("Deseja continuar jogando? (s/n): ") == "n":
            showPlacar()
            copo.clear()
            break