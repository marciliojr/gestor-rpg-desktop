from __future__ import annotations

import random

import pytest

from gestor_rpg.db import queries
from gestor_rpg.db.connection import Database
from gestor_rpg.modules.dice.parser import format_detail, roll


def test_simple_d20():
    rng = random.Random(0)
    result = roll("d20", rng)
    assert result.total == random.Random(0).randint(1, 20)
    assert result.detail[0]["faces"] == 20
    assert result.detail[0]["count"] == 1


def test_compound_expression_deterministic():
    rng = random.Random(42)
    result = roll("3d6+2", rng)
    expected_rng = random.Random(42)
    expected = sum(expected_rng.randint(1, 6) for _ in range(3)) + 2
    assert result.total == expected
    assert result.expression == "3d6+2"


def test_mixed_dice_and_negative():
    rng = random.Random(7)
    result = roll("1d20+1d4-1", rng)
    expected_rng = random.Random(7)
    expected = expected_rng.randint(1, 20) + expected_rng.randint(1, 4) - 1
    assert result.total == expected
    assert "d20" in format_detail(result)


def test_invalid_faces():
    with pytest.raises(ValueError, match="Faces permitidas"):
        roll("1d7")


def test_missing_operator():
    with pytest.raises(ValueError, match="operador"):
        roll("1d6d4")


def test_empty():
    with pytest.raises(ValueError):
        roll("   ")


def test_clear_dice_history(tmp_path):
    db = Database(tmp_path / "dice.db")
    queries.insert_dice_roll(db.conn, "1d20", 11, [{"faces": 20, "rolls": [11]}])
    queries.insert_dice_roll(db.conn, "2d6", 7, [{"faces": 6, "rolls": [3, 4]}])
    assert queries.list_dice_history(db.conn)
    queries.clear_dice_history(db.conn)
    assert queries.list_dice_history(db.conn) == []
    db.close()
