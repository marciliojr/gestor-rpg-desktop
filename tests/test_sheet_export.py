from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import fitz
from PySide6.QtWidgets import QApplication

from gestor_rpg.core.registry import PluginRegistry
from gestor_rpg.modules.sheet_export.html import format_campaign_html
from gestor_rpg.modules.sheet_export.pdf import write_sheet_pdf


def test_write_sheet_pdf_contains_name(tmp_path):
    app = QApplication.instance() or QApplication([])
    plugin = PluginRegistry().get("ddt_victory")
    html = plugin.format_sheet_html(
        {
            "name": "Mira Ventania",
            "kind": "pc",
            "notes": "Nota de teste",
            "attributes": plugin.default_attributes(),
            "system_name": plugin.display_name,
        }
    )
    path = tmp_path / "mira.pdf"
    write_sheet_pdf(html, path)
    assert path.exists()
    assert path.stat().st_size > 100
    document = fitz.open(path)
    text = "\n".join(page.get_text() for page in document)
    document.close()
    assert "Mira Ventania" in text
    app.processEvents()


def test_write_campaign_pdf_contains_roster(tmp_path):
    app = QApplication.instance() or QApplication([])
    from gestor_rpg.modules.sheet_export.html import format_campaign_html
    from gestor_rpg.modules.sheet_export.pdf import write_sheet_pdf

    plugin = PluginRegistry().get("ddt_victory")
    html = format_campaign_html(
        {
            "campaign": {
                "name": "A Torre Quebrada",
                "system_slug": "ddt_victory",
                "notes": "Notas da mesa",
            },
            "characters": [
                {
                    "kind": "pc",
                    "name": "Kael",
                    "motivation": "Proteger o reino",
                    "story_hook": "A carta selada",
                    "notes": "",
                    "attributes": plugin.default_attributes(),
                }
            ],
            "encounters": [
                {
                    "name": "Emboscada",
                    "round": 2,
                    "grid_cols": 12,
                    "grid_rows": 8,
                    "combatants": [
                        {
                            "name": "Kael",
                            "initiative": 14,
                            "hp_current": 12,
                            "hp_max": 20,
                        }
                    ],
                }
            ],
            "session_entries": [
                {
                    "title": "Sessão 1",
                    "body": "Os heróis chegaram à torre.",
                    "xp": "300",
                    "treasure": "2 PO",
                    "hooks": "A carta selada",
                }
            ],
            "locations": [
                {
                    "uuid": "loc-1",
                    "name": "Porto Seguro",
                    "kind": "cidade",
                    "notes": "Porto comercial",
                }
            ],
            "people": [
                {
                    "name": "Mara",
                    "role": "Estalajadeira",
                    "attitude": "aliado",
                    "location_uuid": "loc-1",
                }
            ],
            "documents": [{"doc_type": "manual", "title": "Livro básico"}],
        },
        plugin,
    )
    path = tmp_path / "torre.pdf"
    write_sheet_pdf(html, path, title="A Torre Quebrada")
    assert path.exists()
    document = fitz.open(path)
    text = "\n".join(page.get_text() for page in document)
    document.close()
    assert "A Torre Quebrada" in text
    assert "Kael" in text
    assert "Emboscada" in text
    assert "Sessão 1" in text
    assert "Porto Seguro" in text
    assert "Mara" in text
    app.processEvents()
