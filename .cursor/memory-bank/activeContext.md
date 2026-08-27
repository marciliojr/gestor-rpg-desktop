# Active context — 1.1.0

## Estado atual

Release 1.1.0 no GitHub: mundo (locais e pessoas), lutas com situação, notas da partida, CI e binários Linux/Windows/macOS. Schema v7. Nav MESA / MUNDO / PREPARAR / JOGAR. Abrir campanha vai para Locais.

## Não mexer (pedido do usuário)

Hover da nav, selo de rodada, iniciativa “clara” além do que já está, card do mapa (além do zoom já adicionado).

## Empacote

- Local Linux: `./packaging/build-appimage.sh` e `./packaging/build-rpm.sh`
- Release das três plataformas: `python packaging/package-release.py` (artefatos em `dist/upload/`)
- GitHub Actions: `.github/workflows/ci.yml` (pytest) e `release.yml` (tag `v*`)

## Git / GitHub

- Repositório: https://github.com/marciliojr/gestor-rpg-desktop
- Branch padrão: **main** (não há `master`)
- Release 1.0.0 (AppImage): https://github.com/marciliojr/gestor-rpg-desktop/releases/tag/v1.0.0
- Release 1.1.0: https://github.com/marciliojr/gestor-rpg-desktop/releases/tag/v1.1.0
- Commits só a pedido.

## Testes

`python3 -m pytest -q`. Smoke: 8 páginas de mesa na nav agrupada (inclui Locais e Pessoas), grupo MUNDO, `toolsList` com 3 atalhos (sem Sair), Como usar e Sair no rodapé, menubar oculta, mapa só em Combate (índice 6), ajuda no índice 8.
