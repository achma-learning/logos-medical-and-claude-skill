"""Régénère la planche d'aperçu assets/catalogue.png depuis assets/catalogue.json.

Usage :
  python3 planche_catalogue.py [sortie.png]

Une vignette de 240 px par logo (5 colonnes), dans l'ordre du catalogue :
logo centré (sur fond sombre si sa variante contient « fond sombre »), id en gras, « catégorie · formats » en gris dessous.
À relancer après tout ajout / retrait de logo dans catalogue.json.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ICI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(ICI, ".."))
CAT = json.load(open(os.path.join(SK, "assets", "catalogue.json"), encoding="utf-8"))
T, COLS = 240, 5


def police(nom, taille):
    try:
        return ImageFont.truetype(f"/usr/share/fonts/truetype/dejavu/{nom}.ttf", taille)
    except OSError:
        return ImageFont.load_default()


def main():
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SK, "assets", "catalogue.png")
    fb, fr = police("DejaVuSans-Bold", 12), police("DejaVuSans", 10)
    rows = (len(CAT) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * T, rows * T), "white")
    for i, e in enumerate(CAT):
        src = next(f["fichier"] for f in e["fichiers"] if f["format"] == "png")
        im = Image.open(os.path.join(SK, src)).convert("RGBA")
        im.thumbnail((T - 20, T - 64))
        t = Image.new("RGBA", (T, T), "white")
        x, y = (T - im.width) // 2, 8 + (T - 64 - im.height) // 2
        d = ImageDraw.Draw(t)
        if "fond sombre" in e["variante"]:  # logo blanc : invisible sur la vignette blanche sinon
            d.rectangle([x - 4, y - 4, x + im.width + 3, y + im.height + 3], fill=(60, 60, 60))
        t.alpha_composite(im, (x, y))
        d.rectangle([0, 0, T - 1, T - 1], outline=(210, 210, 210))
        d.text((6, T - 50), e["id"], fill="black", font=fb)
        formats = "/".join(f["format"] for f in e["fichiers"])
        d.text((6, T - 32), f"{e['categorie']} · {formats}", fill=(110, 110, 110), font=fr)
        sheet.paste(t.convert("RGB"), ((i % COLS) * T, (i // COLS) * T))
    sheet.save(dst, optimize=True)
    print(os.path.abspath(dst))


if __name__ == "__main__":
    main()
