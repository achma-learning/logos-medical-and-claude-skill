"""Vectorise un logo raster à aplats de couleurs → SVG (+ PDF, + PNG rendu).

Usage :
  python3 vectoriser_logo.py entree.png sortie.svg --palette 657f64,ffffff,da4438,22936a
                             [--cercle] [--fond 657f64] [--anti-halo] [--png 2000]

  --palette   couleurs du logo en hex (2 à 8). Les mesurer sur l'image : médiane des
              pixels saturés de chaque zone. Chaque pixel est ramené à la plus proche.
  --cercle    badge rond : contour = cercle parfait (clipPath) au lieu du contour tracé,
              qui ondule toujours un peu. Le cercle est déduit de la zone opaque du PNG.
  --fond      couleur du disque de base sous le tracé (évite tout liseré au bord) ;
              par défaut la couleur la plus fréquente sur le pourtour.
  --anti-halo les pixels de bord d'un texte foncé (anticrénelage) sont rattachés au
              foncé ou au blanc, jamais à une couleur claire intermédiaire de la palette
              (sinon : liseré coloré autour des lettres).
  --png N     écrit aussi sortie.png (N px de large, fond transparent) et sortie.pdf.

Pipeline : palette → filtre de majorité 5×5 (supprime les mouchetures JPEG) →
vtracer (splines, empilement) → viewBox, sans taille fixe → clip circulaire optionnel.
Partir de préférence d'un PNG déjà agrandi (agrandir_logo.py) : plus de pixels = courbes
plus justes. Limite : c'est un tracé, pas le fichier d'origine — bords légèrement lissés,
dégradés aplatis, petits détails < 3 px fusionnés. Toujours comparer visuellement.
pip : vtracer cairosvg scipy pillow
"""
import re, sys
import numpy as np
from PIL import Image, ImageFilter


def hexrgb(h):
    h = h.strip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def snap(a, palette, anti_halo=False):
    from scipy import ndimage
    rgb = a[..., :3].astype(np.float32)
    pal = np.array(palette, np.float32)
    idx = ((rgb[:, :, None] - pal[None, None]) ** 2).sum(-1).argmin(-1).astype(np.uint8)
    if anti_halo:
        lum = pal @ np.array([.299, .587, .114], np.float32)
        dark, light = int(lum.argmin()), int(lum.argmax())
        near_dark = ndimage.binary_dilation(idx == dark, iterations=4)
        mid = (idx != dark) & (idx != light) & near_dark
        px_l = (rgb @ np.array([.299, .587, .114], np.float32))
        idx[mid] = np.where(px_l[mid] < (lum[dark] + lum[light]) / 2, dark, light)
    return np.asarray(Image.fromarray(idx).filter(ImageFilter.ModeFilter(5))), pal.astype(np.uint8)


def main():
    a_ = sys.argv[1:]
    src, dst = a_[0], a_[1]
    opt = lambda k, d=None: a_[a_.index(k) + 1] if k in a_ else d
    palette = [hexrgb(x) for x in opt("--palette").split(",")]
    im = np.asarray(Image.open(src).convert("RGBA"))
    opaque = im[..., 3] > 127
    idx, pal = snap(im, palette, "--anti-halo" in a_)
    H, W = idx.shape
    out = pal[idx]
    alpha = np.where(opaque, 255, 0).astype(np.uint8)
    circle = None
    if "--cercle" in a_:
        ys, xs = np.where(opaque)
        cx, cy = (xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2
        R = (xs.max() - xs.min() + 1) / 2
        yy, xx = np.mgrid[0:H, 0:W]
        dist = np.hypot(xx + .5 - cx, yy + .5 - cy)
        rim = (dist > R - 8) & opaque
        fond = hexrgb(opt("--fond")) if opt("--fond") else tuple(
            pal[np.bincount(idx[rim], minlength=len(pal)).argmax()])
        # prolonge le fond au-delà du cercle : le bord net vient du clipPath, pas du tracé
        out[dist > R - 1] = fond
        alpha[dist > R - 1] = 255
        circle = (cx, cy, R - 1, "#%02x%02x%02x" % tuple(fond))
    tmp = dst + ".snap.png"
    Image.fromarray(np.dstack([out, alpha]), "RGBA").save(tmp)
    import vtracer, os
    vtracer.convert_image_to_svg_py(tmp, dst, colormode="color", hierarchical="stacked", mode="spline",
                                    filter_speckle=6, color_precision=8, layer_difference=8,
                                    corner_threshold=60, length_threshold=4.0, max_iterations=10,
                                    splice_threshold=45, path_precision=2)
    os.remove(tmp)
    s = open(dst).read()
    m = re.search(r' width="(\d+)" height="(\d+)"', s)
    s = s.replace(m.group(0), f' viewBox="0 0 {m.group(1)} {m.group(2)}"', 1)
    if circle:
        cx, cy, r, f = circle
        h_end = s.index(">", s.index("<svg")) + 1
        s = (s[:h_end] + f'<defs><clipPath id="badge"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}"/>'
             f'</clipPath></defs><g clip-path="url(#badge)"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{f}"/>'
             + s[h_end:s.rindex("</svg>")] + "</g></svg>")
    open(dst, "w").write(s)
    print(dst, s.count("<path"), "tracés")
    if opt("--png"):
        import cairosvg
        base = dst[:-4]
        cairosvg.svg2pdf(url=dst, write_to=base + ".pdf")
        cairosvg.svg2png(url=dst, write_to=base + ".png", output_width=int(opt("--png")))
        print(base + ".pdf", base + ".png")


if __name__ == "__main__":
    main()
