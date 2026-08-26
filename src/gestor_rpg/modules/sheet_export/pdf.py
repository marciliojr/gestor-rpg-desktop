from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QPdfWriter, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QDialog, QWidget


def write_sheet_pdf(html: str, path: str | Path, title: str = "Ficha") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    writer = QPdfWriter(str(target))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(12, 12, 12, 12), QPageLayout.Unit.Millimeter)
    writer.setTitle(title)
    document = QTextDocument()
    document.setHtml(html)
    document.print_(writer)


def print_sheet(html: str, parent: QWidget | None = None) -> bool:
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    dialog = QPrintDialog(printer, parent)
    dialog.setWindowTitle("Imprimir ficha")
    if dialog.exec() != QDialog.DialogCode.Accepted:
        return False
    document = QTextDocument()
    document.setHtml(html)
    document.print_(printer)
    return True
