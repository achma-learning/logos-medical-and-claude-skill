import os, sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

L = "/usr/share/fonts/truetype/liberation/"
F = "/usr/share/fonts/truetype/freefont/"
pdfmetrics.registerFont(TTFont("Serif", L + "LiberationSerif-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Serif-B", L + "LiberationSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BI", L + "LiberationSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Ar", F + "FreeSerif.ttf"))
pdfmetrics.registerFont(TTFont("Ar-B", F + "FreeSerifBold.ttf"))

W, H = A4
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
MS_LOGO = os.path.join(ASSETS, "nb", "ministere-sante-embleme-nb.png")
ARMS = os.path.join(ASSETS, "nb", "royaume-maroc-armoiries-nb.png")


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def dots(c, x1, x2, y, size=9):
    """Dotted leader from x1 to x2 at baseline y."""
    c.saveState()
    c.setFont("Serif", size)
    dw = pdfmetrics.stringWidth(".", "Serif", size)
    n = int((x2 - x1) / dw)
    c.drawString(x1, y, "." * n)
    c.restoreState()


def underline(c, x, y, text, font, size, gap=2.2, lw=0.8):
    w = pdfmetrics.stringWidth(text, font, size)
    c.setLineWidth(lw)
    c.line(x, y - gap, x + w, y - gap)


# ---------------------------------------------------------------- Cessation / Reprise
def service_form(c, top, kind):
    """One form block; `top` = y of the block's top edge. kind: 'cessation' | 'reprise'."""
    xl, xr = 72, W - 68
    # Header
    c.setFont("Serif-B", 11)
    c.drawCentredString(140, top - 30, "ROYAUME DU MAROC")
    c.drawCentredString(140, top - 44, "MINISTERE DE LA SANTE")
    lw = 54
    c.drawImage(MS_LOGO, xr - lw - 6, top - 62, width=lw, height=lw * 607 / 666)

    # Préfecture / PPR
    y = top - 86
    c.setFont("Serif-B", 10.5)
    c.drawString(xl + 10, y, "Préfecture : MARRAKECH")
    c.drawString(xl + 10, y - 14, "Formation :")
    dots(c, xl + 10 + pdfmetrics.stringWidth("Formation : ", "Serif-B", 10.5), xl + 170, y - 14)
    rx = 345
    c.drawString(rx, y, "Mle à la PPR :")
    dots(c, rx + pdfmetrics.stringWidth("Mle à la PPR : ", "Serif-B", 10.5), rx + 150, y)
    c.drawString(rx, y - 14, "N° C I N :")
    dots(c, rx + pdfmetrics.stringWidth("N° C I N : ", "Serif-B", 10.5), xr - 8, y - 14)

    # Title
    title = f"Compte rendu de {kind} de Service"
    ty = top - 140
    c.setFont("Serif-B", 17)
    tw = pdfmetrics.stringWidth(title, "Serif-B", 17)
    c.drawString((W - tw) / 2, ty, title)
    c.setLineWidth(1)
    c.line((W - tw) / 2, ty - 3.5, (W + tw) / 2, ty - 3.5)

    # Fields
    fields = [
        "Nom et prénom :",
        "Grade :",
        "Nature du congé ou de l'absence :",
        "Date de la décision :",
        "Adresse de l'agent pendant son congé :",
        f"Date de {kind} de service :",
    ]
    fx, fr = xl + 18, xr - 4
    y = ty - 32
    for f in fields:
        c.setFont("Serif-B", 10.5)
        c.drawString(fx, y, f)
        dots(c, fx + pdfmetrics.stringWidth(f + " ", "Serif-B", 10.5), fr, y)
        y -= 15.5
    c.setFont("Serif-B", 10.5)
    c.drawString(fx, y, "OBSERVATIONS :")
    underline(c, fx, y, "OBSERVATIONS", "Serif-B", 10.5)
    for _ in range(2):
        y -= 16
        dots(c, fx, fr, y)

    # Signatures
    y -= 34
    c.setFont("Serif-B", 10.5)
    cols = [
        (xl + 25, ["L'agent"]),
        (xl + 120, ["Le chef du service"]),
        (xl + 245, ["Le Médecin chef", "du SRES"]),
        (xr - 62, ["Le Délégué du MS et de", "la Protection sociale à", "la Préfecture de MRK"]),
    ]
    for cx, lines in cols:
        for i, t in enumerate(lines):
            c.drawCentredString(cx, y - i * 12.5, t)


def build_service(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Comptes rendus de cessation et de reprise de service")
    c.setAuthor("Ministère de la Santé - Préfecture de Marrakech")
    for kind in ("cessation", "reprise"):
        service_form(c, H - 18, kind)
        # cutting guide between the two copies
        c.saveState()
        c.setDash(3, 3)
        c.setStrokeGray(0.65)
        c.setLineWidth(0.5)
        c.line(30, H / 2, W - 30, H / 2)
        c.restoreState()
        service_form(c, H / 2 - 14, kind)
        c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Compte_rendu_cessation_reprise_service.pdf"
    build_service(out)
    print(out)
