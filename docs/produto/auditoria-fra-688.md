# Auditoria FRA-688 — código × regras do README

- **Card:** FRA-688 — Auditar o código contra as regras do README e classificar os achados por severidade.
- **Base auditada:** `6c8033e` (`main`).
- **Arquivo de implementação auditado:** `main.py` (277 linhas), confrontado com `README.md` e `docs/produto/caminho.md`.
- **Método:** leitura integral do código e execução manual roteirizada do jogo, com entradas reais de jogador (sem build e sem suíte de testes). Para não esperar os `time.sleep(3)`, a reprodução usou um harness fora do repositório que neutraliza `time.sleep` e fixa `random.seed(3)`; as transcrições estão no §9. Nenhum arquivo de código foi alterado. O `git-leitura` do revisor foi exercitado localmente contra este worktree e devolveu o diff e o conteúdo deste relatório; a falha relatada na revisão anterior (avisos do Xcode) não se reproduziu aqui.
- **Escopo de arquivos:** este relatório é o único arquivo novo. `main.py`, `main_teste.py`, `mainAntigo.py`, `README.md` e `docs/produto/caminho.md` permanecem intactos.

## 1. Resumo executivo

As **definições** de dados (quantidade, símbolos e faces por cor) estão corretas no código. As **regras de execução** do turno, porém, divergem do README em pontos centrais:

1. Depois do primeiro lançamento do turno, o código volta a processar **os mesmos 3 dados do primeiro lançamento**, enquanto retira outros 3 dados do copo (F-01).
2. O ramo do **dado amarelo nunca executa**, porque compara uma lista com uma string; os 4 dados amarelos são lançados como vermelhos (F-02).
3. Os dados de **passos não são relançados**: o código só soma `passo` e sorteia 3 dados novos, sem recolocar os passos no copo (F-03).
4. Quando o copo fica com 2 ou menos dados, o código **devolve ao copo os dados reservados** (cérebros e tiros) ao repor os 13 (F-04).
5. Os **cérebros não são acumulados** entre turnos: `cerebro` é zerado a cada turno e o placar é sobrescrito; a vitória é testada só contra o total do turno (F-05).
6. Cada jogador joga **um único turno**: o nome é removido de `players` e o jogo termina quando o dicionário esvazia, sem segunda rodada (F-06).

Além disso, há 4 inconsistências de entrada e 2 de texto (F-07 a F-12). Nenhum achado de regra exige decisão do dono: as divergências de R3/R4/R5/R7 e da vitória são correções objetivas do README/norte. O mínimo de jogadores (F-11) não é fixado pelo README; o achado apenas registra que o texto e a condição atual se contradizem, sem propor um mínimo novo.

| Severidade | Quantidade | Achados |
| --- | ---: | --- |
| bug | 4 | F-01, F-02, F-03, F-04 |
| regra errada | 2 | F-05, F-06 |
| inconsistência de entrada | 4 | F-07, F-08, F-09, F-10 |
| inconsistência de texto | 2 | F-11, F-12 |

## 2. Veredito por regra (R1 a R8 + condição de vitória)

| Regra | Exigência (README / norte) | Trecho do código que sustenta o veredito | Veredito |
| --- | --- | --- | --- |
| **R1** | Tubo com 13 dados de 6 faces, de 3 tipos (verde, amarelo, vermelho). | `main.py:22-34` `addDadosCopo()`: 6 verdes + 4 amarelos + 3 vermelhos = 13; cada string tem 6 símbolos (`main.py:13-15`). | **conforme** |
| **R2** | Os dados têm 3 símbolos: cérebro, tiro e passos. | `main.py:13-15` usa `C`, `P`, `T`; `main.py:227-258` trata os três em todos os ramos de cor. | **conforme** |
| **R3** | Vermelho com mais faces de tiro; verde com mais faces de cérebro; amarelo com quantidades iguais de cérebro, tiro e passos. | Definições corretas: verde `CPCTPC` (3C/2P/1T), amarelo `TPCTPC` (2C/2P/2T), vermelho `TPTCPT` (1C/2P/3T) em `main.py:13-15`. Porém `main.py:235` usa `elif dadosSorteados == 'TPCTPC':`, comparação de **lista com string** sempre falsa; o amarelo cai no ramo vermelho (`main.py:247-258`). | **divergente** (F-02) |
| **R4** | No turno, o jogador sempre pega 3 dados do tubo ao acaso e lança os três juntos. | `main.py:140-156` `sortear3Dados()` retira 3 dados do copo; mas o laço `main.py:210-221` chama `sortear3Dados()` de novo e usa `dadosSorteados[0..2]`, que são os 3 dados do primeiro lançamento, não os recém-retirados. | **divergente** (F-01) |
| **R5** | Dado que caiu em "passos" é relançado se o jogador continuar, completando os 3 dados com novos do tubo. | `main.py:229-230` apenas incrementa `passo`; não há retorno dos dados de passos ao copo nem seleção deles para o próximo lançamento. `main.py:219` sorteia 3 dados novos, e o laço reprocessa os 3 antigos (`main.py:221`). | **divergente** (F-01, F-03) |
| **R6** | Ao acumular 3 tiros no turno, o jogador perde e sai do jogo. | `main.py:88-93` `showStatusPlayer()`: `tiro >= 3` → limpa dados/copo, imprime "Perdeu!" e devolve `"loose"`; `main.py:204` remove o jogador de `players` no início do turno; `main.py:265-267` encerra o turno. | **conforme** (o mecanismo existe; a repetição indevida de dados é F-01) |
| **R7** | Ao parar, os cérebros do turno são contabilizados e os tiros são zerados. | Tiros são zerados em `main.py:206-208`. Cérebros **não** são acumulados: `main.py:56` grava `placar[playerName]` com o total do turno (sobrescrevendo o anterior) e `main.py:275-277` apenas encerra o turno, sem somar a um total do jogador. | **divergente** (F-05) |
| **R8** | Após cada lançamento, o jogador escolhe parar ou continuar. | `main.py:272-277` pergunta `(s/n)` após cada lançamento; `s` continua e `n` para. O fluxo existe, mas a leitura da resposta tem as falhas F-07 e F-08. | **conforme** (fluxo), com inconsistências de entrada F-07/F-08 |
| **Vitória** | Comer 13 cérebros primeiro (README, linha 3; norte §1). | `main.py:94` testa `placar[plr_name]['cerebro'] >= 13`. O número **13** coincide com README e norte, mas o valor testado é o total do **turno**, não o acumulado do jogador (F-05). | **divergente na condição**; **conforme na contagem (13)** — ver §3.1 |

## 3. Verificações explícitas exigidas pelo aceite

### 3.1 Contagem de cérebros para vencer: 13 nos três lugares

- **README, linha 3:** "O objetivo é comer 13 cérebros para vencer o jogo".
- **Norte, §1, linha 8:** "vence quem comer 13 cérebros primeiro".
- **Código, `main.py:94`:** `elif placar[plr_name]['cerebro'] >= 13:`.

**Resultado:** a contagem é **13** nos três lugares. Não há divergência de número e, portanto, **não há decisão de dono pendente sobre a contagem**. O que diverge é a **acumulação** (o código testa só o turno e zera o total a cada turno), registrada como F-05. Corrigir a acumulação para 13 é aplicar o README/norte, não escolher um número novo; o norte não foi editado.

### 3.2 Dados que sobram no tubo/copo após o relançamento de passos

O aceite pede verificação explícita de que os dados que sobram permanecem no tubo/copo. O que se observa no código:

- `sortear3Dados()` (`main.py:149-153`) escolhe 3 índices, remove **exatamente 3** dados do copo e devolve os 3 escolhidos. Os dados não escolhidos **permanecem** no copo entre um sorteio e outro: 13 → 10 → 7 → 4 → 1.
- Porém, os 3 dados escolhidos incluem os de **passos**, e eles **não voltam ao copo** para serem relançados; o código sorteia 3 dados novos e ainda processa os 3 antigos (F-01/F-03).
- Quando `len(copo) <= 2`, `main.py:212-217` faz `copo.clear(); addDadosCopo()`, repondo os 13 dados. Nesse momento, os dados de **cérebro e tiro já reservados voltam ao copo** e o estado do tubo é descartado (F-04).

**Resultado:** os dados que simplesmente **não foram sorteados** permanecem no copo no curto prazo (13→10→7→4→1), mas o comportamento exigido por R5 — passos voltam, completam-se os 3 com novos do tubo e cérebros/tiros ficam reservados — **não é cumprido**. Veredito: **divergente** (F-03 e F-04), com a ressalva de que o copo não é esvaziado a cada lançamento.

## 4. Achados individuais

> Convenção: **severidade** usa exatamente as categorias do card; **impacto** é uma priorização prática. Linhas se referem a `main.py` na base `6c8033e`.

### F-01 — O laço reprocessa os 3 dados do primeiro lançamento

- **Severidade:** bug. **Impacto:** alto.
- **Arquivo/função:** `main.py`, `sortear3Dados()` (linhas 140-156) e laço principal (linhas 210-221).
- **Comportamento atual:** `dadosSorteados` é global e só é limpo quando o copo é reposto (`main.py:214`) ou quando o jogador perde (`main.py:89`). `sortear3Dados()` faz `dadosSorteados.append(dado)` (`main.py:152`) e devolve `list(dadosSorteados)` (`main.py:156`). No segundo lançamento do turno, o retorno tem 6 dados, mas o laço usa `for i in range(3)` (`main.py:221`), isto é, os índices 0-2 — os **três dados do primeiro lançamento**. Nos lançamentos seguintes, 9, 12 etc., e o mesmo trio continua sendo relançado.
- **Comportamento esperado (README/R4 e R5):** cada lançamento usa exatamente os 3 dados daquele lançamento: os dados de passos que voltaram + dados novos do tubo, completando 3.
- **Reprodução manual:** iniciar `python3 main.py`, informar `2`, nomes `A` e `B`, e responder `s` enquanto o jogador sobreviver (quem leva o terceiro tiro não é mais consultado). Observado com `random.seed(3)`: no turno de A, o primeiro lançamento imprime `Vermelho, Vermelho, Verde` e, após `s`, o segundo lançamento imprime exatamente as mesmas três cores; A leva o terceiro tiro e perde. No turno de B, os três lançamentos seguidos (duas vezes `s`, depois `n`) imprimem `Verde, Vermelho, Vermelho` nas três vezes. Transcrição no §9.2. No nível da função: chamar `sortear3Dados()` duas vezes sem limpar `dadosSorteados` devolve 3 e depois 6 dados; os primeiros 3 do segundo retorno são iguais aos do primeiro.
- **Efeito:** um mesmo dado pode render tiro e depois cérebro no mesmo turno; os dados de passos não são os relançados; o copo é consumido sem que os dados usados correspondam aos sorteados.

### F-02 — Dado amarelo é lançado como vermelho

- **Severidade:** bug. **Impacto:** alto.
- **Arquivo/função:** `main.py`, laço principal, ramo do amarelo (linhas 234-245).
- **Comportamento atual:** `elif dadosSorteados == 'TPCTPC':` compara a **lista** `dadosSorteados` com a **string** `'TPCTPC'`; a igualdade é sempre `False`. Todo dado amarelo cai no `else` (`main.py:247-258`), que chama `sortearDadoVermelho()` e imprime "Vermelho".
- **Comportamento esperado (README/R3):** dado amarelo deve usar `dadoAmarelo = 'TPCTPC'` (2 cérebros, 2 passos, 2 tiros) e ser identificado como amarelo. O teste correto é `dadosSorteados[i] == 'TPCTPC'`.
- **Reprodução manual:** qualquer partida com lançamentos suficientes para sair um amarelo; a saída nunca contém "Dado sorteado: Amarelo" e o amarelo aparece como "Vermelho". Com `random.seed(3)`, os três primeiros dados retirados do copo no turno de A são `Amarelo, Amarelo, Verde`, mas o jogo imprime `Vermelho, Vermelho, Verde` (§9.2). Verificação direta: `['TPCTPC'] == 'TPCTPC'` → `False`.
- **Efeito:** 4 dos 13 dados têm distribuição errada (mais tiros e menos cérebros que o previsto), violando R3.

### F-03 — Passos não são relançados; são apenas contados

- **Severidade:** bug. **Impacto:** alto.
- **Arquivo/função:** `main.py`, laço principal (linhas 221-245, em especial 229-230) e `sortear3Dados()` (linhas 140-156).
- **Comportamento atual:** quando a face é `P`, o código faz apenas `passo += 1` (`main.py:230`, `243`, `256`). Não guarda esses dados, não os recoloca no copo e não os inclui no próximo lançamento. O próximo `sortear3Dados()` retira 3 dados novos do copo e o laço processa o trio antigo (F-01).
- **Comportamento esperado (README/R5):** se o jogador continuar, os dados de passos são os relançados; completa-se a quantidade com novos dados do tubo, sempre lançando os três juntos.
- **Reprodução manual:** responder `s` após um lançamento com passos. O placar mostra `Passo: N`, mas as cores do lançamento seguinte não são as dos passos; são as mesmas do primeiro lançamento (F-01). Nenhum dado de passos é reutilizado.
- **Efeito:** R5 não é implementada; o contador `passo` não tem efeito no fluxo.

### F-04 — Reposição do copo devolve cérebros e tiros reservados

- **Severidade:** bug. **Impacto:** médio.
- **Arquivo/função:** `main.py`, laço principal, reposição do copo (linhas 210-218).
- **Comportamento atual:** quando `len(copo) <= 2`, o código executa `dadosSorteados.clear(); copo.clear(); addDadosCopo()` (`main.py:212-217`). Isso repõe os 13 dados, inclusive os que já tinham saído como cérebro ou tiro e deveriam estar reservados fora do copo até o fim do turno.
- **Comportamento esperado (README/R4, R5, R7):** o tubo contém apenas os dados ainda não lançados; cérebros e tiros ficam reservados, e os passos voltam para completar os 3. A reposição com os 13 deve ocorrer no fim do turno, não no meio.
- **Reprodução manual/estrutural:** com o copo cheio, quatro chamadas de `sortear3Dados()` deixam o copo em 10, 7, 4 e 1; na quinta, o código limpa e repõe 13. Os dados retirados nos quatro primeiros sorteios (12 no total, entre eles cérebros/tiros) voltam ao copo. Observado também no jogo: após 4 blocos de "Sorteando 3 dados!", o copo volta a ter 13.
- **Efeito:** dados já usados no turno voltam a ser sorteados; a composição do tubo deixa de refletir os dados disponíveis.

### F-05 — Cérebros não são acumulados; vitória olha só o turno

- **Severidade:** regra errada. **Impacto:** alto.
- **Arquivo/função:** `main.py`, `showPlacar()` (linhas 50-64), `showStatusPlayer()` (linhas 79-101), laço principal (linhas 206-208 e 275-277).
- **Comportamento atual:** no início de cada turno, `cerebro = 0` (`main.py:206`). A cada lançamento, `showPlacar()` grava/sobrescreve `placar[playerName] = {...}` (`main.py:56`) com o acumulado **daquele turno**; não existe um total do jogador entre turnos. A vitória testa `placar[plr_name]['cerebro'] >= 13` (`main.py:94`), isto é, 13 cérebros **em um único turno**. Ao parar, o código apenas dá `break` (`main.py:275-277`); não soma o turno a um total do jogador.
- **Comportamento esperado (README/R7 e condição de vitória):** ao parar, os cérebros do turno são contabilizados no total do jogador; os tiros são zerados; o primeiro a acumular 13 cérebros vence. O total não pode ser sobrescrito a cada turno.
- **Reprodução manual:** com 2 jogadores, cada um para no primeiro lançamento. O placar final mostra apenas os cérebros daquele turno (ex.: `A: 1`, `B: 3`) e o jogo termina; não há segundo turno para somar. Com `s`, o valor de `Cerebro` cresce dentro do mesmo turno, mas é descartado no turno seguinte.
- **Efeito:** a condição de vitória do README (13 acumulados) não é alcançável pelo fluxo normal; o jogo termina por esvaziamento de `players`, não por 13 cérebros.

### F-06 — Cada jogador joga um único turno; não há rodadas

- **Severidade:** regra errada. **Impacto:** alto.
- **Arquivo/função:** `main.py`, laço principal (linhas 194-208).
- **Comportamento atual:** `playerName = random.choice(list(players.keys()))` e, em seguida, `players.pop(playerName)` (`main.py:200-204`) retiram o jogador do dicionário. Quando `players` fica vazio, o `if` interno do laço (`main.py:195-198`) imprime "O jogo foi terminou!" e dá `break`. Assim, cada jogador joga exatamente um turno e o jogo acaba após uma rodada.
- **Comportamento esperado (README: "para próxima rodada"; R7; norte §1 "partida por turnos"):** os jogadores não eliminados voltam a jogar nas rodadas seguintes, até alguém acumular 13 cérebros; só quem levou 3 tiros sai do jogo.
- **Reprodução manual:** iniciar com 2 jogadores, responder `n` em cada turno. O jogo imprime um turno por jogador e "O jogo foi terminou!"; `players` termina vazio. No código, `players` funciona apenas como conjunto de nomes a consumir, e os valores gravados no cadastro (`players[plr] = cerebro, passo, tiro`, `main.py:174`) nunca são usados.
- **Efeito:** o jogo não tem rodadas; a partida termina sem vencedor na maioria dos casos.

### F-07 — "N" maiúsculo continua o turno

- **Severidade:** inconsistência de entrada. **Impacto:** médio.
- **Arquivo/função:** `main.py`, laço principal, leitura da decisão (linhas 272-275).
- **Comportamento atual:** `status = input("Deseja continuar jogando? (s/n): ")` e `status.lower()` na linha seguinte, mas o resultado de `.lower()` **não é atribuído**. `if status == "n"` só reconhece `n` minúsculo; `N` continua o turno.
- **Comportamento esperado:** a opção `s/n` deve ser lida sem diferenciar maiúsculas de minúsculas (`status = status.lower()` ou `status.lower() == "n"`).
- **Reprodução manual:** responder `N`; o jogo imprime "*** Sorteando 3 dados! ***" e faz outro lançamento em vez de parar. Observado no harness: duas rolagens para o mesmo jogador após `N`.
- **Efeito:** o jogador que digita `N` continua sem querer.

### F-08 — Entrada inválida na decisão é tratada como "continuar"

- **Severidade:** inconsistência de entrada. **Impacto:** médio.
- **Arquivo/função:** `main.py`, laço principal (linhas 272-277).
- **Comportamento atual:** qualquer valor diferente de `"n"` (string vazia, `"x"`, `"0"`, etc.) não entra no `if` e o fluxo segue para o próximo lançamento, como se fosse `s`. Não há mensagem nem nova pergunta.
- **Comportamento esperado:** aceitar apenas `s`/`n` (sem diferenciar caixa) e repetir a pergunta para qualquer outra entrada.
- **Reprodução manual:** responder `x` ou deixar em branco; o jogo faz outro lançamento. Observado: `continue_vazio` e `continue_S` produziram a mesma quantidade de rolagens; `invalid_continue` (`x`) também continuou.
- **Efeito:** entrada inválida é silenciosamente interpretada como decisão de continuar.

### F-09 — Quantidade de jogadores não numérica derruba o jogo

- **Severidade:** inconsistência de entrada. **Impacto:** médio.
- **Arquivo/função:** `main.py`, leitura da quantidade de jogadores (linhas 160-165).
- **Comportamento atual:** `qtdPlayers = input(...)` e `while int(qtdPlayers) < 2:` (`main.py:160`, `163`). Se a entrada não for um inteiro válido (por exemplo `abc`), `int()` lança `ValueError` e o programa termina com traceback.
- **Comportamento esperado:** validar a entrada e repetir a pergunta com mensagem clara, sem traceback.
- **Reprodução manual:** `python3 main.py`, informar `abc`. Observado: `ValueError: invalid literal for int() with base 10: 'abc'`.
- **Efeito:** o jogo não inicia; a falha é apresentada como erro de Python, não como validação.

### F-10 — Nome de jogador vazio é aceito

- **Severidade:** inconsistência de entrada. **Impacto:** baixo.
- **Arquivo/função:** `main.py`, cadastro de jogadores (linhas 167-178).
- **Comportamento atual:** `plr = input(...)` (`main.py:170`); se a entrada for vazia, `"" not in players` é verdadeiro e o jogador é cadastrado com nome vazio (`main.py:174`). Não há validação de vazio.
- **Comportamento esperado:** recusar nome vazio (e repetir a pergunta), como já ocorre com nome duplicado (`main.py:171-173`).
- **Reprodução manual:** informar quantidade `2`, nome vazio e depois `B`; o placar mostra um jogador `""` e o jogo prossegue. Observado: `placar` termina com a chave `''`.
- **Efeito:** jogador sem identificação; placar e mensagens ficam com nome vazio.

### F-11 — Mensagem diz "maior que 2", mas o código aceita 2

- **Severidade:** inconsistência de texto. **Impacto:** baixo.
- **Arquivo/função:** `main.py`, validação da quantidade de jogadores (linhas 163-165).
- **Comportamento atual:** a condição `while int(qtdPlayers) < 2:` rejeita apenas 0 e 1, mas a mensagem é "A quantidade de Usuários deve ser maior que 2!" (`main.py:164`). Quem informa `2` é aceito, contrariando o texto.
- **Comportamento esperado:** mensagem e condição devem dizer a mesma coisa. O README não fixa mínimo de jogadores; se o mínimo for 2, o texto deve ser "maior ou igual a 2" (ou "pelo menos 2"); se for 3, a condição deve ser `<= 2`.
- **Reprodução manual:** informar `1` (repete com a mensagem) e depois `2`; o jogo aceita `2` e inicia.
- **Efeito:** o texto induz o jogador a achar que 2 é inválido.

### F-12 — Texto "O jogo foi terminou!"

- **Severidade:** inconsistência de texto. **Impacto:** baixo.
- **Arquivo/função:** `main.py`, laço principal (linha 196).
- **Comportamento atual:** imprime `'O jogo foi terminou!'` quando `players` fica vazio.
- **Comportamento esperado:** frase correta em português, por exemplo "O jogo terminou!".
- **Reprodução manual:** partida com 2 jogadores, ambos parando; a linha aparece no fim.
- **Efeito:** texto visível ao jogador com erro de concordância.

## 5. Testes de entradas inválidas (resultado observado)

Todos os casos abaixo foram executados manualmente com o jogo real, usando `time.sleep` neutralizado e sementes fixas; a coluna "observado" é o comportamento do código na base `6c8033e`.

| Entrada | O que o jogo fez | Veredito |
| --- | --- | --- |
| `abc` na quantidade de jogadores | `ValueError` e traceback; não inicia | achado F-09 |
| `1` na quantidade | repetiu a pergunta com "deve ser maior que 2"; aceitou `2` em seguida | achado F-11 |
| `0` na quantidade | repetiu a pergunta; aceitou `2` em seguida | conforme (rejeita) |
| `2` na quantidade | aceitou e iniciou | conforme |
| Nome duplicado (`A`, `A`, `B`) | recusou o segundo `A` com "Player já existe! Informe outro nome." | conforme |
| Nome vazio (`""`, depois `B`) | aceitou `""` como jogador | achado F-10 |
| `N` na decisão de continuar | continuou o turno (novo lançamento) | achado F-07 |
| `S` na decisão | continuou o turno | conforme |
| `x` na decisão | continuou o turno, sem aviso | achado F-08 |
| vazio na decisão | continuou o turno, sem aviso | achado F-08 |
| `n` na decisão | parou o turno | conforme |

## 6. Histórias sugeridas (a partir dos achados)

1. **Corrigir o ciclo de dados do turno** — F-01, F-02, F-03 e F-04.
   - Aceite: a cada lançamento, exatamente os dados de passos + dados novos do copo são lançados; `dadosSorteados` é reiniciado por lançamento; o amarelo usa a distribuição `TPCTPC`; cérebros e tiros ficam fora do copo até o fim do turno; o copo só é reposto no fim do turno.
2. **Placar acumulado e rodadas até 13 cérebros** — F-05 e F-06.
   - Aceite: cérebros somam no total do jogador entre turnos; tiros zeram ao parar; jogadores não eliminados voltam na rodada seguinte; o primeiro a acumular 13 cérebros vence; o jogo não termina por esvaziar `players`.
3. **Validar entradas do jogador** — F-07, F-08, F-09 e F-10.
   - Aceite: quantidade numérica válida (sem traceback), nome não vazio e não duplicado, decisão `s`/`n` sem diferenciar caixa e nova pergunta para opção inválida.
4. **Ajustar textos do jogo** — F-11 e F-12.
   - Aceite: a mensagem de quantidade coincide com a condição; "O jogo terminou!" corrigido.

## 7. Arquivos não auditados e riscos residuais

- **`main_teste.py`** é a variante usada para testar interrupção/retomada (R9), explicitamente fora do escopo deste card. Ela repete os mesmos defeitos de R3/R4/R5 (inclusive `elif dadosSorteados == 'TPCTPC'`) e acrescenta manipulação de `nojogo`; se esse arquivo for mantido como implementação, os achados precisam ser reaplicados nele em história própria.
- **`mainAntigo.py`** é o protótipo antigo (sem funções, com repetição de passos dentro de `while`); não é a implementação atual do README e não foi auditado.
- **R9 (interromper e retomar)** não foi analisada, por estar fora do escopo.
- **Ordem dos jogadores:** o código sorteia um jogador por turno; o README não fixa a ordem, então isso não foi tratado como divergência.
- **Aleatoriedade:** os achados de F-01 a F-06 são estruturais e independem da semente; os exemplos com semente servem só para reproduzir a mesma saída.
- **Nenhuma correção foi feita** — o card pede apenas a auditoria classificada. O norte e o README não foram editados.

## 8. Prova desta auditoria

- O card pede **sem suíte**: a verificação foi a execução manual do jogo nos casos descritos em cada achado (entradas e passos acima), com a saída observada registrada neste relatório e as transcrições no §9.
- `git diff --stat 6c8033e..HEAD` mostra apenas `docs/produto/auditoria-fra-688.md`; nenhum arquivo de código foi alterado.

## 9. Apêndice — como revisar e transcrições

### 9.1 Comandos de leitura

O único arquivo novo é este relatório; o head do PR é um commit sobre `6c8033e` (`main`).
Com a ferramenta do revisor:

    git-leitura diff origin/main...origin/francieltechnix/fra-688-auditar-o-codigo-contra-as-regras-do --stat
    # saída esperada: 1 file changed (só docs/produto/auditoria-fra-688.md)

    git-leitura show origin/francieltechnix/fra-688-auditar-o-codigo-contra-as-regras-do:docs/produto/auditoria-fra-688.md

O segundo comando imprime este relatório desde o título. Sem o wrapper:

    git --no-pager diff 6c8033e...HEAD --stat
    git --no-pager show HEAD:docs/produto/auditoria-fra-688.md

Se o `git` do macOS devolver apenas avisos do Xcode, o problema está no shim do Xcode do
ambiente de leitura, não no repositório: usar `/usr/bin/git`, apontar `DEVELOPER_DIR` para a
instalação ativa ou ler o arquivo direto resolve. Neste worktree o `git-leitura` devolveu
`1 file changed` no diff e o texto deste relatório no `show`.

### 9.2 Transcrições das execuções

Execuções reais de `python3 main.py` com `time.sleep` neutralizado e `random.seed(3)`, em
harness fora do repositório. Blocos de placar de outros jogadores aparecem repetidos porque
`showPlacar()` imprime o dicionário inteiro a cada lançamento.

**F-01/F-02 — mesmo trio e amarelo rotulado como vermelho (trecho do turno de A, seguido de `s`):**

```
*** Jogador atual: "A" ***
*** Sorteando 3 dados! ***
Dado sorteado: Vermelho
Face sorteada: T
Dado sorteado: Vermelho
Face sorteada: P
Dado sorteado: Verde
Face sorteada: T
*** Cerebro: 0 Passo: 1 Tiro: 2
Deseja continuar jogando? (s/n): *** Sorteando 3 dados! ***
Dado sorteado: Vermelho
Face sorteada: C
Dado sorteado: Vermelho
Face sorteada: T
Dado sorteado: Verde
Face sorteada: P
*** Cerebro: 1 Passo: 2 Tiro: 3
Jogador: "A" Perdeu!
```

Sonda do mesmo seed, no nível do sorteio: jogador sorteado `A`; dados realmente retirados do
copo `['Amarelo', 'Amarelo', 'Verde']`; `['TPCTPC'] == 'TPCTPC'` → `False`. Os dois primeiros
dados eram amarelos, mas o jogo os rotulou "Vermelho" e sorteou as faces com
`sortearDadoVermelho()` (`TPTCPT`), não com `TPCTPC` (F-02). O segundo lançamento reusou o
mesmo trio de cores, agora com faces novas (`C, T, P`), até A levar o terceiro tiro (F-01).

**F-01 — turno de B, três lançamentos seguidos (duas vezes `s`, depois `n`):**

| Lançamento | Cores impressas | Faces |
| --- | --- | --- |
| 1 | `Verde, Vermelho, Vermelho` | `P, P, C` |
| 2 | `Verde, Vermelho, Vermelho` | `C, P, P` |
| 3 | `Verde, Vermelho, Vermelho` | `C, T, P` |

As três cores são as mesmas do primeiro lançamento; só as faces mudam porque o laço reprocessa
os índices 0-2 de `dadosSorteados` (F-01).

**F-06/F-12 — um turno por jogador e fim sem vencedor (trecho com 2 jogadores, `n` nos dois turnos):**

```
*** Jogador atual: "A" ***
*** Placar: "A"
*** Cerebro: 0 Passo: 1 Tiro: 2
Deseja continuar jogando? (s/n): *** Jogador atual: "B" ***
*** Placar: "B"
*** Cerebro: 0 Passo: 2 Tiro: 1
Deseja continuar jogando? (s/n): O jogo foi terminou!
```

Não há segunda rodada; o jogo termina com 0 cérebro e `players` vazio, sem testar a vitória
por 13 cérebros (F-05/F-06), e imprime o texto com erro de concordância (F-12).

**F-07/F-08 — `N` e `x` continuam o turno:** cada uma dessas entradas (seguida de `n`)
produziu 3 linhas `*** Sorteando 3 dados! ***` — A rolou 2 vezes e B, 1 —, o mesmo fluxo de
`s`. Em ambos os casos A só parou porque levou o terceiro tiro. Com `n` no primeiro turno
(transcrição acima), A rolou uma única vez e passou a vez.

**F-09 — quantidade de jogadores não numérica (`abc`):**

```
Traceback (most recent call last):
  File ".../main.py", line 163, in <module>
    while int(qtdPlayers) < 2:
ValueError: invalid literal for int() with base 10: 'abc'
```

**F-10 — nome vazio aceito (Enter no 1º jogador, `B` no 2º):**

```
*** Jogadores Cadastrados ***
{'': (0, 0, 0), 'B': (0, 0, 0)}
...
*** Placar: ""
```

**F-11 — texto "maior que 2" com `1` e depois `2`:**

```
Informe a quantidade de Players
A quantidade de Usuários deve ser maior que 2!
Informe a quantidade de Players
*** Cadastro de Players ***
...
```

O `2` foi aceito e o jogo iniciou, contrariando a mensagem (F-11).
