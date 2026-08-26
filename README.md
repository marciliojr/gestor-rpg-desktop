# Gestor RPG

Aplicativo desktop **1.0** para mestrar RPG neste computador: campanhas, fichas, documentos, monstros, combate com mapa simples e log de sessão. Sistemas: **3D&T Victory** e **D&D 5e**. Sem conta, nuvem ou sincronização.

## Sistemas

- **3D&T Victory** — ficha P, H, R + PV/PM/PA (sem Armadura nem PdF); catálogo de 47 desafios; combate com PV, PM e PA
- **D&D 5e** — ficha no recorte do plugin; catálogo com 100 criaturas da tabela mestra + fichas detalhadas do compêndio local

O sistema da campanha não muda depois de salvar.

## Recorte 1.0

- **Campanhas:** criar, editar, excluir; exportar/importar JSON `gestor-rpg-campaign-v1`; exportar PDF da mesa (elenco, fichas, combates, sessão, títulos dos manuais)
- **Fichas:** PC/NPC; busca FTS; Salvar valida atributos (auto-save não bloqueia); exportar e imprimir PDF da ficha preenchida (layout original, não preenche ficha oficial)
- **Documentos:** importar PDF (texto + OCR quando preciso), busca FTS, excluir, abrir o arquivo original
- **Monstros:** catálogo do sistema ativo; gerar e usar no combate; preview por plugin
- **Combate:** iniciativa, PV e recursos; PA no Victory; histórico de encontros; grid de tokens no painel direito (sem paredes/dungeon)
- **Sessão:** log da mesa (XP, tesouro), opcionalmente ligado a um encontro
- **Como usar:** ajuda no rodapé da barra esquerda, com todas as funções da mesa

Não entram neste recorte: dungeon com paredes, sync, 3D&T Alpha e Tormenta20.

## Interface

Três colunas fixas, sem barra de menus no topo:

1. **Esquerda** — marca, campanha, grupos **MESA** (Campanhas), **PREPARAR** (Fichas, Documentos, Monstros), **JOGAR** (Combate, Sessão), **FERRAMENTAS** (NPC rápido, Gerador de nomes, Importar PDF), **Como usar** e **Sair**
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

O banco SQLite fica em `GESTOR_RPG_DATA` (se definida) ou no diretório de dados do aplicativo (`gestor.db`). Schema atual: **v6**.

## Executável

No Linux, o empacote gera um binário congelado (PyInstaller) e, se `appimagetool` estiver no PATH, o AppImage:

```bash
pip install -e ".[packaging]"
./packaging/build-appimage.sh
```

- AppImage: `dist/GestorRPG.AppImage` (marque como executável e dê dois cliques, ou `./dist/GestorRPG.AppImage`)
- Pasta congelada: `dist/gestor-rpg/gestor-rpg`
- RPM (Fedora): `./packaging/build-rpm.sh` — instala em `/opt/gestor-rpg` e cria o atalho `gestor-rpg`

## Testes

```bash
python3 -m pytest -q
```

## Changelog

Ver [CHANGELOG.md](CHANGELOG.md).
