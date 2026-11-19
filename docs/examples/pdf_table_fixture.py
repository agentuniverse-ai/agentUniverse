"""Generate a deterministic ruled-table PDF for integration/visual checks.

Requires reportlab (test/example dependency only). Never overwrites an existing file.
"""
from pathlib import Path

from reportlab.pdfgen import canvas


def make_fixture(path, *, second_caption="Table 1 (continued)",
                 second_header=("Item", "Value"), second_x=50,
                 second_top=720, first_top=170, blank_page=False):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=(612, 792), invariant=1)

    def table(caption, header, rows, x, top):
        pdf.setFont("Helvetica", 10)
        pdf.drawString(x, top + 20, caption)
        values = [header, *rows]
        for row in range(len(values) + 1):
            pdf.line(x, top - row * 24, x + 440, top - row * 24)
        for column in range(3):
            pdf.line(x + column * 220, top, x + column * 220, top - len(values) * 24)
        for row, cells in enumerate(values):
            for column, text in enumerate(cells):
                pdf.drawString(x + column * 220 + 6, top - row * 24 - 16, text)

    pdf.setFont("Helvetica", 14)
    pdf.drawString(50, 750, "Cross-page ruled-table test fixture")
    table("Table 1: Operating limits", ("Item", "Value"),
          [("alpha", "12"), ("beta", "15"), ("gamma", "16")], 50, first_top)
    pdf.showPage()
    if blank_page:
        pdf.drawString(50, 750, "Intervening page - no table")
        pdf.showPage()
    table(second_caption, second_header, [("delta", "18"), ("epsilon", "20")], second_x, second_top)
    pdf.showPage()
    pdf.save()
    return path


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output")
    make_fixture(parser.parse_args().output)
