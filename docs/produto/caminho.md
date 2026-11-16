# Norte — ZombieDice

> Norte do projeto: o que ele é e o que não pode acontecer. Só o dono altera este arquivo.
> Agentes: leiam antes de planejar. Para mudar algo aqui, proponham ao dono (needs_dono); não editem.

## §1 Objetivo

Implementar o jogo de mesa Zombie Dice (dados de zumbi) para jogadores em partida por turnos, em que vence quem comer 13 cérebros primeiro.

## §2 Restrições inegociáveis

- R1: O tubo tem 13 dados de 6 faces, de 3 tipos: verdes, vermelhos e amarelos.
- R2: Os dados têm 3 símbolos: cérebro, tiro e passos.
- R3: Vermelho tem mais faces de tiro; verde tem mais faces de cérebro; amarelo tem quantidades iguais de cérebro, tiro e passos.
- R4: No turno, o jogador sempre pega 3 dados do tubo ao acaso e lança os três juntos.
- R5: Dado que caiu em "passos" é relançado se o jogador continuar, completando os 3 dados com novos do tubo.
- R6: Ao acumular 3 tiros no turno, o jogador perde e sai do jogo.
- R7: Ao parar, os cérebros do turno são contabilizados e os tiros são zerados.
- R8: Após cada lançamento, o jogador escolhe parar ou continuar.
- R9: O jogador pode interromper a partida e voltar depois para continuar jogando.

## §3 Desempate

1. a fidelidade às regras do README vence, por ser a base do projeto e do que foi entregue para avaliação.

## §4 O que nunca se faz

- nunca perder o progresso de partida interrompida e nunca deixar um jogador eliminado continuar jogando.

## §5 Glossário

- Tubo: recipiente com os 13 dados, de onde se tiram 3 por lançamento
- Cérebro: símbolo que conta ponto; 13 cérebros vencem o jogo
- Tiro: símbolo de espingarda; 3 tiros no turno eliminam o jogador
- Passos: a vítima fugiu; o dado é relançado se o jogador continuar
- Turno: vez de um jogador; rodada: todos os jogadores jogam um turno
- Dado verde / amarelo / vermelho: dificuldade fácil / intermediária / difícil
