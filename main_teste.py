"""Fluxo jogável Zombie Dice com interrupção retomável (FRA-689).

Execute ``python3 main_teste.py`` para jogar ou ``python3 main_teste.py --test``
para rodar os testes do fluxo integrado.
"""

from __future__ import annotations

import json
import random
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, TextIO

DICE = ("CPCTPC",) * 6 + ("TPCTPC",) * 4 + ("TPTCPT",) * 3


@dataclass
class Game:
    players: list[str]
    scores: dict[str, int] = field(init=False)
    eliminated: set[str] = field(default_factory=set)
    turn_index: int = 0
    pending: dict[str, int] = field(default_factory=lambda: {"brains": 0, "footprints": 0, "shots": 0})
    current_player: str | None = None
    carried_dice: list[str] = field(default_factory=list)
    cup: list[str] = field(default_factory=list)
    decision_pending: bool = False

    def __post_init__(self) -> None:
        if len(self.players) < 2 or len(set(self.players)) != len(self.players):
            raise ValueError("A partida precisa de pelo menos dois jogadores distintos")
        self.players = list(self.players)
        self.scores = {name: 0 for name in self.players}
        if self.current_player is None:
            self.current_player = self._next_active(0)

    def _next_active(self, start: int) -> str | None:
        for offset in range(len(self.players)):
            index = (start + offset) % len(self.players)
            if self.players[index] not in self.eliminated:
                self.turn_index = index
                return self.players[index]
        return None

    def resolve_roll(self, dice: list[str], faces: list[str]) -> dict[str, int]:
        """Apply known die faces (also used by roll after random selection)."""
        result = {"brains": 0, "footprints": 0, "shots": 0}
        for die, face in zip(dice, faces):
            result[{"C": "brains", "P": "footprints", "T": "shots"}[face]] += 1
        for key, count in result.items():
            self.pending[key] += count
        self.carried_dice = [die for die, face in zip(dice, faces) if face == "P"]
        if self.pending["shots"] >= 3:
            self.eliminated.add(self.current_player)
            self.pending = {"brains": 0, "footprints": 0, "shots": 0}
            self.carried_dice = []
            self._advance()
        return result

    def toss(self, chooser: Callable[[list[str]], str] = random.choice,
             face_roller: Callable[[str], str] = random.choice) -> dict[str, int]:
        if self.current_player is None:
            raise RuntimeError("Não há jogador ativo")
        if len(self.cup) < 3 - len(self.carried_dice):
            self.cup = list(DICE)
        dice = self.carried_dice + [chooser(self.cup) for _ in range(3 - len(self.carried_dice))]
        for die in dice[len(self.carried_dice):]:
            self.cup.remove(die)
        self.carried_dice = []
        # Passos da jogada anterior são relançados e deixam de estar pendentes.
        self.pending["footprints"] = 0
        return self.resolve_roll(dice, [face_roller(die) for die in dice])

    def stop_turn(self) -> None:
        if self.current_player is None:
            return
        self.scores[self.current_player] += self.pending["brains"]
        self.pending = {"brains": 0, "footprints": 0, "shots": 0}
        self.carried_dice = []
        self._advance()

    def _advance(self) -> None:
        self.current_player = self._next_active(self.turn_index + 1)

    def snapshot(self) -> dict[str, object]:
        return {"players": self.players[:], "scores": dict(self.scores), "eliminated": sorted(self.eliminated),
                "turn_index": self.turn_index, "current_player": self.current_player,
                "pending": dict(self.pending), "carried_dice": self.carried_dice[:], "cup": self.cup[:],
                "decision_pending": self.decision_pending}

    @classmethod
    def resume(cls, saved: dict[str, object]) -> "Game":
        game = cls(list(saved["players"]))
        game.scores = dict(saved["scores"])
        game.eliminated = set(saved["eliminated"])
        game.turn_index = int(saved["turn_index"])
        game.pending = dict(saved["pending"])
        game.carried_dice = list(saved["carried_dice"])
        game.cup = list(saved["cup"])
        game.decision_pending = bool(saved.get("decision_pending", False))
        current = saved["current_player"]
        game.current_player = current if current not in game.eliminated else game._next_active(game.turn_index + 1)
        return game


def save_game(game: Game, path: Path) -> None:
    path.write_text(json.dumps(game.snapshot(), ensure_ascii=False), encoding="utf-8")


def load_game(path: Path) -> Game:
    return Game.resume(json.loads(path.read_text(encoding="utf-8")))


def play(input_stream: TextIO = sys.stdin, output_stream: TextIO = sys.stdout,
         save_path: Path = Path("partida_salva.json"),
         chooser: Callable[[list[str]], str] = random.choice,
         face_roller: Callable[[str], str] = random.choice) -> Game | None:
    """Executa o jogo interativo; ``sair`` grava e termina, ``retomar`` carrega."""
    if save_path.exists():
        output_stream.write("Partida salva encontrada. Retomar? (s/n): ")
        if input_stream.readline().strip().lower() == "s":
            game = load_game(save_path)
        else:
            save_path.unlink()
            game = None
    else:
        game = None
    if game is None:
        output_stream.write("Quantidade de jogadores (mínimo 2): ")
        count = int(input_stream.readline().strip())
        players = []
        for number in range(count):
            output_stream.write(f"Nome do jogador {number + 1}: ")
            players.append(input_stream.readline().strip())
        game = Game(players)
    while game.current_player is not None and max(game.scores.values(), default=0) < 13:
        if game.decision_pending:
            output_stream.write("Continuar, parar ou sair? (c/p/s): ")
            choice = input_stream.readline().strip().lower()
            if choice == "s":
                save_game(game, save_path)
                output_stream.write("Partida salva. Até logo!\n")
                return game
            game.decision_pending = False
            if choice == "p":
                game.stop_turn()
            save_game(game, save_path)
            continue
        rolling_player = game.current_player
        output_stream.write(f"Vez de {rolling_player}; placar {game.scores}; turno {game.pending}\n")
        result = game.toss(chooser, face_roller)
        output_stream.write(f"Lançamento: {result}; placar {game.scores}; turno {game.pending}\n")
        # A eliminação já avança o índice. O próximo jogador deve lançar antes
        # de receber a escolha parar/continuar para o seu próprio turno.
        if rolling_player in game.eliminated:
            continue
        game.decision_pending = True
    if save_path.exists():
        save_path.unlink()
    output_stream.write(f"Fim da partida. Placar: {game.scores}\n")
    return game


class IntegratedResumeTests(unittest.TestCase):
    @staticmethod
    def turn_starts(output: str) -> list[str]:
        return [line.split(";", 1)[0].removeprefix("Vez de ")
                for line in output.splitlines() if line.startswith("Vez de ")]

    def test_interrupt_restart_preserves_score_turn_order_and_partial_roll(self) -> None:
        from io import StringIO
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            # Ana banks 2 brains; Bia rolls a brain, footprint and shot, then exits
            # while the stop/continue decision is still pending.
            scripted_faces = iter(["C", "C", "T", "C", "P", "T"])
            chooser = lambda cup: cup[0]
            face = lambda die: next(scripted_faces)
            first_output = StringIO()
            play(StringIO("3\nAna\nBia\nCaio\np\ns\n"), first_output, path, chooser, face)
            saved = load_game(path)
            before_score = dict(saved.scores)
            self.assertEqual(before_score, {"Ana": 2, "Bia": 0, "Caio": 0})
            self.assertEqual(saved.current_player, "Bia")
            self.assertEqual(saved.pending, {"brains": 1, "footprints": 1, "shots": 1})
            self.assertEqual(len(saved.carried_dice), 1)

            resumed_output = StringIO()
            resumed = play(StringIO("s\ns\n"), resumed_output, path, chooser, lambda die: "C")
            self.assertEqual(resumed.scores, before_score)
            self.assertEqual(resumed.current_player, "Bia")
            # Retomar apresenta a decisão daquele lançamento antes de lançar de novo.
            self.assertTrue(resumed.decision_pending)
            self.assertEqual(resumed.pending, {"brains": 1, "footprints": 1, "shots": 1})
            self.assertEqual(resumed.scores, before_score)
            resumed_output = StringIO()
            play(StringIO("s\np\ns\n"), resumed_output, path, chooser, lambda die: "C")
            uninterrupted_faces = iter(["C", "C", "T", "C", "P", "T"] + ["C"] * 3)
            uninterrupted_output = StringIO()
            play(StringIO("3\nAna\nBia\nCaio\np\np\ns\n"), uninterrupted_output,
                 Path(directory) / "uninterrupted.json", chooser,
                 lambda die: next(uninterrupted_faces, "C"))
            observed_order = (self.turn_starts(first_output.getvalue())
                              + self.turn_starts(resumed_output.getvalue()))
            uninterrupted_order = self.turn_starts(uninterrupted_output.getvalue())
            self.assertEqual(observed_order, uninterrupted_order)
            self.assertEqual(observed_order, ["Ana", "Bia", "Caio"])

    def test_eliminated_player_is_persisted_and_skipped_after_restart(self) -> None:
        from io import StringIO
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            path = Path(directory) / "save.json"
            scripted_faces = iter(["T", "T", "T"] + ["C"] * 9)
            play(StringIO("3\nAna\nBia\nCaio\ns\ns\n"), StringIO(), path,
                 lambda cup: cup[0], lambda die: next(scripted_faces))
            resumed_output = StringIO()
            resumed = play(StringIO("s\np\ns\n"), resumed_output, path,
                           lambda cup: cup[0], lambda die: next(scripted_faces))
            self.assertIn("Ana", resumed.eliminated)
            self.assertEqual(resumed.current_player, "Caio")
            self.assertIn("Ana", resumed.eliminated)
            self.assertNotEqual(resumed.current_player, "Ana")
            self.assertNotIn("Vez de Ana", resumed_output.getvalue())

    def test_next_player_rolls_before_choice_after_elimination(self) -> None:
        from io import StringIO
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as directory:
            output = StringIO()
            faces = iter(["T", "T", "T"] + ["C"] * 9)
            play(StringIO("3\nAna\nBia\nCaio\np\np\ns\n"), output,
                 Path(directory) / "save.json", lambda cup: cup[0],
                 lambda die: next(faces))
            self.assertEqual(self.turn_starts(output.getvalue()), ["Ana", "Bia", "Caio", "Bia"])


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        play()
