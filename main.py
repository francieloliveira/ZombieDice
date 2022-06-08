# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira


import random
import time

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
status: str = ''


def addDadosCopo() -> None:
    """
        Função para Adicionar 13 dados ao Copo.

    :return: None.
    """
    for j in range(6):
        copo.append(dadoVerde)
    for k in range(4):
        copo.append(dadoAmarelo)
    for m in range(3):
        copo.append(dadoVermelho)
    return None


def showCopo() -> None:
    """
    Função para Mostrar Copo.

    :return: None.
    """
    for n in range(len(copo)):
        print(f"Index: {n} Copo: {copo[n]}")
    return None


def showPlacar() -> None:
    """
    Mostra o placar dos jogadores.

    :return: None.
    """
    placar[playerName] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}
    print('placar:', placar)
    return None


def showPlayers() -> None:
    """
    Mostra os Jogadores Cadastrados.

    :return: None.
    """
    print("\n::::::::::::::::::::::::::::::::::::")
    print(f'{":: ":<12}{"Jogadores Cadastrados"}{" ::":>12}')
    print(dic_players)
    print("::::::::::::::::::::::::::::::::::::")

    pass


def showStatusPlayer(plr_name: str) -> str:
    """
    Verifica o estado do jogador atual.

    :param plr_name: recebe o nome do jogador.
    :return: retorna o estado do jogador.
    """

    global status
    if placar[plr_name]['tiro'] >= 3:
        dadosSorteados.clear()
        copo.clear()
        status = "loose"
        print('Dicionario Players', dic_players)
        print(f"Jogador {plr_name} perdeu!")
        time.sleep(3)
    elif placar[plr_name]['cerebro'] >= 13:
        print(f"Jogador {plr_name} Venceu!")
        showPlacar()
        status = "win"
    else:
        status = "jogando"

    return status


def sortearDadoVerde() -> str:
    """
    Função para Sortear face do dado Verde.

    :return: retorna a face do dado Sorteado Verde.
    """
    face_sorteado_verde = random.choice(dadoVerde)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_verde))
    return face_sorteado_verde


def sortearDadoAmarelo() -> str:
    """
    Função para Sortear face do dado Amarelo.

    :return: retorna a face do dado Sorteado Amarelo.
    """
    face_sorteado_amarelo = random.choice(dadoAmarelo)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_amarelo))
    return face_sorteado_amarelo


def sortearDadoVermelho() -> str:
    """
    Função para Sortear face do dado Vermelho.

    :return: retorna a face do dado Sorteado Vermelho.
    """
    face_sorteado_vermelho = random.choice(dadoVermelho)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(face_sorteado_vermelho))
    return face_sorteado_vermelho


def retira3DadosCopo(lista_dados_copo: list) -> list:
    """
    Retira 3 dados do e retira-os da lista de dados a serem sorteados novamente.
    
    :param lista_dados_copo: recebe o Copo para ser sorteado 3 dados dele.
    :return: retorna lista dos 3 dados sorteados.
    """
    for p in range(3):
        rnd = random.randint(0, int(len(lista_dados_copo)) - int(1))
        dado = lista_dados_copo[rnd]
        dadosSorteados.append(dado)
        lista_dados_copo.remove(dado)
    print("dadosSorteados: ", dadosSorteados)
    print("Copo com dados removidos:", lista_dados_copo)
    return list(dadosSorteados)


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

# Mostra os jogadores cadastrados
showPlayers()

print("*** Iniciando o jogo ***")

# Add 13 dados no copo
print("*** Inserindo dados no copo ***")
addDadosCopo()

# Mostra Copo
showCopo()

while not WIN or not list(dic_players.keys()):
    if not list(dic_players.keys()):
        print('O jogo foi terminou!')
        showPlacar()
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
            dadosSorteados = retira3DadosCopo(copo)
        else:
            dadosSorteados = retira3DadosCopo(copo)

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

        # Verifica estado do jogador
        status = showStatusPlayer(playerName)
        print('status player: ', status)
        if status == "loose":
            break
        if status == "win":
            WIN = True
            break

        # Deseja continuar?
        if input("Deseja continuar jogando? (s/n): ") == "n":
            showPlacar()
            copo.clear()
            break
