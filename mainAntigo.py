# Curso: Gestão da Tecnologia da Informação
# Aluno: José Franciel Pires de Oliveira

import random
import time

print("ZOMBIE DICE (PROTÓTIPO SEMANA 4)")
print("Seja bem vindo ao jogo Zombie Dice!\n")

qtdPlayers = input('Informe a quantidade de Players \n')

listaPlayers = []
tiros: int = 0
cerebros: int = 0
passos: int = 0
dadosSorteados = []
corDado: str = ''
keepGoing = True
faceSorteadoVerde = ''
faceSorteadoAmarelo = ''
faceSorteadoVermelho = ''
player = None
# Criando dados
dadoVerde = 'CPCTPC'
dadoAmarelo = 'TPCTPC'
dadoVermelho = 'TPTCPT'
# Criando lista com a quantidade de dados
listaDados = []
indx = ''

# Solicita quantidade de usuários superior a 2
while int(qtdPlayers) < 2:
    print("Aquantidade de Usuários deve ser maior que 2!")
    qtdPlayers = input('Informe a quantidade de Players \n')

# Adiciona nomes a listaPlayers
while int(len(listaPlayers) + 1) <= int(qtdPlayers):
    plr = input('Nome do ' + str(len(listaPlayers) + 1) + 'º Player:\n')
    if plr in listaPlayers:
        print("Este nome já esta cadastrao! Informe outro.\n")
    else:
        listaPlayers.append(plr)
# Mostra a lista de players
# print("Players Registrados:", listaPlayers)
# time.sleep(3)

# Sorteia qual usuário começa o jogo
if player is None:
    player = random.choice(listaPlayers)
    print("\nPlayer sorteado para começar: ", player)

    time.sleep(3)

    # muda o jogador
    # envia o random player para o  index 0 do array e deixa a lista pronta para ser executada
    indx = listaPlayers.index(player)
    # print("indx player: ", indx)
    listaPlayers[indx] = listaPlayers[0]
    # print("listaPlayers[indx] recebe:", listaPlayers[indx])
    listaPlayers[0] = player
    # print("listaPlayers[0] :", listaPlayers[0])
    # print("listaPlayers[indx] novo :", listaPlayers[indx])
    # print("ListaPlayers: ", listaPlayers)

# Adiciona os 13 dados na lista para serem sorteados
for copo in range(6):
    listaDados.append(dadoVerde)
for copo in range(4):
    listaDados.append(dadoAmarelo)
for copo in range(3):
    listaDados.append(dadoVermelho)

# Iniciando o jogo
print('\n::::::: INICIO :::::::')

time.sleep(3)

# Função para sortear face do dado Verde
def sortearDadoVerde():
    faceSorteadoVerde = random.choice(dadoVerde)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoVerde))
    return faceSorteadoVerde


# Função para sortear face do dado Amarelo
def sortearDadoAmarelo():
    faceSorteadoAmarelo = random.choice(dadoAmarelo)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoAmarelo))
    return faceSorteadoAmarelo


# Função para sortear face do dado Vermelho
def sortearDadoVermelho():
    faceSorteadoVermelho = random.choice(dadoVermelho)
    print('Dado sorteado: {}'.format(corDado))
    print('face sorteada: {}'.format(faceSorteadoVermelho))
    return faceSorteadoVermelho


# TODO Separar placar dos jogadores
# TODO Placar unificado

# Para todos os usuários faça
for i in range(len(listaPlayers)):
    player = listaPlayers[i]

    # Sorteando os dados enquanto o jogador não decide parar
    while True:
        # Soteando os dados
        for copo in range(3):
            numSorteado = random.randint(0, 12)
            dadoSorteado = listaDados[numSorteado]
            dadosSorteados.append(dadoSorteado)
            # Dado Verde
            if dadoSorteado == 'CPCTPC':
                corDado = 'Verde'
                faceSorteadoVerde = sortearDadoVerde()

                # Adiciona valor da face sorteada no placar
                if faceSorteadoVerde == 'C':
                    cerebros += 1
                elif faceSorteadoVerde == 'P':
                    passos += 1
                    while faceSorteadoVerde == 'P':
                        print("Precisa sortear novamente")
                        faceSorteadoVerde = sortearDadoVerde()
                        if faceSorteadoVerde == 'C':
                            cerebros += 1
                            break
                        if faceSorteadoVerde == 'T':
                            tiros += 1
                            break
                else:
                    tiros += 1

            # Dado Amarelo
            elif dadoSorteado == 'TPCTPC':
                corDado = 'Amarelo'
                faceSorteadoAmarelo = sortearDadoAmarelo()

                # Adiciona valor da face sorteada no placar
                if faceSorteadoAmarelo == 'C':
                    cerebros += 1
                elif faceSorteadoAmarelo == 'P':
                    passos += 1
                    while faceSorteadoAmarelo == 'P':
                        print("Precisa sortear novamente")
                        faceSorteadoAmarelo = sortearDadoAmarelo()
                        if faceSorteadoAmarelo == 'C':
                            cerebros += 1
                            break
                        if faceSorteadoAmarelo == 'T':
                            tiros += 1
                            break
                else:
                    tiros += 1

            # Dado Vermelho
            else:
                corDado = 'Vermelho'
                faceSorteadoVermelho = sortearDadoVermelho()

                # Adiciona valor da face sorteada no placar
                if faceSorteadoVermelho == 'C':
                    cerebros += 1
                elif faceSorteadoVermelho == 'P':
                    passos += 1
                    while faceSorteadoVermelho == 'P':
                        print("Precisa sortear novamente")
                        faceSorteadoVermelho = sortearDadoVermelho()
                        if faceSorteadoVermelho == 'C':
                            cerebros += 1
                            break
                        if faceSorteadoVermelho == 'T':
                            tiros += 1
                            break
                else:
                    tiros += 1

        # Mostra o Placar
        print("\n::::::::::::::::::::::::::::::::::::")
        print(f'{":: Placar de: ":<12}{player:10}{" ::":>12}')
        print(f'::{" Cérebros":^10}|{"Passos":^10}|{"Tiros ":^10}::')
        print(f'::{cerebros:^10}|{passos:^10}|{tiros:^10}::')
        print("::::::::::::::::::::::::::::::::::::")

        # Perdeu
        if tiros >= 3:
            print("\n::::::: Você Perdeu! :::::::\n")
            time.sleep(3)
            keepGoing = "n"
            cerebros = 0
            passos = 0
            tiros = 0
            print("Próximo jorgador!\n")
            break

        # Ganhou
        if cerebros == 13:
            print("\n::::::: Você Ganhou! ::::::: ")
            time.sleep(3)
            break

        print('\nDeseja Continuar Sorteando os Dados?\n')

        keepGoing = input("Sim = s ou Não = n?\n")

        # guarda o ultimo player e muda de player
        if keepGoing != "s":
            cerebros = 0
            passos = 0
            tiros = 0
            print("Próximo jorgador!\n")
            break
        else:
            pass

