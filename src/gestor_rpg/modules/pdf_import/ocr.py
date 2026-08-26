from __future__ import annotations

import io


def ocr_page(page) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        return ""

    pixmap = page.get_pixmap(dpi=200)
    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
    try:
        return pytesseract.image_to_string(image, lang="por+eng")
    except Exception:
        try:
            return pytesseract.image_to_string(image)
        except Exception:
            return ""
