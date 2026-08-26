from __future__ import annotations

import random
import re
from dataclasses import dataclass, field

TOKEN = re.compile(
    r"(?P<sign>[+-])?(?:(?P<count>\d*)d(?P<faces>\d+)|(?P<const>\d+))",
    re.IGNORECASE,
)

ALLOWED_FACES = {4, 6, 8, 10, 12, 20, 100}


@dataclass
class DiceResult:
    expression: str
    total: int
    detail: list = field(default_factory=list)


def roll(expression: str, rng: random.Random | None = None) -> DiceResult:
    rng = rng or random.Random()
    expr = expression.replace(" ", "").lower()
    if not expr:
        raise ValueError("Expressão vazia")

    pos = 0
    total = 0
    detail: list[dict] = []
    first = True

    while pos < len(expr):
        match = TOKEN.match(expr, pos)
        if not match:
            raise ValueError(f"Token inválido em '{expr[pos:]}'")

        sign_s = match.group("sign")
        if not first and sign_s is None:
            raise ValueError("Falta operador + ou - entre termos")
        if sign_s == "-":
            sign = -1
        else:
            sign = 1

        if match.group("faces") is not None:
            count = int(match.group("count") or "1")
            faces = int(match.group("faces"))
            if count < 1 or count > 100:
                raise ValueError("Quantidade de dados deve estar entre 1 e 100")
            if faces not in ALLOWED_FACES:
                raise ValueError("Faces permitidas: d4, d6, d8, d10, d12, d20, d100")
            rolls = [rng.randint(1, faces) for _ in range(count)]
            total += sign * sum(rolls)
            detail.append(
                {
                    "type": "dice",
                    "count": count,
                    "faces": faces,
                    "sign": sign,
                    "rolls": rolls,
                }
            )
        else:
            const = int(match.group("const"))
            total += sign * const
            detail.append({"type": "const", "value": sign * const})

        pos = match.end()
        first = False

    return DiceResult(expression=expression.strip(), total=total, detail=detail)


def format_detail(result: DiceResult) -> str:
    parts: list[str] = []
    for item in result.detail:
        if item["type"] == "dice":
            prefix = "-" if item["sign"] < 0 else ""
            rolls = ", ".join(str(n) for n in item["rolls"])
            parts.append(f"{prefix}{item['count']}d{item['faces']} [{rolls}]")
        else:
            value = int(item["value"])
            parts.append(f"{value:+d}")
    return "  ".join(parts)
