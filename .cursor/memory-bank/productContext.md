# Product context

O mestre precisa da mesa neste computador, sem nuvem. Abre uma campanha (Victory ou 5e), prepara fichas e PDFs, puxa monstros, roda combate e anota a sessão.

## Janela

1. Esquerda `#appSidebar`: marca, campanha, MESA / PREPARAR / JOGAR, FERRAMENTAS, Como usar, Sair
2. Centro `#appContent`: página ativa (índices 0–6; `PAGE_HELP = 6`)
3. Direita `#appRail`: Dados; em Combate o `#mapPanel` acima dos dados

Ações de página ficam no miolo ou no `sidePanel` da própria página. Não ir para FERRAMENTAS nem para menu de topo.

## Paleta

Modo claro em `src/gestor_rpg/ui/styles.py`: canvas `#E8EEF4`, superfície `#F5F8FC`, tinta `#1B2838`, laterais `#243044`, aço `#3D6FA3`. Nunca neon amarelo/preto.

## Plugins

`hp_paths`, `format_monster_preview`, `format_sheet_html`, `monster_catalog` / `generate_monster`. Backup JSON `gestor-rpg-campaign-v1`. PDF da campanha via `format_campaign_html` + `write_sheet_pdf` (import lazy em Campanhas para evitar ciclo).
