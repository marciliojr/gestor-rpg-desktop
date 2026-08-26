from __future__ import annotations

from pathlib import Path

from gestor_rpg.modules.pdf_import.extractor import extract_pdf


def test_extract_text_pdf(tmp_path: Path):
    import fitz

    path = tmp_path / "ficha.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (72, 72),
        "Nome: Aldric\nForça: 2\nHabilidade: 1\nResistência: 2\nArmadura: 1\nPdF: 0",
    )
    doc.save(path)
    doc.close()

    extracted = extract_pdf(path)
    assert extracted.used_ocr is False
    assert "Força" in extracted.full_text or "Forca" in extracted.full_text or "Aldric" in extracted.full_text
    assert len(extracted.page_texts) == 1
