# Gestor RPG

Aplicativo desktop **1.1** para mestrar RPG neste computador: campanhas, mundo (cidades e pessoas), fichas, documentos, monstros, combate com mapa simples e notas de sessão. Sistemas: **3D&T Victory** e **D&D 5e**. Sem conta, nuvem ou sincronização.

Site: [marciliojr.github.io/gestor-rpg-desktop](https://marciliojr.github.io/gestor-rpg-desktop/).

## Sistemas

- **3D&T Victory** — ficha P, H, R + PV/PM/PA (sem Armadura nem PdF); catálogo de 47 desafios; combate com PV, PM e PA
- **D&D 5e** — ficha no recorte do plugin; catálogo com 100 criaturas da tabela mestra + fichas detalhadas do compêndio local

O sistema da campanha não muda depois de salvar.

## Recorte 1.1

- **Campanhas:** criar, editar, excluir; exportar/importar JSON `gestor-rpg-campaign-v1`; exportar PDF da mesa (mundo, elenco, fichas, combates, sessão, títulos dos manuais)
- **Locais:** cidades, vilas, regiões, tavernas e masmorras da campanha (descrição + segredos do mestre). Sem editor de dungeon com paredes
- **Pessoas:** elenco do mundo (papel, local, atitude, aparência, notas, segredos); ficha de combate opcional. Diferente de NPC rápido (gerador) e da lista Fichas (stats)
- **Fichas:** PC/NPC; busca FTS; Salvar valida atributos (auto-save não bloqueia); exportar e imprimir PDF da ficha preenchida (layout original, não preenche ficha oficial)
- **Documentos:** importar PDF (texto + OCR quando preciso), busca FTS, excluir, abrir o arquivo original
- **Monstros:** catálogo do sistema ativo; gerar e usar no combate; preview por plugin
- **Combate:** preparar e rodar lutas (situação, local, notas); iniciativa, PV e recursos; PA no Victory; histórico; grid de tokens no painel direito (sem paredes/dungeon)
- **Sessão:** notas da partida (XP, tesouro, ganchos da próxima), opcionalmente ligadas a uma luta
- **Como usar:** ajuda no rodapé da barra esquerda, com todas as funções da mesa

Não entram neste recorte: dungeon com paredes, sync, 3D&T Alpha e Tormenta20.

## Interface

Três colunas fixas, sem barra de menus no topo:

1. **Esquerda** — marca, campanha, grupos **MESA** (Campanhas), **MUNDO** (Locais, Pessoas), **PREPARAR** (Fichas, Documentos, Monstros), **JOGAR** (Combate, Sessão), **FERRAMENTAS** (NPC rápido, Gerador de nomes, Importar PDF), **Como usar** e **Sair**
2. **Centro** — página ativa
3. **Direita** — dados; na página Combate o mapa fica acima dos dados

Modo claro permanente (papel frio, ardósia azul, aço). Paleta em `src/gestor_rpg/ui/styles.py`.

## Requisitos

- Python 3.12+
- PySide6, PyMuPDF, pytesseract, Pillow
- Tesseract no sistema se quiser OCR em PDF escaneado

## Como rodar (desenvolvimento)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python3 -m gestor_rpg
```

O banco SQLite fica em `GESTOR_RPG_DATA` (se definida) ou no diretório de dados do aplicativo (`gestor.db`). Schema atual: **v7**.

## Executável

A [release v1.1.0](https://github.com/marciliojr/gestor-rpg-desktop/releases/tag/v1.1.0) traz o binário de cada sistema:

- **Linux:** `GestorRPG-1.1.0-linux-x64.AppImage` (marque como executável) ou o `.tar.gz`
- **Windows:** zip com `GestorRPG.exe`
- **macOS:** zip com `Gestor RPG.app`

A [release v1.0.0](https://github.com/marciliojr/gestor-rpg-desktop/releases/tag/v1.0.0) permanece só com o AppImage Linux.

OCR em PDF escaneado continua pedindo Tesseract instalado no sistema.

Para gerar de novo no Linux (PyInstaller; AppImage se `appimagetool` estiver no PATH):

```bash
pip install -e ".[packaging]"
./packaging/build-appimage.sh
```

Nas três plataformas, o mesmo empacote da release:

```bash
pip install -e ".[packaging]"
GESTOR_RPG_VERSION=1.1.0 python packaging/package-release.py
```

- AppImage: `dist/GestorRPG.AppImage` (marque como executável e dê dois cliques, ou `./dist/GestorRPG.AppImage`)
- Pasta congelada Linux: `dist/gestor-rpg/gestor-rpg`
- RPM (Fedora): `./packaging/build-rpm.sh` — instala em `/opt/gestor-rpg` e cria o atalho `gestor-rpg`
- Artefatos de release: `dist/upload/`

O GitHub Actions (`Release`) gera os três binários quando a tag `v*` é publicada.

## Testes

```bash
python3 -m pytest -q
```

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md).
