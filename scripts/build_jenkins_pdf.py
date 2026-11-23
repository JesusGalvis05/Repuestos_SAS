"""Exporta el informe de Entrega 2 e incorpora las capturas reales existentes.

Dependencias opcionales: scripts/requirements-evidence.lock.
La portada se completa en docs/entrega-2/informe.md antes de la entrega.
"""

import re
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/entrega-2"


def inline(text):
    text = escape(text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)", r'<link href="\2" color="#174ea6">\1</link>', text
    )
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)


def diagram():
    drawing = Drawing(490, 200)
    boxes = [
        (170, 160, "GitHub: JG Repuestos"),
        (45, 105, "Jenkins local"),
        (295, 105, "GitHub Actions"),
        (170, 45, "Pruebas > imagen > humo"),
    ]
    for x, y, label in boxes:
        drawing.add(Rect(x, y, 155, 30, rx=4, fillColor=colors.HexColor("#edf4fc")))
        drawing.add(String(x + 8, y + 11, label, fontName="Helvetica", fontSize=9))
    for start, end in [
        ((200, 160), (122, 135)),
        ((290, 160), (372, 135)),
        ((122, 105), (215, 75)),
        ((372, 105), (280, 75)),
    ]:
        drawing.add(Line(*start, *end))
    drawing.add(
        String(
            80,
            18,
            "PostgreSQL temporal por ejecucion; limpieza incluso si falla Pytest",
            fontSize=9,
        )
    )
    return drawing


def main():
    font, bold = "Helvetica", "Helvetica-Bold"
    for base, regular, heavy in [
        (Path("C:/Windows/Fonts"), "arial.ttf", "arialbd.ttf"),
        (
            Path("/usr/share/fonts/truetype/dejavu"),
            "DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf",
        ),
    ]:
        if (base / regular).exists() and (base / heavy).exists():
            pdfmetrics.registerFont(TTFont("JG2", str(base / regular)))
            pdfmetrics.registerFont(TTFont("JG2Bold", str(base / heavy)))
            pdfmetrics.registerFontFamily(
                "JG2", normal="JG2", bold="JG2Bold", italic="JG2", boldItalic="JG2Bold"
            )
            font, bold = "JG2", "JG2Bold"
            break
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle("Body2", fontName=font, fontSize=10, leading=15, spaceAfter=8)
    )
    styles.add(
        ParagraphStyle(
            "Head2",
            fontName=bold,
            fontSize=14,
            leading=18,
            spaceBefore=12,
            spaceAfter=8,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle("Title2", fontName=bold, fontSize=19, leading=24, spaceAfter=16)
    )
    styles.add(ParagraphStyle("Cell2", fontName=font, fontSize=8, leading=11))
    output = DIRECTORY / "JG_Repuestos_Entrega_2_Jenkins.pdf"
    document = BaseDocTemplate(
        str(output),
        title="JG Repuestos - Entrega 2 - Jenkins",
        author="JG Repuestos",
        leftMargin=45,
        rightMargin=45,
    )

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            45, 23, "JG Repuestos | Entrega 2 | Evidencias de ejecuciones reales"
        )
        canvas.drawRightString(canvas._pagesize[0] - 45, 23, str(doc.page))

    portrait = PageTemplate(
        "portrait", [Frame(45, 40, A4[0] - 90, A4[1] - 85)], pagesize=A4, onPage=footer
    )
    wide = landscape(A4)
    screenshots = PageTemplate(
        "screenshots",
        [Frame(35, 35, wide[0] - 70, wide[1] - 70)],
        pagesize=wide,
        onPage=footer,
    )
    document.addPageTemplates([portrait, screenshots])
    story = []
    lines = (DIRECTORY / "informe.md").read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("```"):
            language = line.removeprefix("```")
            block = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            story.append(
                diagram()
                if language == "mermaid"
                else Preformatted("\n".join(block), styles["Code"])
            )
        elif line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [
                    cell.strip() for cell in lines[index].strip().strip("|").split("|")
                ]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(
                        [Paragraph(inline(cell), styles["Cell2"]) for cell in cells]
                    )
                index += 1
            table = Table(
                rows,
                colWidths=[(A4[0] - 102) / len(rows[0])] * len(rows[0]),
                repeatRows=1,
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3edf8")),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b5c2d0")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.extend([table, Spacer(1, 10)])
            continue
        elif line.startswith("# "):
            story.append(Paragraph(inline(line[2:]), styles["Title2"]))
        elif line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), styles["Head2"]))
        else:
            paragraph = [line]
            while (
                index + 1 < len(lines)
                and lines[index + 1].strip()
                and not lines[index + 1].startswith(("#", "|", "```", "- "))
            ):
                index += 1
                paragraph.append(lines[index].strip())
            story.append(Paragraph(inline(" ".join(paragraph)), styles["Body2"]))
        index += 1
    story.extend([NextPageTemplate("screenshots"), PageBreak()])
    images = sorted((DIRECTORY / "capturas").glob("[0-9][0-9]-*.png"))
    assert len(images) == 10, "Se requieren las diez capturas reales de la entrega"
    for index, path in enumerate(images):
        metadata = path.with_suffix(".json")
        assert metadata.exists(), f"Faltan metadatos de captura: {path.name}"
        width, height = ImageReader(str(path)).getSize()
        ratio = min((wide[0] - 90) / width, (wide[1] - 135) / height)
        story.append(Paragraph(escape(path.stem.replace("-", " ")), styles["Head2"]))
        story.append(Image(str(path), width=width * ratio, height=height * ratio))
        if index < len(images) - 1:
            story.append(PageBreak())
    document.build(story)
    print(output)


if __name__ == "__main__":
    main()
