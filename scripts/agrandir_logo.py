"""Agrandit un petit logo raster ×4 (super-résolution EDSR), avec découpe ronde optionnelle.

Usage :
  python3 agrandir_logo.py entree.jpg sortie.png [--cercle CX CY R] [--modele EDSR_x4.pb]

  --cercle CX CY R  logo circulaire : centre et rayon en pixels DE L'IMAGE SOURCE ;
                    tout ce qui est hors du cercle devient transparent (bord anticrénelé),
                    l'intérieur (y compris un fond blanc de badge) est conservé.
  --modele          modèle EDSR ×4 (OpenCV dnn_superres). Défaut : EDSR_x4.pb à côté du
                    script, sinon ~/saafke/edsr_tensorflow/models/EDSR_x4.pb.
                    Obtention : git clone --depth 1 https://github.com/Saafke/EDSR_Tensorflow
                    (38 Mo, non inclus dans la skill). pip : opencv-contrib-python-headless.
                    Sans modèle : repli sur Lanczos ×4 (net mais plus flou) + avertissement.

Pour trouver CX CY R : boîte englobante de l'anneau extérieur du logo
(pixels dont min(R,G,B) < 215) → centre = milieu de la boîte, R = largeur / 2.
Logo non circulaire : agrandir, puis passer le résultat dans optimiser_logo.py.
Une super-résolution reconstitue des bords nets mais n'invente pas de détail :
préférer une source vectorielle quand elle existe (vector.ma, seeklogo.com).
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ICI = os.path.dirname(os.path.abspath(__file__))
MODELES = [os.path.join(ICI, "EDSR_x4.pb"),
           os.path.expanduser("~/saafke/edsr_tensorflow/models/EDSR_x4.pb"),
           "/home/claude/saafke/edsr_tensorflow/models/EDSR_x4.pb"]


def agrandir(im, modele=None):
    chemin = modele or next((m for m in MODELES if os.path.exists(m)), None)
    try:
        import cv2
        if not chemin or not hasattr(cv2, "dnn_superres"):
            raise ImportError
        sr = cv2.dnn_superres.DnnSuperResImpl_create()
        sr.readModel(chemin)
        sr.setModel("edsr", 4)
        up = sr.upsample(cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR))
        up = Image.fromarray(cv2.cvtColor(up, cv2.COLOR_BGR2RGB))
    except (ImportError, Exception) as e:
        print(f"AVERTISSEMENT : EDSR indisponible ({e.__class__.__name__}) → Lanczos ×4", file=sys.stderr)
        up = im.resize((im.width * 4, im.height * 4), Image.LANCZOS)
    return up.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))


def main():
    a = sys.argv[1:]
    src, dst = a[0], a[1]
    modele = a[a.index("--modele") + 1] if "--modele" in a else None
    im = Image.open(src).convert("RGB")
    if "--cercle" in a:
        i = a.index("--cercle")
        cx, cy, r = (float(v) for v in a[i + 1:i + 4])
        b = (int(round(cx - r)) - 2, int(round(cy - r)) - 2, int(round(cx + r)) + 3, int(round(cy + r)) + 3)
        c = Image.new("RGB", (b[2] - b[0], b[3] - b[1]), "white")
        c.paste(im.crop((max(b[0], 0), max(b[1], 0), min(b[2], im.width), min(b[3], im.height))),
                (max(0, -b[0]), max(0, -b[1])))
        up = agrandir(c, modele)
        ss = 4
        m = Image.new("L", (up.width * ss, up.height * ss), 0)
        R, X, Y = r * 4 * ss, (cx - b[0]) * 4 * ss, (cy - b[1]) * 4 * ss
        ImageDraw.Draw(m).ellipse([X - R, Y - R, X + R, Y + R], fill=255)
        up.putalpha(m.resize(up.size, Image.LANCZOS))
        al = np.asarray(up)[..., 3]
        ys, xs = np.where(al > 0)
        up = up.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    else:
        up = agrandir(im, modele)
    up.save(dst, optimize=True)
    print(dst, up.size)


if __name__ == "__main__":
    main()
