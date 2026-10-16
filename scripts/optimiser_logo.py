"""Optimise un logo raster : fond blanc -> transparent, rognage, PNG optimisé.

Usage : python3 optimiser_logo.py entree.(png|jpg) sortie.png [--garder-fond] [--sans-enclaves] [--marge 0.01]
  --sans-enclaves : garder les petites zones blanches enclavées (logo posé sur un cartouche blanc)

Principe (préserve les blancs INTÉRIEURS du logo) :
1. Le fond = pixels quasi blancs CONNECTÉS AU BORD de l'image (remplissage par
   diffusion depuis les bords, comme la baguette magique), PLUS les petites
   enclaves blanches (< 2 % de l'image : intérieur des lettres A, O, R…). Les
   grandes zones blanches entourées par le logo (fond d'un cartouche, anneau
   blanc) font partie du design et sont conservées.
2. Sur la frontière (fond dilaté de 2 px) on applique « couleur vers alpha »
   (algorithme GIMP) avec seuil : seuls les pixels clairs de l'anticrénelage
   deviennent semi-transparents (plus de halo blanc), les traits gris/colorés fins
   restent opaques ; le bruit JPEG résiduel est mis à 0. Un fond déjà transparent
   est traité comme du fond (supprime les halos blancs des PNG détourés).
3. Rognage sur le contenu visible + marge, PNG RGBA optimisé.
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

SEUIL_FOND = 228      # min(R,G,B) au-dessus duquel un pixel peut être du fond
SEUIL_COEUR = 246     # fond « sûr » -> alpha 0 direct
ALPHA_MIN = 0.06      # en dessous : bruit -> transparent
PETITE_ENCLAVE = 0.02 # enclave blanche < 2 % de l'image -> contre-forme -> transparente
OPAQUE_DES = 0.5      # couleur assez foncée (>= 50 % d'écart au blanc) -> reste opaque


def fond_transparent(im, enclaves=True):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3] / 255.0
    mn = rgb.min(axis=2)
    # le fond déjà transparent compte aussi comme fond (élimine les halos blancs)
    candidat = ((mn >= SEUIL_FOND) & (alpha > 0)) | (alpha < 0.04)
    lab, _ = ndimage.label(candidat)
    bord = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    fond = np.isin(lab, list(bord))
    # blancs ENCLAVÉS petits = contre-formes de lettres (intérieur de A, R, D, O…)
    # -> fond aussi. Les grandes zones blanches enclavées (carte blanche d'un logo
    # encadré, anneau du Croissant-Rouge) sont des éléments du design : conservées.
    if enclaves:
        tailles = np.bincount(lab.ravel())
        petits = np.where(tailles < PETITE_ENCLAVE * lab.size)[0]
        petits = np.setdiff1d(petits, list(bord) + [0])
        fond |= np.isin(lab, petits)
    if not fond.any():
        return im.convert("RGBA")
    zone = ndimage.binary_dilation(fond, iterations=2)
    # couleur -> alpha (blanc)
    ca = ((255.0 - rgb) / 255.0).max(axis=2)
    ca = np.where(ca < ALPHA_MIN, 0.0, ca)
    # seuil : seuls les pixels clairs (halo d'anticrénelage) deviennent translucides ;
    # un texte gris ou coloré fin reste opaque au lieu de « fondre »
    ca = np.clip(ca / OPAQUE_DES, 0.0, 1.0)
    safe = np.maximum(ca, 1e-6)[..., None]
    new_rgb = (rgb - 255.0 * (1.0 - safe)) / safe
    new_rgb = np.clip(new_rgb, 0, 255)
    out_rgb = np.where(zone[..., None], new_rgb, rgb)
    out_a = np.where(zone, np.minimum(alpha, ca), alpha)
    out_a = np.where(fond & (mn >= SEUIL_COEUR), 0.0, out_a)
    out = np.dstack([out_rgb, out_a * 255.0]).round().astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def rogner(im, marge=0.01):
    a = np.asarray(im)[..., 3]
    ys, xs = np.where(a > 8)
    if len(ys) == 0:
        return im
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    p = int(round(max(x1 - x0, y1 - y0) * marge))
    c = im.crop((x0, y0, x1, y1))
    out = Image.new("RGBA", (c.width + 2 * p, c.height + 2 * p), (0, 0, 0, 0))
    out.paste(c, (p, p))
    return out


def optimiser(src, dst, garder_fond=False, marge=0.01, enclaves=True):
    im = Image.open(src)
    im = im.convert("RGBA") if garder_fond else fond_transparent(im, enclaves)
    im = rogner(im, marge)
    # nettoyer la couleur des pixels totalement transparents (meilleure compression)
    a = np.asarray(im).copy()
    a[a[..., 3] == 0, :3] = 0
    Image.fromarray(a, "RGBA").save(dst, optimize=True)
    return Image.open(dst).size


if __name__ == "__main__":
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    marge = 0.01
    if "--marge" in sys.argv:
        marge = float(sys.argv[sys.argv.index("--marge") + 1])
        args = [x for x in args if x != str(marge) and x != sys.argv[sys.argv.index("--marge") + 1]]
    print(optimiser(args[0], args[1], "--garder-fond" in sys.argv, marge, "--sans-enclaves" not in sys.argv))
