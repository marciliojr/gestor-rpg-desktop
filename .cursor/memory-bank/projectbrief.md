# Project brief — Gestor RPG

App desktop local para o mestre: campanhas, fichas, manuais em PDF, catálogo de monstros, combate com grid simples e log de sessão.

**Versão do produto:** 1.0.0 (2026-08-26)  
**Schema SQLite:** v6 (não há v7; “versão sete” do recorte virou o 1.0)

## Sistemas no recorte

- 3D&T Victory (P, H, R + PV/PM/PA; 47 desafios)
- D&D 5e (ficha do plugin; catálogo 109 entradas do compêndio local)

Fora: dungeon com paredes, sync, 3D&T Alpha, Tormenta20.

## Stack

PySide6 + SQLite (FTS5). UI e respostas em português. Sem QMenuBar; três colunas.

## Entrega 1.0

Binário congelado (PyInstaller / AppImage / RPM), README, CHANGELOG, repositório GitHub.
