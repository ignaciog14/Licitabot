"""Generación del PDF de cotización con ReportLab.

Se elige ReportLab por sobre WeasyPrint porque es pure-Python y no depende
de cairo/pango/glib del sistema — fundamental para correr en Windows local
y en Railway sin imágenes Docker custom.
"""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

TALINAY_RAZON_SOCIAL = "Industrial y Comercial Talinay Ltda."
TALINAY_DIRECCION = "Iquique 3423, Estación Central, Santiago"
TALINAY_WEB = "talinay.cl"
TALINAY_EMAIL = "talinay@talinay.cl"

COLOR_TALINAY = colors.HexColor("#1e3a8a")
COLOR_SUBTEXTO = colors.HexColor("#555555")
COLOR_PIE = colors.HexColor("#666666")


def generar_pdf_cotizacion(cotizacion: dict, oportunidad: dict) -> bytes:
    """Devuelve el PDF (bytes) de una cotización aprobada."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        title=f"Cotización Talinay — {oportunidad.get('codigo', '')}",
        author=TALINAY_RAZON_SOCIAL,
    )

    estilos = _construir_estilos()
    elementos: list = []

    _agregar_encabezado(elementos, estilos)
    _agregar_titulo(elementos, estilos)
    _agregar_referencia(elementos, estilos, oportunidad)
    _agregar_cuerpo(elementos, estilos, cotizacion)
    _agregar_condiciones(elementos, estilos, cotizacion)
    _agregar_pie(elementos, estilos)

    doc.build(elementos)
    return buffer.getvalue()


def _construir_estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "normal": base["Normal"],
        "encabezado": ParagraphStyle(
            "Encabezado",
            parent=base["Normal"],
            fontSize=14,
            leading=18,
            textColor=COLOR_TALINAY,
            spaceAfter=4,
        ),
        "sub": ParagraphStyle(
            "Sub",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=COLOR_SUBTEXTO,
        ),
        "titulo": ParagraphStyle(
            "Titulo",
            parent=base["Heading1"],
            fontSize=18,
            leading=22,
            spaceAfter=12,
            textColor=colors.black,
        ),
        "seccion": ParagraphStyle(
            "Seccion",
            parent=base["Heading2"],
            fontSize=11,
            leading=14,
            spaceBefore=14,
            spaceAfter=6,
            textColor=COLOR_TALINAY,
        ),
        "pie": ParagraphStyle(
            "Pie",
            parent=base["Normal"],
            fontSize=9,
            leading=12,
            textColor=COLOR_PIE,
            spaceBefore=6,
        ),
    }


def _agregar_encabezado(elementos, estilos):
    elementos.append(Paragraph(TALINAY_RAZON_SOCIAL, estilos["encabezado"]))
    elementos.append(Paragraph(TALINAY_DIRECCION, estilos["sub"]))
    elementos.append(Paragraph(f"{TALINAY_WEB} · {TALINAY_EMAIL}", estilos["sub"]))
    elementos.append(Spacer(1, 0.4 * cm))

    sep = Table([[""]], colWidths=[17 * cm], rowHeights=[1])
    sep.setStyle(
        TableStyle([("LINEABOVE", (0, 0), (-1, -1), 1, COLOR_TALINAY)])
    )
    elementos.append(sep)
    elementos.append(Spacer(1, 0.3 * cm))


def _agregar_titulo(elementos, estilos):
    elementos.append(Paragraph("Cotización", estilos["titulo"]))


def _agregar_referencia(elementos, estilos, oportunidad):
    elementos.append(Paragraph("Referencia", estilos["seccion"]))
    elementos.append(
        Paragraph(
            f"<b>Código:</b> {_safe(oportunidad.get('codigo'))}",
            estilos["normal"],
        )
    )
    elementos.append(
        Paragraph(
            f"<b>Compra:</b> {_safe(oportunidad.get('nombre'))}",
            estilos["normal"],
        )
    )
    elementos.append(
        Paragraph(
            f"<b>Organismo:</b> {_safe(oportunidad.get('organismo'))}",
            estilos["normal"],
        )
    )


def _agregar_cuerpo(elementos, estilos, cotizacion):
    elementos.append(Paragraph("Productos ofrecidos", estilos["seccion"]))
    texto = (
        cotizacion.get("borrador_editado")
        or cotizacion.get("borrador_ia")
        or "(sin contenido)"
    )
    elementos.append(Paragraph(_a_html(texto), estilos["normal"]))


def _agregar_condiciones(elementos, estilos, cotizacion):
    elementos.append(Paragraph("Condiciones", estilos["seccion"]))
    filas = [
        ["Precio total ofertado:", _formato_clp(cotizacion.get("precio_ofertado"))],
        [
            "Plazo de entrega:",
            f"{_safe(cotizacion.get('plazo_entrega_dias'), default='—')} días hábiles",
        ],
        [
            "Despacho:",
            "Coordinado con el organismo al confirmar la orden de compra.",
        ],
    ]
    tabla = Table(filas, colWidths=[5 * cm, 12 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elementos.append(tabla)


def _agregar_pie(elementos, estilos):
    elementos.append(Spacer(1, 0.6 * cm))
    elementos.append(
        Paragraph("Cotización válida por 5 días hábiles.", estilos["pie"])
    )
    fecha = datetime.now().strftime("%d/%m/%Y")
    elementos.append(Paragraph(f"Generada el {fecha}.", estilos["pie"]))


def _formato_clp(monto) -> str:
    if monto is None or monto == "":
        return "—"
    try:
        n = int(float(monto))
    except (TypeError, ValueError):
        return str(monto)
    return "$" + f"{n:,}".replace(",", ".") + " CLP"


def _safe(valor, default: str = "—") -> str:
    if valor is None or valor == "":
        return default
    return str(valor)


def _a_html(texto: str) -> str:
    """Convierte saltos de línea a <br/> para que ReportLab los respete
    dentro de un Paragraph, y escapa los caracteres mínimos."""
    escapado = (
        texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return escapado.replace("\n", "<br/>")
