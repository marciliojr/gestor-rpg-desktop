# System patterns

## Layout

Três colunas. Sem `QDockWidget` para dados. Listas de página: `objectName="sidePanel"` (min ~260px, max ~360px).

Nav: cabeçalhos `NoItemFlags` (MESA, MUNDO, PREPARAR, JOGAR) na mesma `navList`. API: `select_page(n)`, `nav_page_labels()`, `PAGE_HELP = 8`. Abrir campanha vai para Locais (`select_page(1)`). Mapa só se `page == PAGE_COMBAT` (6).

## Visual

`fit_button` / `polish_buttons` em `styles.py`. Um primário por bloco. Campos no miolo: fundo claro, texto tinta. Campos nas laterais: ardósia, texto gelo.

## Mundo

`locations` (tipo cidade/vila/região/taverna/masmorra/outro) e `people` (elenco; `location_id` e `character_id` opcionais). Pessoas ≠ ficha NPC e ≠ NPC rápido.

## Combate

Grid simples no rail (`CombatGridView.refit()`). Tokens `grid_x`/`grid_y`. Encontro `grid_cols`/`grid_rows`, `location_id`, `notes`, `status` (preparado / em_andamento / encerrado). Iniciativa ou próximo turno promove preparado → em andamento. Iniciativa: rótulos do plugin; PV 0 mudo + riscado.

## Plugins / banco

`validate_attributes` só no Salvar da ficha. Schema v7. Não copiar bestiários copyrighted além dos compêndios anexados pelo usuário.

## Import circular (PDF da campanha)

`sheet_export/__init__.py` não reexporta HTML. `campaigns_page._export_pdf` importa `format_campaign_html` e `write_sheet_pdf` de forma lazy.
