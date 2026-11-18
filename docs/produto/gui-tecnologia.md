# Escolha de tecnologia para a interface gráfica — Zombie Dice (FRA-691)

Documento curto de decisão. **Nenhum código de GUI é escrito aqui**; o protótipo fica para FRA-692.

## Escopo

Comparar Tkinter, pygame e web para um protótipo mínimo que mostre dados rolados (cor e face) e o placar, com botões **Rolar** e **Parar**, sem criar mecânica nova além de R1–R9.

## Comparação

### Dependências a instalar

| Opção | Dependências | Observação |
| --- | --- | --- |
| Tkinter | Nenhuma (biblioteca padrão do Python). | Roda com o `python3` já usado no projeto. |
| pygame | `pygame` via `pip install pygame`. | Pacote nativo/compilado; pode exigir build em alguns ambientes. |
| web | Navegador + servidor HTTP local (ex.: `http.server` ou framework). | Sem dependência Python pesada, mas exige duas camadas (servidor + front-end). |

### Esforço para desenhar dados com cor e face

| Opção | Esforço | Como se desenha o dado |
| --- | --- | --- |
| Tkinter | Baixo. | `Canvas` com retângulo/oval colorido (verde/amarelo/vermelho) e texto da face (C/P/T). |
| pygame | Médio. | Superfícies, `pygame.draw`, fontes e loop de renderização manual. |
| web | Médio. | HTML/CSS (divs coloridos + texto) ou SVG; mais verboso para layout responsivo. |

### Esforço para os botões Rolar e Parar

| Opção | Esforço | Observação |
| --- | --- | --- |
| Tkinter | Baixo. | `Button` com `command` ligado à interface de jogo (FRA-690). |
| pygame | Médio. | Detecção de clique por retângulo e desenho manual do botão. |
| web | Baixo. | `<button>` com evento `click`; exige ponte com o back-end Python. |

### Facilidade de rodar para quem avalia o projeto

| Opção | Facilidade | Observação |
| --- | --- | --- |
| Tkinter | Alta. | Um único comando `python3 gui.py`, sem instalação extra. |
| pygame | Média. | Exige `pip install` e, em alguns SOs, bibliotecas gráficas do sistema. |
| web | Média. | Exige subir servidor e abrir navegador; mais passos para o avaliador. |

## Escolha

**Tkinter.** Motivo em até 5 linhas: zero dependências externas, um único comando para rodar, widgets prontos para botões e `Canvas` suficiente para dados coloridos com face, o que atende ao protótipo mínimo de baixo custo sem alterar R1–R9; pygame e web exigem instalação ou duas camadas (servidor + front-end) para o mesmo resultado.

## Tela do turno

A tela do turno (protótipo FRA-692) exibe, usando a interface de jogo separada (FRA-690):

- **Dados rolados**: 3 dados na mão, cada um com cor (verde/amarelo/vermelho) e face sorteada (C = cérebro, P = passos, T = tiro), conforme R4/R5.
- **Contadores**: cérebros do turno e tiros do turno (e placar acumulado), conforme R6/R7.
- **Botões**: **Rolar** (pega 3 dados e lança, R4/R8) e **Parar** (contabiliza cérebros e zera tiros do turno, R7/R8).
- **Interromper e retomar**: a tela expõe a ação de interromper a partida ligada à transição mapeada em `docs/produto/fluxo-jogo.md` §7 (R9). Na base atual não há persistência entre execuções (R9 não implementado), então o protótipo não inventa mecânica nova de salvamento; apenas reflete o fluxo mapeado e deixa a retomada para as histórias de correção (FRA-689/FRA-690). A escolha de Tkinter não exige mudança em nenhuma regra R1–R9.

## Ligação com o fluxo mapeado

- Rolagem e avaliação: `docs/produto/fluxo-jogo.md` §3 (pegar 3 dados, lançar, contabilizar face) e §4 (derrota por 3 tiros, vitória por 13 cérebros).
- Parar/continuar: §5 (R7/R8).
- Fim de partida: §6.
- Interromper/retomar: §7 (R9), hoje não implementado — ver nota acima.

## Regras não alteradas

Esta decisão não altera R1–R9 do norte (`docs/produto/caminho.md` §2). Apenas escolhe a tecnologia da camada de apresentação.

## Fora de escopo

- Implementar o protótipo (FRA-692).
- Alterar a lógica do jogo (FRA-690).
- Criar mecânica nova além de R1–R9.
