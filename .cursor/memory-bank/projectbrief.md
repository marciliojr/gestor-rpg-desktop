# Project brief — Gestor RPG

App desktop local para o mestre: campanhas, mundo (locais e pessoas), fichas, manuais em PDF, catálogo de monstros, combate com grid simples e notas de sessão.

**Versão do produto:** 1.1.0 (2026-08-27)  
**Schema SQLite:** v7 (`locations`, `people`; luta com local/notas/status; ganchos na sessão)

## Sistemas no recorte

- 3D&T Victory (P, H, R + PV/PM/PA; 47 desafios)
- D&D 5e (ficha do plugin; catálogo 109 entradas do compêndio local)

Fora: dungeon com paredes, sync, 3D&T Alpha, Tormenta20.

## Stack

PySide6 + SQLite (FTS5). UI e respostas em português. Sem QMenuBar; três colunas.

## Entrega 1.1

Caderno do mestre no app 1.0: locais, pessoas, lutas com situação, notas da partida. README, CHANGELOG e memory bank alinhados. Binários Linux, Windows e macOS na release GitHub.
