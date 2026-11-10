"""Genera el PDF académico desde Markdown y capturas reales opcionales."""

from datetime import datetime
import json
from pathlib import Path
import re
import textwrap
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/entrega-1"


def latest_docker_run():
    for directory in sorted(
        (DIRECTORY / "evidencias/ejecuciones").glob("*"), reverse=True
    ):
        result = directory / "resultado.json"
        if result.exists():
            report = json.loads(result.read_text(encoding="utf-8"))
            if report.get("status") == "passed":
                return directory
    return None


def latest_github_run():
    for path in sorted(
        (DIRECTORY / "evidencias/github-actions").glob("*/github-run.json"),
        reverse=True,
    ):
        report = json.loads(path.read_text(encoding="utf-8"))
        if (
            report.get("status") == "completed"
            and report.get("conclusion") == "success"
        ):
            return path.parent, report
    return None


def docker_diagram(font):
    drawing = Drawing(500, 195)
    drawing.add(
        Rect(
            8,
            23,
            484,
            140,
            rx=10,
            strokeColor=colors.HexColor("#52786a"),
            fillColor=colors.HexColor("#f4f8f5"),
        )
    )
    drawing.add(String(22, 144, "jg-network · bridge", fontName=font, fontSize=11))
    for x, title, detail in [
        (30, "api · FastAPI", "UID 10001 · puerto 8000"),
        (302, "db · PostgreSQL", "5432 interno · sin puerto host"),
    ]:
        drawing.add(
            Rect(
                x,
                81,
                165,
                45,
                rx=5,
                fillColor=colors.white,
                strokeColor=colors.HexColor("#52786a"),
            )
        )
        drawing.add(String(x + 12, 107, title, fontName=font, fontSize=11))
        drawing.add(String(x + 12, 91, detail, fontName=font, fontSize=8))
    drawing.add(Line(195, 101, 301, 101, strokeColor=colors.HexColor("#244c39")))
    drawing.add(
        Polygon([301, 101, 293, 105, 293, 97], fillColor=colors.HexColor("#244c39"))
    )
    drawing.add(String(205, 111, "db:5432", fontName=font, fontSize=9))
    drawing.add(
        String(
            30,
            180,
            "Host: React / Swagger → 127.0.0.1:8000",
            fontName=font,
            fontSize=10,
        )
    )
    drawing.add(Line(110, 174, 110, 127))
    drawing.add(
        Rect(
            302,
            34,
            165,
            29,
            rx=5,
            fillColor=colors.HexColor("#e4eee5"),
            strokeColor=colors.HexColor("#52786a"),
        )
    )
    drawing.add(
        String(313, 45, "postgres_data · persistente", fontName=font, fontSize=9)
    )
    drawing.add(Line(385, 81, 385, 64))
    return drawing


def main():
    docker_run = latest_docker_run()
    github_run = latest_github_run()
    font, bold, mono = "Helvetica", "Helvetica-Bold", "Courier"
    for base in [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")]:
        regular = base / ("arial.ttf" if base.name == "Fonts" else "DejaVuSans.ttf")
        heavy = base / (
            "arialbd.ttf" if base.name == "Fonts" else "DejaVuSans-Bold.ttf"
        )
        if regular.exists() and heavy.exists():
            pdfmetrics.registerFont(TTFont("JG", str(regular)))
            pdfmetrics.registerFont(TTFont("JG-Bold", str(heavy)))
            pdfmetrics.registerFontFamily(
                "JG", normal="JG", bold="JG-Bold", italic="JG", boldItalic="JG-Bold"
            )
            font, bold = "JG", "JG-Bold"
            break
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="JGBody", fontName=font, fontSize=10, leading=15, spaceAfter=9
        )
    )
    styles.add(
        ParagraphStyle(
            name="JGHeading",
            fontName=bold,
            fontSize=14,
            leading=19,
            spaceBefore=15,
            spaceAfter=10,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            name="JGCover",
            fontName=bold,
            fontSize=25,
            leading=32,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#244c39"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="JGSmall", fontName=font, fontSize=8, leading=11, spaceAfter=5
        )
    )
    styles.add(
        ParagraphStyle(
            name="JGCode",
            fontName=mono,
            fontSize=7.2,
            leading=10,
            backColor=colors.HexColor("#f2f4f3"),
            borderPadding=7,
            spaceAfter=12,
        )
    )
    output = DIRECTORY / "JG_Repuestos_Entrega_1_Escenario_3.pdf"
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=43,
        leftMargin=43,
        topMargin=45,
        bottomMargin=43,
        title="JG Repuestos - Entrega 1, Escenario 3",
        author="JG Repuestos",
    )
    story = [
        Spacer(1, 65),
        Paragraph("JG REPUESTOS", styles["JGCover"]),
        Spacer(1, 20),
        Paragraph("Entrega proyecto 1 · Escenario 3", styles["JGHeading"]),
        Paragraph("Docker, Docker Compose y GitHub Actions", styles["JGBody"]),
        Spacer(1, 25),
        Paragraph(
            "Material académico preparado con resultados reales y validaciones pendientes identificadas.",
            styles["JGBody"],
        ),
        Paragraph(
            "Datos de estudiante, institución, asignatura y docente: completar antes de entregar.",
            styles["JGBody"],
        ),
        Paragraph(
            "Fecha límite: 10 de noviembre de 2026 · 23:55 · America/Bogota",
            styles["JGBody"],
        ),
        Paragraph(
            "Estado: Docker y GitHub Actions aprobados; capturas de consola y portada pendientes."
            if github_run
            else "Estado: Docker validado localmente; ejecución remota de GitHub pendiente."
            if docker_run
            else "Estado: pruebas locales aprobadas; Docker y ejecución GitHub pendientes.",
            styles["JGBody"],
        ),
        PageBreak(),
    ]

    def markup(text):
        return escape(text).replace("`", "")

    def paragraph(text):
        return Paragraph(markup(text), styles["JGBody"])

    lines = (DIRECTORY / "informe.md").read_text(encoding="utf-8").splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.startswith("# "):
            index += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), styles["JGHeading"]))
            index += 1
        elif line.startswith("```"):
            language, block = line[3:].strip(), []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            if language == "mermaid":
                story.append(docker_diagram(font))
            else:
                wrapped = "\n".join(
                    "\n".join(
                        textwrap.wrap(
                            value,
                            width=96,
                            replace_whitespace=False,
                            drop_whitespace=False,
                        )
                    )
                    if value
                    else ""
                    for value in block
                )
                story.append(Preformatted(wrapped, styles["JGCode"]))
        elif line.startswith("|"):
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                row = [value.strip() for value in lines[index].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", value) for value in row):
                    rows.append(
                        [Paragraph(markup(value), styles["JGSmall"]) for value in row]
                    )
                index += 1
            table = Table(
                rows,
                colWidths=[210, 299] if len(rows[0]) == 2 else None,
                repeatRows=1,
                hAlign="LEFT",
            )
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e4eee5")),
                        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#ccd8cf")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 7),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                        ("TOPPADDING", (0, 0), (-1, -1), 7),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.extend([table, Spacer(1, 12)])
        else:
            block = [line]
            index += 1
            while (
                index < len(lines)
                and lines[index].strip()
                and not lines[index].startswith(("#", "|", "```"))
            ):
                block.append(lines[index])
                index += 1
            story.append(paragraph(" ".join(block)))

    story.extend(
        [
            PageBreak(),
            Paragraph("Anexo: salida real de Pytest local", styles["JGHeading"]),
        ]
    )
    result = DIRECTORY / "evidencias/pytest-local.txt"
    if result.exists():
        value = result.read_text(encoding="utf-8")
        summary = "\n".join(value.splitlines()[:2] + value.splitlines()[-4:])
        story.append(Preformatted(summary, styles["JGCode"]))
    else:
        story.append(paragraph("Pendiente de incorporar salida real de Pytest."))
    if docker_run:
        story.extend(
            [
                PageBreak(),
                Paragraph("Anexo: ejecuciones reales Docker", styles["JGHeading"]),
                paragraph(
                    f"Ejecución: {docker_run.name}. Los bloques siguientes son extractos de salidas originales saneadas; los archivos completos están en evidencias/ejecuciones/{docker_run.name}/."
                ),
            ]
        )
        for filename, title, limit in [
            ("05-docker-build.txt", "Construcción de la imagen", 20),
            ("07-compose-up.txt", "Arranque y salud de los servicios", 24),
            ("08-compose-ps.txt", "Dos servicios y puertos", 15),
            ("10-network-inspect.txt", "Inspección de jg-network", 85),
            ("11-api-user.txt", "Usuario no privilegiado", 8),
            ("12-alembic-current.txt", "Revisión Alembic", 10),
            ("13-alembic-check.txt", "Correspondencia entre esquema y modelos", 14),
            ("14-escritura-lectura-limpieza.txt", "Escritura, lectura y limpieza", 10),
            ("15-persistencia-crear.txt", "Crear registro para persistencia", 8),
            ("16-recrear-down.txt", "Recrear sin eliminar el volumen: parada", 14),
            ("17-recrear-up.txt", "Recrear sin eliminar el volumen: arranque", 20),
            ("18-persistencia-leer.txt", "Mismo UUID recuperado", 10),
            ("19-persistencia-limpiar.txt", "Limpieza del registro temporal", 8),
            ("22-pytest.txt", "Pytest dentro de api con PostgreSQL db", 18),
            ("28-final-compose-ps.txt", "Estado final tras restaurar runtime", 12),
        ]:
            path = docker_run / filename
            if not path.exists():
                continue
            source = path.read_text(encoding="utf-8").splitlines()
            if len(source) > limit:
                source = (
                    source[:1]
                    + ["[Extracto: se omiten líneas intermedias; ver archivo original]"]
                    + source[-limit:]
                )
            text = "\n".join(
                "\n".join(
                    textwrap.wrap(
                        line, 96, replace_whitespace=False, drop_whitespace=False
                    )
                )
                if line
                else ""
                for line in source
            )
            story.append(Paragraph(markup(title), styles["JGHeading"]))
            story.append(Preformatted(text, styles["JGCode"]))
    if github_run:
        directory, report = github_run
        story.extend(
            [
                PageBreak(),
                Paragraph("Anexo: GitHub Actions remoto aprobado", styles["JGHeading"]),
                paragraph(
                    "Fuente: GitHub REST API autenticada y artefactos originales de la ejecución. Esto corresponde a una ejecución real por push, distinta de la prueba Docker local."
                ),
                Paragraph(
                    f'<link href="{escape(report["url"])}" color="blue">{escape(report["url"])}</link>',
                    styles["JGBody"],
                ),
                paragraph(
                    f"Commit validado: {report['head_sha']} · Resultado: {report['conclusion']}."
                ),
            ]
        )
        completed = datetime.fromisoformat(
            report["updated_at"].replace("Z", "+00:00")
        ).astimezone(ZoneInfo("America/Bogota"))
        story.append(
            paragraph(
                f"Verificación de cierre: {completed.strftime('%Y-%m-%d %H:%M %z')} (America/Bogota)."
            )
        )
        for job in report["jobs"]:
            story.append(paragraph(f"Trabajo {job['name']}: {job['conclusion']}."))
        result_path = directory / "22-pytest.txt"
        if result_path.exists():
            source = result_path.read_text(encoding="utf-8").splitlines()
            excerpt = "\n".join(source[:2] + source[-4:])
            story.append(Preformatted(excerpt, styles["JGCode"]))
        story.append(
            paragraph(
                f"Los logs completos, resultados de comunicación/persistencia y metadatos están en evidencias/github-actions/{directory.name}/. La captura de la interfaz web de Actions queda por incorporar."
            )
        )
    screenshots = sorted((DIRECTORY / "capturas").glob("*.png"))
    if screenshots:
        for file in screenshots:
            story.extend(
                [PageBreak(), Paragraph(markup(file.name), styles["JGHeading"])]
            )
            width, height = ImageReader(str(file)).getSize()
            ratio = min(500 / width, 650 / height)
            story.append(Image(str(file), width=width * ratio, height=height * ratio))
    else:
        story.append(
            paragraph(
                "No hay capturas Docker/Actions incorporadas. Consulte la lista de capturas pendientes; no se sustituyen por imágenes generadas."
            )
        )

    generated = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M %z")

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont(font, 8)
        canvas.setFillColor(colors.HexColor("#607367"))
        canvas.drawString(43, 25, f"JG Repuestos · Generado {generated}")
        canvas.drawRightString(A4[0] - 43, 25, str(document.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"PDF generado: {output}")


if __name__ == "__main__":
    main()
