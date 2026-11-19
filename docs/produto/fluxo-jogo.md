# Fluxo completo do jogo — Zombie Dice (FRA-687)

Mapa do fluxo ponta a ponta e das transições de estado observadas no código atual, confrontadas com as regras do `README.md` e do norte (`docs/produto/caminho.md`, R1–R9). Documento de base para correções e separação de lógica; **nenhum arquivo de código foi alterado**.

## Arquivos de referência

| Arquivo | Papel no repositório | Observação |
| --- | --- | --- |
| `main.py` | Fluxo principal executável (script de topo). | Base principal do mapeamento. |
| `main_teste.py` | Implementação integrada do fluxo de jogo com salvamento e retomada entre execuções (FRA-689), além de testes embutidos. | Citado nas etapas/transições de interrupção e retomada; o fluxo legado de `main.py` continua separado. |
| `mainAntigo.py` | Versão anterior preservada. | Citado como contraste histórico quando relevante (não é o fluxo vigente). |
| `README.md` | Dinâmica do jogo descrita para avaliação. | Fonte de fidelidade (norte §3). |

## Fluxo ponta a ponta

Cada etapa cita o arquivo e a função/bloco onde ocorre. Referências de linha são do estado atual dos arquivos no repositório.

### 1. Início de partida

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Solicitar quantidade de jogadores | Lê `qtdPlayers` via `input`; enquanto `int(qtdPlayers) < 2` repete o pedido. | `main.py`, bloco principal, L160–165. |
| Cadastrar jogadores | Enquanto `len(players)+1 <= qtdPlayers`, lê nome; rejeita duplicata (`plr in players`); senão registra `players[plr] = (cerebro, passo, tiro)` (tupla com contadores globais zerados). | `main.py`, bloco principal, L169–178. |
| Exibir jogadores | Imprime jogadores cadastrados e aguarda (`sleep`). | `main.py`, `showPlayers()` L70–76; chamada em L181. |
| Inicializar tubo (copo) | Insere 13 dados no copo: 6 verdes (`CPCTPC`), 4 amarelos (`TPCTPC`), 3 vermelhos (`TPTCPT`). | `main.py`, `addDadosCopo()` L22–34; chamada em L189 (após mensagem em L187–188). |
| Exibir copo | Lista índices/dados do copo e aguarda. | `main.py`, `showCopo()` L37–47; chamada em L192. |
| Entrar no laço de partida | Laço `while not WIN or not list(players.keys()):`; se não houver jogadores restantes imprime término, mostra placar e encerra. | `main.py`, bloco principal, L194–198. |

**Diferenças observadas:** o texto de validação diz “maior que 2”, mas a condição aceita `2` (`< 2`). A “partida” é um único processo em memória, sem persistência.

### 2. Início de turno (seleção de jogador)

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Sortear jogador atual | Escolhe aleatoriamente um nome em `players.keys()`; guarda `lastPlayed`; remove o jogador de `players` (`pop`). | `main.py`, bloco principal, L200–204. |
| Zerar contadores do turno | Define `cerebro = 0`, `passo = 0`, `tiro = 0` (globais do turno/jogada corrente). | `main.py`, bloco principal, L206–208. |

**Diferenças observadas:** em `main.py`, o jogador é removido de `players` e não é reinserido, então cada cadastrado joga um turno até esgotar a lista. Já `main_teste.py` mantém uma lista fixa de participantes, avança pelo índice de turno e ignora os eliminados (`Game._next_active()` L40–46, `Game._advance()` L85–86).

### 3. Rolagem (dentro do turno)

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Garantir dados disponíveis no copo | Se `len(copo) <= 2`, limpa `dadosSorteados` e `copo`, repõe 13 dados e sorteia 3; senão apenas sorteia 3 do copo atual. | `main.py`, bloco principal, L212–219; reposição via `addDadosCopo()` L22–34. |
| Pegar 3 dados do tubo | Sorteia 3 índices aleatórios do copo, anexa os dados em `dadosSorteados` e remove cada um do copo (`remove`). | `main.py`, `sortear3Dados(lista_dados_copo)` L140–156; chamadas em L217, L219. |
| Lançar/avaliar cada dado sorteado | Itera os 3 itens de `dadosSorteados`; identifica tipo pela string do dado e sorteia uma face aleatória (`random.choice` sobre a string de 6 faces). | `main.py`, bloco principal, L221–258; `sortearDadoVerde()` L104–113, `sortearDadoAmarelo()` L116–125, `sortearDadoVermelho()` L128–137. |
| Contabilizar face no turno | Para a face sorteada: `C` → `cerebro += 1`; `P` → `passo += 1`; `T` → `tiro += 1` (contadores globais do turno). | `main.py`, bloco principal, L227–232 (verde), L240–245 (amarelo), L252–257 (vermelho). |
| Atualizar/exibir placar do turno | Atribui `placar[playerName] = {'cerebro': cerebro, 'passo': passo, 'tiro': tiro}` e imprime placar de todos os registrados. | `main.py`, `showPlacar()` L50–64; chamada em L262. |

**Diferenças observadas (importantes):**
- **Passos (R5):** ao sair `P`, o código apenas incrementa `passo` e segue; na próxima iteração do turno chama `sortear3Dados` e compra 3 dados novos do copo — **não** mantém o dado de passos para relançar nem completa a mão preservando-o. Em `mainAntigo.py` há tentativa de relançar a mesma face enquanto for `P` (ex.: L123–131), mas isso relança a face do mesmo tipo de dado, não preserva o “mesmo dado” físico para continuar conforme R5.
- **Ramo amarelo:** em `main.py` a condição é `elif dadosSorteados == 'TPCTPC':` (compara a lista inteira com string) em L235, então o dado amarelo não cai nesse ramo e é tratado no `else` como vermelho (usa `sortearDadoVermelho`/faces de vermelho). Em `main_teste.py` ocorre o mesmo padrão em L245 (`elif dadosSorteados == 'TPCTPC':`).
- **Reposição do copo:** a verificação é `len(copo) <= 2` (L212) e, ao repor, limpa também `dadosSorteados`; não há regra explícita de “recolocar dados de cérebros/tiros” separada da recarga total mostrada.

### 4. Avaliação de estado do jogador (após rolagem)

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Derrota por 3 tiros | Se `placar[plr_name]['tiro'] >= 3`: limpa `dadosSorteados` e `copo`, imprime derrota, define `status = "loose"`. | `main.py`, `showStatusPlayer(plr_name)` L82–94. |
| Vitória por 13 cérebros | Se `placar[plr_name]['cerebro'] >= 13`: imprime vitória, mostra placar, define `status = "win"`. | `main.py`, `showStatusPlayer(plr_name)` L94–98. |
| Continuar jogando | Caso contrário `status = "jogando"`. | `main.py`, `showStatusPlayer(plr_name)` L99–101. |
| Reação do laço do turno | `loose` → encerra turno (`break`); `win` → `WIN = True` e encerra turno; senão pergunta se deseja continuar. | `main.py`, bloco principal, L265–270. |

**Variante `main_teste.py`:** `Game.resolve_roll()` elimina o jogador quando os tiros pendentes chegam a 3, zera os contadores pendentes e avança para o próximo jogador ativo (L48–61).

### 5. Fim de turno por decisão do jogador (parar)

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Perguntar continuar/parar | Lê `status = input("Deseja continuar jogando? (s/n): ")` e normaliza com `lower()` (retorno não atribuído). | `main.py`, bloco principal, L273–274. |
| Parar (`n`) | Limpa o copo (`copo.clear()`) e encerra o laço do turno (`break`). | `main.py`, bloco principal, L275–277. |
| Continuar (`s` ou outro valor ≠ `n`) | Não entra no `if status == "n"`; o `while True` do turno repete (nova rolagem). | `main.py`, bloco principal, L210–277. |

**Diferenças observadas (R7/R8):** a pergunta ocorre após cada ciclo de rolagem/avaliação (R8 atendido no formato). Ao parar, os cérebros do turno já foram gravados no `placar` na chamada de `showPlacar()` (L262, L56), mas **não há** zeramento explícito de “tiros para próxima rodada” como regra separada além do reset de contadores ao iniciar um novo turno de outro jogador (L206–208); como o jogador já foi removido de `players` (L204), ele não retorna para novo turno em `main.py`. A limpeza do copo ao parar descarta o estado do tubo.

### 6. Fim de partida

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Sem jogadores restantes | No topo do laço externo, se `not list(players.keys())`: imprime término, chama `showPlacar()` e `break`. | `main.py`, bloco principal, L195–198. |
| Vitória detectada | Ao vencer, `showStatusPlayer` imprime vitória e mostra placar (L94–97) e o bloco principal define `WIN = True` e sai do turno (L268–270). Na próxima avaliação, o laço externo `while not WIN or not list(players.keys())` termina imediatamente: com `WIN` verdadeiro e jogadores restantes, ambos os termos são falsos. Se `players` estiver vazio, o segundo termo é verdadeiro, então a próxima iteração entra no laço, exibe o término/placar e sai pelo `break`. | `main.py`, `showStatusPlayer()` L94–98; bloco principal L194–198, L268–270. |

**Diferenças observadas:** ao atingir 13 cérebros a partida encerra imediatamente se ainda houver jogadores em `players`; quando a lista já está vazia, o laço externo ainda entra uma vez para exibir o término e o placar antes de sair. Não há desempate nem “última rodada” modelados.

### 7. Interrupção e retomada

| Etapa | O que acontece no código | Onde ocorre (arquivo e função/bloco) |
| --- | --- | --- |
| Interromper e salvar (R9) | No fluxo integrado, a opção `sair` serializa o snapshot da partida em JSON e retorna; o snapshot inclui placar, eliminados, jogador/índice atual, contadores pendentes, dados carregados, copo e decisão pendente. | `main_teste.py`, `play()` L140–146; `Game.snapshot()` L88–92; `save_game()` L109–110. |
| Retomar entre execuções (R9) | Se o arquivo salvo existe e o usuário escolhe retomar, lê JSON e restaura o estado da partida antes de voltar ao laço de jogo. | `main_teste.py`, `play()` L122–126; `load_game()` L113–114; `Game.resume()` L94–106. |
| Continuar após retomar lançamento pendente | A decisão de parar/continuar/sair é apresentada antes de um novo lançamento; parar encerra o turno, continuar segue ao próximo lançamento e sair salva novamente. | `main_teste.py`, `play()` L140–151; `Game.stop_turn()` L77–83. |
| Fluxo legado | `main.py` e `mainAntigo.py` não salvam nem restauram estado entre execuções. | Ausente nesses arquivos; o fluxo persistente está em `main_teste.py`. |

**Diferenças observadas (R9):** o fluxo integrado de `main_teste.py` implementa persistência da partida. O fluxo legado em `main.py` permanece sem interrupção/retomada persistente; este mapa registra ambos sem afirmar que os dois executáveis têm o mesmo comportamento.

## Tabela de transições de estado

Colunas: **Estado atual**, **Evento**, **Estado seguinte**, **Condição**. A coluna **Situação no código (vs README)** indica: *Implementa*, *Implementa diferente do README* ou *Não implementa*.

| Estado atual | Evento | Estado seguinte | Condição | Situação no código (vs README) | Evidência (arquivo e função/bloco) |
| --- | --- | --- | --- | --- | --- |
| Partida não iniciada | Configurar jogadores e iniciar | Partida em andamento (tubo pronto, aguardando turno) | `qtdPlayers >= 2` aceito (condição `< 2` para rejeitar) e cadastro concluído; copo preenchido com 13 dados | Implementa diferente do README (validação textual divergente; fluxo de rodada/acúmulo simplificado) | `main.py`, bloco principal L160–192; `addDadosCopo()` L22–34 |
| Aguardando seleção de jogador | Selecionar próximo jogador | Turno iniciado (jogador atual definido, contadores do turno zerados) | Existe jogador em `players`; sorteio aleatório; jogador removido de `players` | Implementa diferente do README (sem rodadas recorrentes com todos os jogadores; remoção impede retorno no mesmo ciclo) | `main.py`, bloco principal L194–208 |
| Turno em andamento (antes da rolagem) | Pegar 3 dados do tubo | Mão pronta para rolagem (3 dados em `dadosSorteados`) | Copo com dados suficientes ou reposto quando `len(copo) <= 2`; `sortear3Dados` retira 3 do copo | Implementa diferente do README (reposição limpa copo/dados sorteados; critério `<= 2` específico do código) | `main.py`, bloco principal L212–219; `sortear3Dados()` L140–156 |
| Mão pronta (3 dados) | Rolar dados | Faces resolvidas no turno | Para cada dado, escolhe face aleatória conforme string do tipo (`C`, `P`, `T`) | Implementa diferente do README (dado amarelo cai no ramo `else` por comparação `dadosSorteados == 'TPCTPC'` em L235, sendo tratado como vermelho) | `main.py`, bloco principal L221–258; `sortearDadoVerde/Amarelo/Vermelho()` L104–137 |
| Faces resolvidas | Resultado = cérebro | Turno em andamento (cérebros do turno +1) | Face sorteada `C` | Implementa (contagem no turno; registro no placar ao exibir) | `main.py`, bloco principal L227–229, L240–242, L252–254; `showPlacar()` L50–64 |
| Faces resolvidas | Resultado = tiro | Turno em andamento (tiros do turno +1) ou derrota se atingir limite | Face sorteada `T`; se total de tiros no placar/turno `>= 3` após avaliação → derrota | Implementa (eliminação por 3 tiros no turno) | `main.py`, bloco principal L231–232, L244–245, L256–257; `showStatusPlayer()` L88–94, L265–267 |
| Faces resolvidas | Resultado = passos (R5) | Turno em andamento (passos do turno +1); dados de passos deveriam ser relançados ao continuar | Face sorteada `P` | Implementa diferente do README (marca passo, mas não preserva o dado para relançar; próxima rolagem compra 3 dados novos) | `main.py`, bloco principal L229–230, L242–243, L254–255, L212–219 |
| Turno em andamento (após avaliação, sem derrota/vitória) | Parar (R7, R8) | Fim do turno do jogador; partida aguarda próximo turno | Jogador responde `n` à pergunta de continuar | Implementa diferente do README (cérebros do turno refletidos no `placar` via `showPlacar`, mas tiros não são explicitamente zerados como regra de transição e o jogador não retorna em nova rodada neste fluxo; copo é limpo) | `main.py`, bloco principal L262–277; `showPlacar()` L50–64 |
| Turno em andamento (após avaliação, sem derrota/vitória) | Continuar (R8) | Nova rolagem no mesmo turno | Jogador não responde `n` (qualquer outra entrada mantém o laço) | Implementa diferente do README (continua rolando, mas sem mecânica correta de passos R5) | `main.py`, bloco principal L210–277 |
| Turno em andamento | Acumular 3 tiros (R6) | Jogador eliminado do jogo; turno encerrado | `placar[plr_name]['tiro'] >= 3` na avaliação | Implementa (marca derrota e encerra turno; jogador já fora de `players`) | `main.py`, `showStatusPlayer()` L88–94; bloco principal L204, L265–267 |
| Turno em andamento | Atingir 13 cérebros | Partida encerrada após o turno atual | `placar[plr_name]['cerebro'] >= 13`; `WIN` passa a verdadeiro e `players` ainda contém ao menos um jogador | Implementa diferente do README (encerra a partida imediatamente; não modela desempate nem última rodada) | `main.py`, `showStatusPlayer()` L94–98; bloco principal L194–198, L268–270 |
| Partida em andamento | Fim de jogadores a sortear | Partida encerrada (término exibido) | `players` vazio ao iniciar iteração do laço externo | Implementa diferente do README (encerramento por esgotamento da lista, não por condição completa de vitória/rodada) | `main.py`, bloco principal L195–198 |
| Partida em andamento | Interromper partida e sair (R9) | Partida persistida para retomada posterior | Jogador escolhe `sair` quando há decisão pendente após lançamento | Implementa em `main_teste.py`; não implementa no fluxo legado de `main.py` | `main_teste.py`, `play()` L140–146; `save_game()` L109–110; ausente em `main.py` |
| Partida interrompida (execução anterior) | Retomar partida (R9) | Partida em andamento no estado salvo | Arquivo JSON encontrado e usuário escolhe retomar | Implementa em `main_teste.py`; não implementa no fluxo legado de `main.py` | `main_teste.py`, `play()` L122–126; `load_game()` L113–114; `Game.resume()` L94–106; ausente em `main.py` |
| Decisão de turno pendente | Continuar após retomada | Mesmo turno continua com estado pendente restaurado | Jogador escolhe `c` | Implementa em `main_teste.py`; mantém cérebros/tiros pendentes e dados de passos carregados para próxima rolagem | `main_teste.py`, `play()` L140–151; `Game.toss()` L63–75; `Game.snapshot()` L88–92 |

## Notas de rastreabilidade

- **Regra de fidelidade:** norte §3 estabelece que a fidelidade às regras do `README.md` vence; este mapa registra o comportamento real observado no código para subsidiar correções posteriores.
- **Escopo respeitado:** nenhuma divergência foi corrigida neste documento ou no código.
- **Conferência sugerida (amostra de 5 transições):** (1) pegar 3 dados — `main.py:sortear3Dados` L140–156; (2) passos R5 — `main.py` L229–230, L242–243, L254–255 e ausência de preservação em L212–219; (3) parar R7/R8 — `main.py` L262–277 e `showPlacar()` L50–64; (4) 3 tiros R6 — `main.py:showStatusPlayer` L88–94; (5) interromper/retomar R9 — `main_teste.py:play()` L122–151, `save_game()` L109–110 e `load_game()` L113–114; contraste: ausente em `main.py`.
