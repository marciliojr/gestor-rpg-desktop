# Active context — 1.0.0

## Estado atual

Release estável. Schema v6. Nav agrupada. Como usar no rodapé. Exportar campanha JSON + PDF. Sair no rodapé.

## Não mexer (pedido do usuário)

Hover da nav, selo de rodada, iniciativa “clara” além do que já está, card do mapa (além do zoom já adicionado).

## Empacote

- `./packaging/build-appimage.sh` → `dist/gestor-rpg/` e `dist/GestorRPG.AppImage` se houver `appimagetool`
- `./packaging/build-rpm.sh` + `packaging/gestor-rpg.rpm.spec` (Version 1.0.0)

## Git / GitHub

- Repositório: https://github.com/marciliojr/gestor-rpg-desktop
- Release 1.0.0 (AppImage): https://github.com/marciliojr/gestor-rpg-desktop/releases/tag/v1.0.0
- Commits só a pedido (esta entrega pediu repo + README + changelog).

## Testes

`python3 -m pytest -q`. Smoke: 6 páginas de mesa na nav agrupada, `toolsList` com 3 atalhos (sem Sair), Como usar e Sair no rodapé, menubar oculta.
