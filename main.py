# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
import random

player = ''
cerebro = 0
passo = 0
tiro = 0
dictPlayers = {}
placar = {}
copo = []
playerAtual = ''
dadoVerde = ('CPCTPC')
dadoAmarelo = ('TPCTPC')
dadoVermelho = ('TPTCPT')
corDado: str = ''
WIN = False
dadosSorteados = []
rnd = int


# Função para Adicionar 13 dados ao Copo
def addDadosCopo():
    for i in range(6):
        copo.append(dadoVerde)
    for i in range(4):
        copo.append(dadoAmarelo)
    for i in range(3):
        copo.append(dadoVermelho)
    return None


# Função para Mostrar Copo
def mostraCopo():
    for i in range(len(copo)):
        print(f"indice: {i} Copo: {copo[i]}")
    return None


# Função para Sortear face do dado Verde
def sortearDadoVerde():
    faceSorteadoVerde = random.choice(dadoVerde)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoVerde))
    return faceSorteadoVerde


# Função para Sortear face do dado Amarelo
def sortearDadoAmarelo():
    faceSorteadoAmarelo = random.choice(dadoAmarelo)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoAmarelo))
    return faceSorteadoAmarelo


# Função para Sortear face do dado Vermelho
def sortearDadoVermelho():
    faceSorteadoVermelho = random.choice(dadoVermelho)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoVermelho))
    return faceSorteadoVermelho


# Função
def jogadorPerdeu(player_atual):
    dictPlayers.pop(player_atual)
    print(f"Jogador {player_atual} perdeu!")
    return None


def jogadorVenceu(player_atual):
    print(f"Jogador {player_atual} Venceu")
    WIN = True
    return WIN


# sorteia 3 dados e retira-os da lista de dados a serem sorteados novamente
def sortear3Dados():
    for i in range(3):
        rnd = random.randint(0, 12)
        dado = copo[rnd]
        dadosSorteados.append(dado)
        copo.remove(dado)
    print("dadosSorteados: ", dadosSorteados)
    print("Copo com dados removidos:", copo)
    return list(dadosSorteados)

# Solicita a quantidade Total de Players
qtdPlayers = input('Informe a quantidade de Players \n')

# Solicita quantidade de usuários superior a 2
while int(qtdPlayers) < 2:
    print("Aquantidade de Usuários deve ser maior que 2!")
    qtdPlayers = input('Informe a quantidade de Players \n')

# Enquanto a quantidade de players estiver menor que a quantidade Total de Players
print("*** Cadastro de Players ***")
while int(len(dictPlayers) + 1) <= int(qtdPlayers):
    player = input('Nome do ' + str(len(dictPlayers) + 1) + 'º Player: \n')
    if player in dictPlayers:
        print('Player já existe! Informe outro nome.\n')
    else:
        dictPlayers[player] = cerebro, passo, tiro
    # dsplacar['Franciel'] = 1, 2, 3
    # if input("Deseja cadastrar um novo contato (s/n): ") == "n":
    if int(len(dictPlayers) + 1) <= int(qtdPlayers):
        print(f"Precisa adicionar mais {int(qtdPlayers) - int(len(dictPlayers))}")
    else:
        break
print(dictPlayers)

print("*** Iniciando o jogo ***")

# Add 13 dados no copo
print("*** Inserindo dados no copo ***")
addDadosCopo()

# Mostra Copo
mostraCopo()

while not WIN or not list(dictPlayers.keys()):
    # Sorteia qual jogador começa o jogo
    playerAtual = random.choice(list(dictPlayers.keys()))
    print(f"Jogador atual:{playerAtual}")
    lastPlayed = playerAtual
    dictPlayers.pop(playerAtual)

    # TODO implementar verificação do copo vazio
    while True:
        # Se copo estiver com 2 ou menos preencha novamente
        if len(copo) <= 2:
            print('*** O Copo está vazio! ***')
            copo.clear()
            addDadosCopo()
            dadosSorteados = sortear3Dados()
        else:
            dadosSorteados = sortear3Dados()

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
        placar[playerAtual] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}
        print('placar:', placar)

        if placar[playerAtual]['tiro'] >= 3:
            jogadorPerdeu(playerAtual)
            break

        if placar[playerAtual]['cerebro'] >= 13:
            WIN = jogadorVenceu(playerAtual)
            print(placar)
            break

        if input("Deseja continuar jogando? (s/n): ") == "n":
            copo.clear()
            break
