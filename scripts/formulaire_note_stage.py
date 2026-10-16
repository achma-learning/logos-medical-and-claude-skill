"""'Note de stage de 5ème année' — original structure, full-width spacing, B&W print."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formulaire_cessation_reprise import *  # fonts, helpers, W, H, ar, dots, underline

ARMS_BW = os.path.join(ASSETS, "nb", "royaume-maroc-armoiries-nb.png")
M = 56
XL, XR = M, W - M


def leader(c, x, y, label, font="Serif", size=11, x2=XR):
    c.setFont(font, size)
    c.drawString(x, y, label)
    dots(c, x + pdfmetrics.stringWidth(label + " ", font, size), x2, y, 10)


def build_note(path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Note de stage de 5ème année")
    c.setAuthor("Ministère de la Santé et de la Protection Sociale - SRES Marrakech")

    # ---------------- Header (same 3-part layout as the original, widened)
    top = H - 50
    c.setFont("Serif", 9.5)
    lh = 12.2
    fr = ["ROYAUME DU MAROC", "MINISTERE DE LA SANTE ET DE PROTECTION",
          "SOCIALE", "REGION MARRAKECH – SAFI", "PREFECTURE DE MARRAKECH", "SRES"]
    lcx = XL + 88
    for i, t in enumerate(fr):
        c.drawCentredString(lcx, top - i * lh, t)
    w = pdfmetrics.stringWidth("SRES", "Serif", 9.5)
    c.setLineWidth(0.7)
    c.line(lcx - w / 2, top - 5 * lh - 2, lcx + w / 2, top - 5 * lh - 2)

    aw = 62
    ah = aw * 748 / 685
    c.drawImage(ARMS_BW, W / 2 - aw / 2, top - ah + 10, width=aw, height=ah)

    arl = ["المملكة المغربية", "وزارة الصحة والحماية الاجتماعية", "جهة مراكش آسفي",
           "عمالة مراكش", "مصلحة شبكة المؤسسات الصحية"]
    rcx = XR - 95
    alh = 14.5
    c.setFont("Ar", 13)
    for i, t in enumerate(arl):
        c.drawCentredString(rcx, top + 1 - i * alh, ar(t))
    sw = pdfmetrics.stringWidth(ar(arl[-1]), "Ar", 13)
    c.line(rcx - sw / 2, top + 1 - 4 * alh - 4, rcx + sw / 2, top + 1 - 4 * alh - 4)

    # ---------------- Title
    ty = top - 125
    a, sup, b = "NOTE  DE  STAGE  DE  5", "ème", "  ANNEE"
    wa = pdfmetrics.stringWidth(a, "Serif-B", 20)
    ws = pdfmetrics.stringWidth(sup, "Serif-B", 11.5)
    wb = pdfmetrics.stringWidth(b, "Serif-B", 20)
    x0 = (W - (wa + ws + wb)) / 2
    c.setFont("Serif-B", 20); c.drawString(x0, ty, a)
    c.setFont("Serif-B", 11.5); c.drawString(x0 + wa + 0.5, ty + 8, sup)
    c.setFont("Serif-B", 20); c.drawString(x0 + wa + ws + 1, ty, b)
    c.setLineWidth(1.1)
    c.line(x0, ty - 3.5, x0 + wa + ws + wb + 1, ty - 3.5)

    # ---------------- Identity
    step = 23
    y = ty - 40
    for t in ["NOM ET PRENOM :", "SERVICE :", "DATE DE DEBUT DE STAGE :", "DATE DE FIN DE STAGE :"]:
        leader(c, XL, y, t)
        y -= step

    # ---------------- Note de stage
    sx = XL + 8
    y -= 10
    c.setFont("Serif-B", 12)
    c.drawString(sx, y, "NOTE DE STAGE :")
    underline(c, sx, y, "NOTE DE STAGE", "Serif-B", 12)

    def sub(prefix, label, y):
        c.setFont("Serif-B", 11)
        pw = pdfmetrics.stringWidth(prefix, "Serif-B", 11)
        c.drawString(sx + 6, y, prefix + label + " :")
        underline(c, sx + 6 + pw, y, label, "Serif-B", 11, lw=0.7)
        return pdfmetrics.stringWidth(prefix + label + " : ", "Serif-B", 11)

    def bullets(items, y):
        for t in items:
            c.circle(sx + 26, y + 3.4, 2, stroke=0, fill=1)
            leader(c, sx + 46, y, t + " :")
            y -= step
        return y

    y -= 28
    sub("A-/ ", "COMPORTEMENT", y)
    y -= step + 2
    y = bullets(["DISCIPLINE", "RELATION  AVEC LE PERSONNEL", "ATTITUDE  AVEC  LES PATIENTS"], y)
    y -= 8
    sub("B-/", "ATTITUDE PROFESSIONNELLE", y)
    y -= step + 2
    y = bullets(["CONNAISSANCE", "SENS DE L'ORGANISATION", "SENS DE RESPONSABILITE"], y)
    y -= 8
    wc = sub("C-/ ", "PONCTUALITE", y)
    dots(c, sx + 6 + wc, XR, y, 10)

    # ---------------- Final grade + date
    y -= 62
    c.setFont("Serif", 12.5)
    c.drawString(sx + 6, y, "NOTE DE STAGE :")
    c.setLineWidth(1.1)
    c.rect(sx + 128, y - 17, 92, 46)
    leader(c, XR - 190, y, "Marrakech, le", size=12.5)

    # ---------------- Signatures
    y -= 72
    c.setFont("Serif", 11)
    c.drawCentredString(XL + 100, y, "LE MEDECIN CHEF DE LA  C/S")
    c.drawCentredString(XR - 100, y, "LE MEDECIN CHEF DU S.R.E.S")
    y -= 105
    c.drawCentredString(W / 2, y, "LE DELEGUE  DU M.S  A  LA PREFECTURE")
    c.drawCentredString(W / 2, y - 13.5, "DE MARRAKECH")

    c.showPage()
    c.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "Note_de_stage_5eme_annee.pdf"
    build_note(out)
    print(out)
