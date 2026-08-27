# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versão do aplicativo (semver). O schema SQLite desta linha é **v7**.

## [1.1.0] — 2026-08-27

A mesa passa a servir o caderno do mestre: mundo, pessoas e lutas com situação, sem sair do recorte Victory + 5e.

### Adicionado

- Grupo **MUNDO** na navegação: páginas **Locais** (cidades, vilas, tavernas, regiões, masmorras) e **Pessoas** (elenco com papel, local, atitude, aparência, notas e segredos).
- Schema **v7**: tabelas `locations` e `people`; luta com `location_id`, `notes` e `status` (preparada / em andamento / encerrada); notas de sessão com ganchos da próxima.
- Combate: nome, local, situação e notas da luta; combo mostra a situação; iniciativa ou próximo turno inicia a luta.
- Sessão: campo **Próxima sessão** para ganchos e fios soltos.
- Backup JSON e PDF da campanha incluem locais, pessoas, situação das lutas e ganchos.
- CI no GitHub Actions (`pytest` em pull request e em `main`).
- Empacote de release para **Linux** (AppImage + tar.gz), **Windows** (zip com `GestorRPG.exe`) e **macOS** (zip com `Gestor RPG.app`), gerado ao publicar a tag `v1.1.0`.

### Alterado

- Navegação: MESA / MUNDO / PREPARAR / JOGAR. Abrir campanha vai para Locais.
- Página Combate fala em **luta** (Nova luta, Excluir luta); a mesa escolhe a luta em andamento ao abrir Combate.
- Página Sessão vira o caderno da partida (notas + XP + tesouro + próxima sessão).
- Como usar cobre Locais, Pessoas e o fluxo de preparar/rodar lutas.
- Versão do aplicativo passa de 1.0.0 para **1.1.0**.

## [1.0.0] — 2026-08-26

Primeira versão estável. Fecha o recorte de mesa local (Victory + 5e) com janela organizada, ajuda e empacote.

### Adicionado

- Página **Como usar** no rodapé da barra esquerda (índice + cards de todas as funções).
- Exportar campanha em **PDF** na página Campanhas (mesa, elenco, fichas, combates, sessão, títulos dos manuais).
- Navegação agrupada: **MESA** (Campanhas), **PREPARAR** (Fichas, Documentos, Monstros), **JOGAR** (Combate, Sessão).
- **Ajustar zoom** no mapa de combate; combo de encontro com setas visíveis.
- Estados vazios nas listas (`emptyHint`).
- Histórico de dados clicável para rerrolar; detalhe da rolagem no rail.
- Empacote 1.0: AppImage / pasta congelada / RPM com versão alinhada ao app.

### Alterado

- **Sair** sai de FERRAMENTAS e vira botão de rodapé; ferramentas ficam NPC rápido, Gerador de nomes e Importar PDF.
- Ficha do combatente compacta (pools em uma linha); iniciativa usa rótulos do plugin; PV 0 mudo e riscado.
- Títulos de página iguais: título fixo + subtítulo `Nome · sistema`.
- Um botão primário por bloco; botões com altura/largura mínimas para o rótulo caber.
- Textos da UI sem 3D&T Alpha, Tormenta20 ou sistemas fora do recorte.
- Versão do aplicativo passa de 0.1.0 para **1.0.0** (schema continua v6).

### Empacote

- `packaging/build-appimage.sh` e `packaging/build-rpm.sh` geram o binário 1.0.0.

## [0.1.0] — 2026-08-25

Primeira entrega usável: recorte de mesa completo.

### Sistemas

- O app fica com **3D&T Victory** e **D&D 5e**. 3D&T Alpha e Tormenta20 saem do registry, da ficha e do gerador de nomes. Schema **v6** remove esses sistemas do banco (e campanhas ligadas a eles).

### Grid de combate e empacote

- Combate ganha um grid simples (12×8, redimensionável) com tokens arrastáveis; posição gravada no encontro (`schema v5`). Sem paredes nem editor de dungeon.
- AppImage e RPM a partir do binário congelado: `packaging/build-appimage.sh` e `packaging/build-rpm.sh`.

### Catálogo D&D 5e

- Página Monstros usa o compêndio local: 100 criaturas da tabela mestra (tipo, ND, XP, habitat) mais fichas detalhadas (Aarakocra, Veterano, Orog, etc.).
- Filtros da campanha 5e: Tipo e Habitat. Stats oficiais só onde o anexo traz CA/PV/atributos; as demais entradas estimam HP/CA por ND.

### Ficha em PDF

- Exportar e imprimir a ficha preenchida a partir do JSON do sistema (`format_sheet_html` + `QPdfWriter`), na página Fichas.
- Layout original no recorte de cada plugin (Victory e 5e); não preenche PDF oficial.

### Sessão e busca em fichas

- Schema v4: tabela `session_entries` (log da mesa com XP/tesouro e encontro opcional) e FTS5 em fichas (`characters_fts`).
- Página **Sessão** na navegação: nova entrada, salvar, excluir; vínculo opcional com encontro.
- Busca nas fichas por nome, notas e JSON de atributos (vantagem, magia, classe).
- Export/import da campanha inclui o log de sessão (arquivos antigos sem a chave continuam válidos).

### Recorte de mesa

- Combate Victory com pool de **PA** (`action_current` / `action_max`, schema v3). Ficha Victory no recorte oficial: **P, H, R** (sem Armadura nem PdF).
- Histórico de encontros na página Combate: combo, novo combate e excluir encontro.
- Documentos: excluir e abrir o PDF original (`QDesktopServices`); aviso se o arquivo não existir.
- Fichas: `validate_attributes` no botão Salvar (com diálogo de erro); auto-save silencioso não bloqueia.
- Preview de monstro por plugin (`format_monster_preview`): 3D&T Victory (P/H/R/PV) e D&D 5e (CA, HP, atributos).
- Exportar e importar campanha em JSON `gestor-rpg-campaign-v1` (campanha, fichas, encontros, documentos; ids novos na importação).

### Fase mesa

- Schema v2: `kind` monster, FTS5 em documentos, tabelas `encounters` e `combatants`.
- Plugins com `hp_paths`, `generate_monster`, `initiative_bonus` e `monster_catalog`.
- Página Monstros e tracker de combate (iniciativa, PV, recurso).
- Catálogo Victory com 47 desafios oficiais (`_ddt_bestiary.py`); desafios sem PM/PA, PV da ficha.

### Visual e layout

- Paleta clara azul (papel `#E8EEF4`, tinta `#1B2838`, ardósia `#243044`, aço `#3D6FA3`).
- Janela em três colunas; menu de topo e dock de dados removidos.
- Navegação: Campanhas, Fichas, Documentos, Monstros, Combate, Sessão.
- Ferramentas: Importar PDF, NPC rápido, gerador de nomes, Sair.

### MVP

- Scaffold PySide6 + SQLite, plugins por sistema, fichas, importação de PDF, dados, NPC rápido e gerador de nomes.
