"""Modelo mínimo de partida e testes de interrupção/retomada (FRA-689).

O snapshot é a forma de guardar uma partida interrompida. Ele inclui a ordem
original, placar, jogadores eliminados e os resultados ainda não contabilizados
do turno atual. O módulo não inicia interação ao ser importado.
"""

from __future__ import annotations

import unittest
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Game:
    players: list[str]
    scores: dict[str, int] = field(init=False)
    eliminated: set[str] = field(default_factory=set)
    turn_index: int = 0
    pending: dict[str, int] = field(default_factory=lambda: {"brains": 0, "turns": 0, "shots": 0})
    current_player: str | None = None

    def __post_init__(self) -> None:
        if len(self.players) < 2 or len(set(self.players)) != len(self.players):
            raise ValueError("A partida precisa de pelo menos dois jogadores distintos")
        self.players = list(self.players)
        self.scores = {name: 0 for name in self.players}
        self.current_player = self._next_active(self.turn_index)

    def _next_active(self, start: int) -> str | None:
        for offset in range(len(self.players)):
            index = (start + offset) % len(self.players)
            if self.players[index] not in self.eliminated:
                self.turn_index = index
                return self.players[index]
        return None

    def record_roll(self, brains: int = 0, turns: int = 0, shots: int = 0) -> None:
        """Registra os símbolos do lançamento ainda pertencentes ao turno atual."""
        if self.current_player is None:
            raise RuntimeError("Não há jogador ativo")
        if min(brains, turns, shots) < 0:
            raise ValueError("Os resultados não podem ser negativos")
        self.pending["brains"] += brains
        self.pending["turns"] += turns
        self.pending["shots"] += shots
        if self.pending["shots"] >= 3:
            self.eliminated.add(self.current_player)
            self.pending = {"brains": 0, "turns": 0, "shots": 0}
            self._advance()

    def stop_turn(self) -> None:
        """Deposita cérebros, zera tiros e passa ao próximo jogador ativo."""
        if self.current_player is None:
            return
        self.scores[self.current_player] += self.pending["brains"]
        self.pending = {"brains": 0, "turns": 0, "shots": 0}
        self._advance()

    def _advance(self) -> None:
        if self.current_player is None:
            return
        self.current_player = self._next_active(self.turn_index + 1)

    def snapshot(self) -> dict[str, Any]:
        """Retorna todos os dados necessários para retomar sem perda de estado."""
        return {
            "players": list(self.players),
            "scores": dict(self.scores),
            "eliminated": sorted(self.eliminated),
            "turn_index": self.turn_index,
            "current_player": self.current_player,
            "pending": dict(self.pending),
        }

    @classmethod
    def resume(cls, saved: dict[str, Any]) -> "Game":
        game = cls(list(saved["players"]))
        game.scores = dict(saved["scores"])
        game.eliminated = set(saved["eliminated"])
        game.turn_index = saved["turn_index"]
        game.pending = dict(saved["pending"])
        game.current_player = saved["current_player"]
        if game.current_player in game.eliminated:
            game.current_player = game._next_active(game.turn_index + 1)
        return game


class ResumeGameTests(unittest.TestCase):
    def test_snapshot_preserves_scores_and_partial_turn_and_resumes_current_player(self) -> None:
        game = Game(["Ana", "Bia", "Caio"])
        game.record_roll(brains=2, turns=1, shots=1)
        game.stop_turn()
        self.assertEqual(game.current_player, "Bia")
        game.record_roll(brains=1, turns=1, shots=1)
        before = dict(game.scores)

        resumed = Game.resume(game.snapshot())

        self.assertEqual(resumed.scores, before)
        self.assertEqual(resumed.current_player, "Bia")
        self.assertEqual(resumed.pending, {"brains": 1, "turns": 1, "shots": 1})
        resumed.stop_turn()
        self.assertEqual(resumed.scores, {"Ana": 2, "Bia": 1, "Caio": 0})
        self.assertEqual(resumed.current_player, "Caio")

    def test_eliminated_player_stays_out_and_gets_no_turn_after_resume(self) -> None:
        game = Game(["Ana", "Bia", "Caio"])
        game.record_roll(shots=3)
        self.assertIn("Ana", game.eliminated)
        self.assertEqual(game.current_player, "Bia")

        resumed = Game.resume(game.snapshot())

        self.assertIn("Ana", resumed.eliminated)
        self.assertEqual(resumed.current_player, "Bia")
        resumed.stop_turn()
        self.assertEqual(resumed.current_player, "Caio")

    def test_saved_snapshot_is_independent_from_later_mutations(self) -> None:
        game = Game(["Ana", "Bia"])
        game.record_roll(brains=1)
        saved = game.snapshot()
        game.record_roll(shots=1)
        self.assertEqual(saved["pending"], {"brains": 1, "turns": 0, "shots": 0})


if __name__ == "__main__":
    unittest.main()
