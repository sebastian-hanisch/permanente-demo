"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Ergebnis (Permanente, Determinante, Kosten), die Matrix. Kein Gedankenstrich und kein Euro-Zeichen (Kernschriften)."""

from fpdf import FPDF

import prn_constants as C
import prn_evaluation as ev


def _text(value: str) -> str:
    """Zeichen, die die Kernschriften nicht kennen, ersetzen (Gedankenstrich, Pfeile, Fettdruck-Markierung, mathematische Zeichen)."""
    table = {"–": "-", "—": "-", "→": "->", "**": "", "€": "EUR", "·": "*", "³": "^3", "≤": "<=", "≥": ">=", "−": "-", "×": "x", "„": '"', "“": '"', "⇔": "<=>", "²": "^2", "√": "sqrt", "≡": "=="}
    for old, new in table.items():
        value = value.replace(old, new)
    return value


def _para(pdf: FPDF, height: float, text: str) -> None:
    """Absatz über die volle Breite; danach steht der Cursor wieder am linken Rand (fpdf2 setzt ihn sonst an den rechten Rand)."""
    pdf.multi_cell(0, height, _text(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(a: ev.Analysis) -> bytes:
    s = a.settings
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _text("Zählen: Permanente gegen Determinante"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    dens = f"   Dichte: {s.dens} %" if s.kind == "random" else ""
    _para(pdf, 5.5, f"Matrix: {len(a.matrix)} x {len(a.matrix)}   Art: {C.KINDS[s.kind]}{dens}   Zufalls-Seed: {s.seed}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Ergebnis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, ev.verdict_main(a)[1])
    if a.estimate is not None:
        e = a.estimate
        _para(pdf, 5.5, f"Schätzer (Godsil-Gutman, {ev.fmt_int(e.samples)} Vorzeichenmatrizen, Illustration): {ev.fmt_fraction(e.mean)} gegen die Permanente {ev.fmt_int(a.per)}.")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Matrix", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Courier", "", 8)
    for row in a.matrix:
        _para(pdf, 4.2, " ".join(str(x) for x in row))
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    _para(pdf, 4.5, "Aufwand in Multiplikationen, nicht in Sekunden. Sebastian Hanisch - Operations Research und Machine Learning.")
    return bytes(pdf.output())
