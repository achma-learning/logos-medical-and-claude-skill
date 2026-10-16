"""Prépare un logo de la bibliothèque pour le remettre à l'utilisateur (téléchargement).

Usage :
  python3 donner_logo.py <id ou mots-clés> [--sortie DOSSIER] [--largeur PX]
                         [--nb [GAMMA]] [--format png|svg|pdf|tous] [--lister]

  <id ou mots-clés>  id exact (ex. msps-logo-vertical), nom d'élément (ex. chu-mohammed-vi
                     -> liste toutes ses variantes) ou mots-clés (ex. chu paysage).
                     Un même élément (organisme) peut avoir plusieurs variantes :
                     vertical/horizontal, bandeau, ancien/nouveau nom, langue…
  --sortie           dossier de destination (défaut : ./logos_remis).
  --largeur          redimensionne le PNG à cette largeur (jamais d'agrandissement
                     au-delà de la source raster ; les logos vectoriels sont
                     re-rendus nets à n'importe quelle largeur).
  --nb [GAMMA]       version noir & blanc assombrie pour impression (gamma 1.6
                     par défaut), transparence conservée.
  --format           png (défaut) | svg | pdf | tous (tout ce qui existe).
  --lister           affiche seulement les correspondances, sans rien copier.
  --apercu           si plusieurs correspondances : crée aussi apercu-variantes.png
                     (planche numérotée) à montrer à l'utilisateur pour qu'il choisisse.

Sortie : imprime le(s) chemin(s) créé(s), un par ligne — à envoyer ensuite à
l'utilisateur avec SendUserFile (ou present_files).
Code retour 2 si plusieurs logos correspondent (la liste est affichée) :
demander alors à l'utilisateur lequel il veut.
"""
import io, json, os, shutil, sys, unicodedata
from PIL import Image

ICI = os.path.dirname(os.path.abspath(__file__))
SK = os.path.normpath(os.path.join(ICI, ".."))
CAT = json.load(open(os.path.join(SK, "assets", "catalogue.json"), encoding="utf-8"))


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").replace("-", " ")


def chercher(q):
    for e in CAT:
        if e["id"] == q:
            return [e]
    # nom d'élément exact -> toutes ses variantes
    variantes = [e for e in CAT if e["element"] == q]
    if variantes:
        return variantes
    mots = norm(q).split()
    res = []
    for e in CAT:
        texte = norm(" ".join([e["id"], e["element"], e["variante"], e["categorie"], e["description"]]))
        if all(m in texte for m in mots):
            res.append(e)
    return res


def fichier(e, fmt):
    for f in e["fichiers"]:
        if f["format"] == fmt:
            return os.path.join(SK, f["fichier"])
    return None


def png(e, largeur=None):
    svg = fichier(e, "svg")
    src = fichier(e, "png")
    im = Image.open(src).convert("RGBA")
    if largeur and largeur > im.width and svg:
        import cairosvg  # rendu vectoriel net
        im = Image.open(io.BytesIO(cairosvg.svg2png(url=svg, output_width=largeur))).convert("RGBA")
    elif largeur and largeur < im.width:
        im = im.resize((largeur, round(im.height * largeur / im.width)), Image.LANCZOS)
    return im


def apercu(res, dst):
    """Planche des variantes trouvées (pour aider l'utilisateur à choisir)."""
    from PIL import ImageDraw, ImageFont
    T, cols = 260, min(4, len(res))
    try:
        fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        fr = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    except OSError:
        fb = fr = ImageFont.load_default()
    rows = (len(res) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * T, rows * T), "white")
    for i, e in enumerate(res):
        im = Image.open(fichier(e, "png")).convert("RGBA")
        im.thumbnail((T - 20, T - 60))
        t = Image.new("RGBA", (T, T), "white")
        t.alpha_composite(im, ((T - im.width) // 2, 10 + (T - 60 - im.height) // 2))
        d = ImageDraw.Draw(t)
        d.rectangle([0, 0, T - 1, T - 1], outline=(215, 215, 215))
        d.text((8, T - 44), f"{i + 1}. {e['variante']}"[:36], fill="black", font=fb)
        d.text((8, T - 24), e["id"][:40], fill=(110, 110, 110), font=fr)
        sheet.paste(t.convert("RGB"), ((i % cols) * T, (i // cols) * T))
    sheet.save(dst, optimize=True)
    return dst


def noir_blanc(im, g=1.6):
    r, gch, b, a = im.split()
    gris = Image.merge("RGB", (r, gch, b)).convert("L")
    gris = gris.point([int(255 * ((i / 255) ** g)) for i in range(256)])
    return Image.merge("LA", (gris, a))


def main():
    a = sys.argv[1:]
    if not a or a[0].startswith("--"):
        print(__doc__); sys.exit(1)
    pos = []
    for x in a:
        if x.startswith("--"):
            break
        pos.append(x)
    q = " ".join(pos)
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) and not a[a.index(k) + 1].startswith("--") else d
    sortie = opt("--sortie", "logos_remis")
    largeur = int(opt("--largeur")) if opt("--largeur") else None
    fmt = opt("--format", "png")
    nb = "--nb" in a
    gamma = float(opt("--nb", 1.6)) if nb else None

    res = chercher(q)
    if not res:
        print(f"Aucun logo ne correspond à « {q} ». Ids disponibles :")
        for e in CAT:
            print(f"  {e['id']}")
        sys.exit(1)
    if len(res) > 1 or "--lister" in a:
        elements = sorted({e["element"] for e in res})
        if len(res) > 1:
            print(f"# {len(res)} correspondances ({len(elements)} élément(s)) — demander laquelle :")
        for el in elements:
            print(f"[{el}]")
            for e in (x for x in res if x["element"] == el):
                fm = "/".join(f["format"] for f in e["fichiers"])
                px = next((f.get("px", "") for f in e["fichiers"] if f["format"] == "png"), "")
                print(f"  {e['id']}\t{e['variante']}\t{fm}\t{px}")
        if "--apercu" in a and len(res) > 1:
            os.makedirs(sortie, exist_ok=True)
            print(os.path.abspath(apercu(res, os.path.join(sortie, "apercu-variantes.png"))))
        sys.exit(2 if len(res) > 1 else 0)

    e = res[0]
    os.makedirs(sortie, exist_ok=True)
    suffixe = "-nb" if nb else ""
    sorties = []
    formats = [f["format"] for f in e["fichiers"]] if fmt == "tous" else [fmt]
    for f in formats:
        dst = os.path.join(sortie, f"{e['id']}{suffixe}.{f}")
        if f == "png":
            im = png(e, largeur)
            if nb:
                im = noir_blanc(im, gamma)
            im.save(dst, optimize=True)
        else:
            src = fichier(e, f)
            if not src:
                print(f"(pas de version {f} pour {e['id']})", file=sys.stderr)
                continue
            shutil.copyfile(src, dst)
        sorties.append(dst)
    for s in sorties:
        print(os.path.abspath(s))


if __name__ == "__main__":
    main()
