from __future__ import annotations


def next_free_cell(
    cols: int, rows: int, occupied: set[tuple[int, int]]
) -> tuple[int, int]:
    cols = max(1, cols)
    rows = max(1, rows)
    for row in range(rows):
        for col in range(cols):
            if (col, row) not in occupied:
                return col, row
    return 0, 0


def token_label(name: str) -> str:
    parts = [part for part in name.replace("(", " ").replace(")", " ").split() if part]
    if len(parts) >= 2:
        return (parts[0][0] + parts[1][0]).upper()
    text = (parts[0] if parts else name).strip()
    return (text[:2] or "?").upper()


def clamp_cell(x: int, y: int, cols: int, rows: int) -> tuple[int, int]:
    return max(0, min(cols - 1, x)), max(0, min(rows - 1, y))
