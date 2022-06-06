# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira
import random

import empty as empty

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
rnd = ''


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
def jogadorPerdeu(playerAtual):
    dictPlayers.pop(playerAtual)
    print(f"Jogador {playerAtual} perdeu!")
    return None


def jogadorVenceu(playerAtual):
    print(f"Jogador {playerAtual} Venceu")
    return None


# sorteia 3 dados e retira-os da lista de dados a serem sorteados novamente
def sortear3Dados():
    for i in range(3):
        rnd = random.randint(0, 12)
        dadoSorteado = copo[rnd]
        dadosSorteados.append(dadoSorteado)
        copo.remove(dadoSorteado)
    print("dadosSorteados: ", dadosSorteados)
    print("Copo com dados removidos:", copo)
    return dadosSorteados


addDadosCopo()

mostraCopo()

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

while not WIN:
    # Sorteia qual jogador começa o jogo
    playerAtual = random.choice(list(dictPlayers.keys()))
    print(f"Jogador atual:{playerAtual}")
    lastPlayed = playerAtual
    dictPlayers.pop(playerAtual)

    # TODO implementar verificação do copo vazio
    while True:
        # se copo não estiver vazio sorteie 3 dados
        if copo is not None:
            dadosSorteados = sortear3Dados()
        else:
            print('*** O Copo está vazio! ***')

        for i in range(3):
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

        placar[playerAtual] = cerebro, passo, tiro
        placar[playerAtual] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}
        print('placar:', placar)

        if placar[playerAtual]['tiro'] >= 3:
            jogadorPerdeu(playerAtual)

        if placar[playerAtual]['cerebro'] >= 13:
            jogadorVenceu()
        if input("Deseja continuar jogando? (s/n): ") == "n":
            break
