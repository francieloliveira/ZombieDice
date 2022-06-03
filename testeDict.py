import time
placar = []
player = ''
cerebro = 0
passo = 0
tiro = 0
duplicado = False

qtdPlayers = input('Informe a quantidade de Players \n')

# Solicita quantidade de usuários superior a 2
while int(qtdPlayers) < 2:
    print("Aquantidade de Usuários deve ser maior que 2!")
    qtdPlayers = input('Informe a quantidade de Players \n')    

# # BLOCO SEM PROBLEMAS PARA ADICIONAR USUÁRIO E MOSTRAR
# for indx in range(int(qtdPlayers)):
#     i = indx
#     player = input('Nome do ' + str(i + 1) + 'º Player:\n')
#     ds = {"player":player,"cerebro":cerebro,"passo":passo,"tiro":tiro}
#     placar.append(ds)
# # MOSTRA TODOS OS PLAYERS
# # u = 0
# # while u < int(qtdPlayers):
# #     print('player: ', placar[u])
# #     u = u + 1
# # MOSTRA COM FOR 
# for indx in range(int(qtdPlayers)):
#     print('placar: ', placar[indx])
# # BLOCO SEM PROBLEMAS PARA ADICIONAR USUÁRIO E MOSTRAR
# ###########

### TESTE se Usuário existe####
# for indx in range(int(qtdPlayers)):
#     i = indx
#     player = input('Nome do ' + str(i + 1) + 'º Player:\n')
    
#     #verificar se array está vazio
#     if not placar:
#         ds = {"player":player,"cerebro":cerebro,"passo":passo,"tiro":tiro}
#         placar.append(ds)
#     else:
#         for indx2 in range(int(qtdPlayers)):
#             if placar[indx2]['player'] == player:
#                 print('já existe o usuário: ', player)
#             else:
#                 ds = {"player":player,"cerebro":cerebro,"passo":passo,"tiro":tiro}
#                 placar.append(ds)

# for indx3 in range(len(placar)):
#     print('placar: ', placar[indx3])
###


# if placar[indx2]['player'] == player:
#     ds = {"player":player,"cerebro":cerebro,"passo":passo,"tiro":tiro}
#     placar.append(ds)
#  if not placar:

# print('já existe o usuário: ', player)

### QUase certo, falta verificar o array completo, ele está apenas verificando o ultimo cadastrado
#enquanto o tamanho do placar for menor que a quantidades total de players possíveis

while int(len(placar)) <= int(qtdPlayers) - int(1):
    player = input('Nome do ' + str(len(placar) + 1) + 'º Player:\n')
    #verifica se o placar está vazio
    # if not placar:
    #     player = input('Nome do ' + str(len(placar) + 1) + 'º Player:\n')
    #     ds = {"player": player, "cerebro": cerebro, "passo": passo, "tiro": tiro}
    #     placar.append(ds)
    # se ele não estiver vazio verifique e adicione

    # else:
        #busca na list placar se já existe o nome
### NÃO TA INCREMENTANDO O indx2

    for indx1 in range(len(placar)):
        for value in placar[indx1]['player']:
            if player == placar[indx1]['player']:
                duplicado = True

    if duplicado:
        print("Este nome já esta cadastrado! Informe outro.\n")
        player = input('Nome do ' + str(len(placar) + 1) + 'º Player:\n')
        ds = {"player": player, "cerebro": cerebro, "passo": passo, "tiro": tiro}
        placar.append(ds)

        # else:
        # player = input('Nome do ' + str(len(placar) + 1) + 'º Player:\n')
        # ds = {"player": player, "cerebro": cerebro, "passo": passo, "tiro": tiro}
        # placar.append(ds)
            # indx2 = indx2 + 1

        # print('tamanho do array', len(placar))

for indx3 in range(len(placar)):
    print('placar: ', placar[indx3])
####


    # # teste começando em 1 para deixar a instaciação
    # i = 0
    # # print("len placar:",len(placar))

    # # problema com o dicionário já começa em 1 sem o 0 na instanciação dele
    # while int(len(placar)) <= int(qtdPlayers):
    #     player = input('Nome do ' + str(len(placar) + 1) + 'º Player:\n')

    #     # player = input(f'Nome do ' + i +  'º Player:\n')
    #     placar[i] = {'player':player,'cerebro':cerebro,'passo':passo,'tiro':tiro}

    #     dict = dict(placar[i])
    #     res = not dict
    #     print('testeplayer',dict)

    #     if dict.get(player):
    #         print('já existe o usuário: ', player)
###################

    # else:
    #     placar.append({'player':player,'cerebro':cerebro,'passo':passo,'tiro':tiro})
    #     # placar[i] = {'player':player,'cerebro':cerebro,'passo':passo,'tiro':tiro}

    # print("Is dictionary empty ? : " + str(res))
    # if res:
    #     testeplayer[{''}] = testeplayer['player']
    #     del testeplayer[{''}]
    #     testeplayer.update({'player': player})
    # else:
    #     placar.append({'player': player})


# print('Placar: ', placar)



# for key,value in placar.items():
# 	print(value)

# while x < int(qtdPlayers):
#     Nome = input(f'Nome do ' + str(x + 1)+  'º Player:\n')
    
#     print('placar:',placar[x])
#     # time.sleep(1)

#     if placar == '':
#         print("placar is None!")
#         playerDict = {'player': Nome}
#         placar.append(playerDict)
#         print(placar)
        
#     else:
#         print("Placar is not None!")
#         for i in placar:
#             # traz do placar o primeiro usuário a assim por diante
#             dictOneUser = placar
#             if Nome in dictOneUser.values():
#                 print("Esta Usuário já foi cadastrado! Informe outro.")
#                 print('player', placar)
#             else:
#                 playerDict = {'player': Nome}
#                 placar.append(playerDict)
#                 print('player2', placar)
#     x += 1

# mostra lista de players cadastrados
# y = 0
# while y < int(qtdPlayers):
#     print('player', placar[y])
#     y += 1


# só mostrará a ultima posição alocada no dicionário para a inserção na lista 
# quem realmente possui todos os dados é a lista Tplacar
# neste caso só irá mostrar uma key que é a nome "player" que está no dicionário
# z = 0
# for z in playerDict.keys():
#     print(f'Chave = {z} e Valor = {playerDict[z]}')

# exemplo de como mostrar um dicionário
# computador = {'CPU': 'Intel', 'RAM': '8gb', 'SSD': '250bg'}
# for chave in computador.keys():
#   print(f'Chave = {chave} e Valor = {computador[chave]}')
