---
name: logos-officiels-maroc
description: Bibliothèque de 48 logos marocains optimisés (PNG transparent + SVG/PDF vectoriels quand disponibles) — armoiries, drapeau et carte du Maroc, Région Marrakech-Safi (logo, drapeau) et armoiries de la ville de Marrakech, Ministère de la Santé / MSPS, CHU Mohammed VI et Hôpital Ibn Tofail, FMPM, Université Cadi Ayyad, associations AMIMA (médecins internes) et ALMOQUIM (médecins résidents) de Marrakech, OMS/WHO, Ordre des Médecins, Croissant-Rouge, Centre de Transfusion Sanguine, Fondation Mohammed V, FAR et Hôpital Militaire Marrakech — avec un script qui remet le logo demandé en PNG téléchargeable, plus les générateurs PDF des formulaires de la Préfecture de Marrakech (cessation/reprise de service, note de stage 5ème année). À utiliser DÈS que l'utilisateur demande, cite ou a besoin d'un logo, d'un emblème, des armoiries, d'un en-tête officiel, d'une page de garde, d'une attestation, d'un formulaire ou d'une lettre à en-tête — même s'il a joint son propre fichier.
---

# Logos officiels marocains + formulaires MS Marrakech

Consignes explicites de l'utilisateur — à appliquer à chaque fois.

## RÈGLE 1 — Remettre un logo demandé (« donne-moi le logo X », « j'ai besoin du logo de… »)

1. Trouver le logo : `python3 scripts/donner_logo.py <mots-clés, élément ou id> --lister`
   (recherche sans accents dans id + élément + variante + catégorie + description ; ex. `chu paysage`, `croissant rouge`, `armoiries`). Un nom d'élément exact (`ministere-sante`, `chu-mohammed-vi`…) liste toutes ses variantes.
2. **Une seule correspondance** → la remettre directement, sans question :
   ```bash
   python3 scripts/donner_logo.py <id> --sortie <dossier de travail>
   ```
   puis envoyer le chemin imprimé avec **SendUserFile** (`display: "render"` pour qu'il le voie, il peut le télécharger depuis la carte).
   Le fichier remis est **toujours un PNG à fond transparent**, nommé `<id>.png`.
3. **Plusieurs correspondances** (code retour 2) → c'est fréquent : **un même élément a souvent plusieurs variantes** (l'utilisateur garde plusieurs versions du même organisme : emblème seul, vertical, horizontal, bandeau d'en-tête, ancien/nouveau nom, langue…). Ne jamais choisir à sa place :
   - relancer avec `--apercu` → `apercu-variantes.png` (planche numérotée des variantes) ; l'envoyer avec SendUserFile (`display: "render"`) ;
   - demander laquelle avec AskUserQuestion (jusqu'à 4 options : libellé = variante, description = format/taille) ; au-delà de 4, demander le numéro sur la planche ;
   - si la recherche couvre plusieurs éléments (ex. « CHU » → CHU Mohammed VI + Hôpital Ibn Tofail), demander d'abord l'élément puis la variante — ou proposer directement les meilleures si c'est clair.
   Puis étape 2. Si l'utilisateur dit « tous » / « toutes les versions », remettre chaque variante.
4. **Aucune correspondance** → le dire en une phrase, indiquer où le chercher — en priorité le site officiel de l'organisme, puis **[vector.ma](https://vector.ma/)** (logos marocains, souvent vectoriels) et **[seeklogo.com](https://seeklogo.com/)** (fichiers `.ai`/SVG) — demander de l'uploader, et proposer de l'ajouter à la bibliothèque (voir « Ajouter un logo »). L'utilisateur tient la liste des logos manquants dans `to-add.md` à la racine de son dépôt GitHub de la skill : si le logo n'y figure pas, lui proposer la ligne à ajouter (format du tableau : `| [ ] | prio | element | variantes | remarque |`).
5. Après la remise, une ligne au plus : proposer SVG/PDF s'ils existent (`--format svg|pdf|tous`) et/ou la version N&B (`--nb`).

Options utiles : `--largeur 800` (redimensionne ; les logos vectoriels sont re-rendus nets même au-delà de la taille stockée), `--nb [gamma]` (gris assombri pour impression N&B, transparence conservée), `--format tous`.

## RÈGLE 2 — Logo à intégrer dans un document

Quand un logo doit aller dans un document (en-tête, attestation, page de garde, formulaire…) et que l'utilisateur n'a pas précisé lequel : **avant de produire**, lui demander s'il veut utiliser le(s) logo(s) déjà stocké(s) ici (proposer 2–3 `id` pertinents) ou son propre fichier. Ne jamais lui redemander d'uploader un logo qui est déjà dans la bibliothèque. S'il a déjà nommé le logo, ne pas redemander.

## Choisir le bon fichier

- **PNG** (tous les logos) : fond transparent, rogné au plus près (marge 1 %), prêt pour Word, PowerPoint, reportlab (`drawImage(..., mask="auto")`), HTML.
- **SVG** : web, Word récent, mise à l'échelle sans perte. **PDF** : insertion vectorielle dans un PDF / LaTeX.
- Toujours conserver le ratio (`px` dans `catalogue.json`).
- Petits PNG (< 400 px : `chu-mohammed-vi-portrait`, `radiologie-ibn-tofail-hit`, `fmpm-uca-encadre`, `ordre-medecins-bandeau`, `region-marrakech-safi-horizontal`, `region-marrakech-safi-embleme`, `region-marrakech-safi-vertical`) → ne pas dépasser ~3 cm imprimés.
- **Impression N&B** : `donner_logo.py <id> --nb` — sans assombrissement, l'or des armoiries et le vert clair du MS disparaissent (conversion par luminance : jaune ≈ blanc). Versions N&B à fond blanc des 3 logos de formulaires : `assets/nb/`. Variantes N&B MSPS déjà prêtes au catalogue (fond transparent, mêmes gris que le formulaire cessation/reprise) : `ms-embleme-nb`, `msps-logo-vertical-nb` (SVG/PDF/PNG), `msps-logo-horizontal-nb` (PNG).
- Nom du ministère : depuis 2021 **Ministère de la Santé et de la Protection Sociale** (MSPS). `ms-entete-royaume-bleu` porte l'ancien nom — seulement pour reproduire un document ancien.
- En-tête administratif marocain : français à gauche, armoiries au centre, arabe à droite.
- Cas particuliers : `drapeau-maroc` et `drapeau-region-marrakech-safi` sont des rectangles pleins (pas de transparence, c'est voulu) ; `armoiries-maroc-filigrane` est volontairement très pâle (fond de page) ; `ministere-jeunesse-culture-communication` est blanc → sur fond sombre uniquement ; `fmpm-uca-encadre` garde son cartouche blanc arrondi.

## Catalogue

Chaque entrée = un **élément** (organisme) + une **variante** ; un élément peut avoir plusieurs variantes. Fichiers : `assets/logos/<categorie>/<id>.<format>` — index machine `assets/catalogue.json`, planche visuelle étiquetée `assets/catalogue.png`. Sources : sites officiels, [vector.ma](https://vector.ma/), [seeklogo.com](https://seeklogo.com/), Wikimedia, fichiers de l'utilisateur.

### Royaume du Maroc

| Élément | Variante | id | Formats |
|---|---|---|---|
| armoiries-maroc | couleur | `armoiries-maroc` | svg, pdf, png 1719x1752 |
| armoiries-maroc | filigrane pâle | `armoiries-maroc-filigrane` | png 900x920 |
| armoiries-maroc | en-tête armoiries + texte trilingue | `royaume-maroc-entete-ar-fr-tifinagh` | png 703x261 |
| drapeau-maroc | standard | `drapeau-maroc` | svg, pdf, png 2000x1300 |
| carte-maroc | silhouette | `carte-maroc` | svg, pdf, png 1657x1761 |
| carte-maroc | 12 régions | `carte-maroc-regions` | svg, pdf, png 1656x1760 |
| carte-maroc | avec étoile | `carte-maroc-etoile` | png 1955x2043 |

### Région Marrakech-Safi / Ville de Marrakech

| Élément | Variante | id | Formats |
|---|---|---|---|
| region-marrakech-safi | emblème seul | `region-marrakech-safi-embleme` | png 336x366 |
| region-marrakech-safi | vertical ar/fr | `region-marrakech-safi-vertical` | png 341x428 |
| region-marrakech-safi | horizontal trilingue | `region-marrakech-safi-horizontal` | png 297x77 |
| drapeau-region-marrakech-safi | standard | `drapeau-region-marrakech-safi` | svg, pdf, png 2000x1333 |
| armoiries-ville-marrakech | grandes armoiries | `armoiries-ville-marrakech` | svg, pdf, png 822x1600 |

### Ministère de la Santé (MS / MSPS)

| Élément | Variante | id | Formats |
|---|---|---|---|
| ministere-sante | emblème seul | `ms-embleme` | svg, pdf, png 1194x1092 |
| ministere-sante | vertical trilingue | `msps-logo-vertical` | svg, pdf, png 1736x1415 |
| ministere-sante | horizontal trilingue | `msps-logo-horizontal` | png 875x199 |
| ministere-sante | bandeau Royaume, ancien nom | `ms-entete-royaume-bleu` | png 1564x288 |
| ministere-sante | bandeau Royaume + MSPS | `msps-entete-royaume` | png 1209x193 |
| ministere-sante | emblème seul — noir & blanc | `ms-embleme-nb` | svg, pdf, png 1020x932 |
| ministere-sante | vertical trilingue — noir & blanc | `msps-logo-vertical-nb` | svg, pdf, png 1655x1349 |
| ministere-sante | horizontal trilingue — noir & blanc | `msps-logo-horizontal-nb` | png 875x199 |

### CHU Mohammed VI Marrakech

| Élément | Variante | id | Formats |
|---|---|---|---|
| chu-mohammed-vi | vertical grand | `chu-mohammed-vi-embleme` | png 724x863 |
| chu-mohammed-vi | horizontal | `chu-mohammed-vi-paysage` | png 1004x498 |
| chu-mohammed-vi | bandeau Royaume + MSPS + CHU | `chu-mohammed-vi-entete-msps` | png 1044x202 |
| chu-mohammed-vi | portrait petit | `chu-mohammed-vi-portrait` | png 163x246 |
| hopital-ibn-tofail | en-tête | `hopital-ibn-tofail-entete` | png 690x141 |
| hopital-ibn-tofail | service imagerie HIT | `radiologie-ibn-tofail-hit` | png 189x67 |

### FMPM / Université Cadi Ayyad

| Élément | Variante | id | Formats |
|---|---|---|---|
| fmpm | palmes + texte, horizontal | `fmpm-uca-couleur` | png 1709x696 |
| fmpm | texte bleu seul | `fmpm-texte-bleu` | png 1744x899 |
| fmpm | cartouche arrondi | `fmpm-uca-encadre` | png 345x159 |
| universite-cadi-ayyad | vertical | `uca-universite-cadi-ayyad` | svg, pdf, png 949x1191 |

### Associations médicales (Marrakech)

| Élément | Variante | id | Formats |
|---|---|---|---|
| almoquim | badge rond | `almoquim-association-medecins-residents-marrakech` | svg, pdf, png 2000x2000 |
| amima | badge rond | `amima-association-medecins-internes-marrakech` | svg, pdf, png 2000x2000 |

### International

| Élément | Variante | id | Formats |
|---|---|---|---|
| oms | français | `oms-fr` | svg, png 2612x700 |
| oms | anglais | `who-en` | svg, pdf, png 1199x385 |

### Organismes de santé

| Élément | Variante | id | Formats |
|---|---|---|---|
| ordre-medecins | emblème doré | `ordre-medecins-embleme` | svg, pdf, png 1202x1204 |
| ordre-medecins | bandeau ar/fr | `ordre-medecins-bandeau` | png 586x81 |
| croissant-rouge-marocain | standard | `croissant-rouge-marocain` | svg, pdf, png 1190x1190 |
| ligue-lutte-tuberculose | standard | `ligue-lutte-tuberculose` | svg, pdf, png 1199x852 |
| centre-transfusion-sanguine | générique | `cts-centre-transfusion-sanguine` | svg, pdf, png 1160x1224 |
| centre-transfusion-sanguine | Errachidia | `cts-errachidia` | svg, pdf, png 930x1205 |
| fondation-mohammed-v | standard | `fondation-mohammed-v` | svg, pdf, png 560x1201 |

### Militaire

| Élément | Variante | id | Formats |
|---|---|---|---|
| far | écusson | `far-forces-armees-royales` | svg, pdf, png 725x1185 |
| hopital-militaire-marrakech | écusson + texte | `hopital-militaire-marrakech` | png 928x417 |
| hopital-militaire-marrakech | avec anneaux | `hopital-militaire-marrakech-v2` | png 919x455 |

### Autres

| Élément | Variante | id | Formats |
|---|---|---|---|
| faculte-pharmacie-paris-saclay | standard | `faculte-pharmacie-paris-saclay` | svg, png 2040x397 |
| banque-populaire | standard | `banque-populaire` | svg, pdf, png 1202x593 |
| ministere-transition-numerique | en-tête | `ministere-transition-numerique` | svg, png 1629x603 |
| ministere-jeunesse-culture-communication | blanc, fond sombre | `ministere-jeunesse-culture-communication` | svg, png 1632x592 |

## Optimisation appliquée (et pour tout nouveau logo)

`python3 scripts/optimiser_logo.py entree.(png|jpg) sortie.png [--sans-enclaves] [--garder-fond]`
- Fond = blanc connecté aux bords (baguette magique) + petites enclaves blanches (< 2 % de l'image = intérieur des lettres A, O, R…) → transparent. Grandes zones blanches enclavées (cartouche, anneau) conservées. `--sans-enclaves` si le logo est posé sur un cartouche blanc.
- Bords : « couleur vers alpha » avec seuil → plus de halo blanc sur fond coloré, et les traits gris/colorés fins restent opaques. Halos des PNG déjà détourés nettoyés aussi.
- Rognage sur le contenu + marge 1 %, PNG RGBA optimisé. JPG convertis en PNG.
- SVG : rectangle de fond blanc pleine page supprimé (ex. UCA), PDF régénéré.

## Ajouter un logo à la bibliothèque

Sources où chercher (dans cet ordre) : site officiel de l'organisme (version à jour) → [vector.ma](https://vector.ma/) → [seeklogo.com](https://seeklogo.com/) (téléchargements « vector » = `.ai`, convertibles) → Wikimedia Commons. Préférer SVG/AI/EPS/PDF, sinon PNG ≥ 1000 px.

**Logo à aplats de couleurs sans version vectorielle** : `python3 scripts/vectoriser_logo.py entree.png sortie.svg --palette hex1,hex2,… [--cercle] [--anti-halo] [--png 2000]` — ramène chaque pixel à la palette, nettoie les mouchetures, trace en courbes (vtracer) ; `--cercle` = contour en cercle parfait pour les badges ; `--anti-halo` évite un liseré clair autour d'un texte foncé. Écrit SVG + PDF + PNG. Toujours comparer le rendu à l'original (planche côte à côte) avant d'ajouter ; noter « vectorisé (tracé) » dans la description. Ne convient pas aux logos à dégradés / photos (armoiries détaillées) : garder le PNG.

**Petit raster seulement disponible** (≤ 500 px, ex. capture d'écran Facebook) : `python3 scripts/agrandir_logo.py entree.jpg sortie.png [--cercle CX CY R]` — super-résolution EDSR ×4 (bords nets, artefacts JPEG atténués) ; `--cercle` pour les badges ronds (fond hors du cercle transparent, intérieur du badge conservé). Indiquer « agrandi ×4 » dans la description et garder la ligne « version vectorielle » dans `TO-ADD.md`.

1. `.ai` (Illustrator) = généralement un PDF : `pdftocairo -svg`, `-pdf`, `-png -transp` (rogner via `-x -y -W -H`). Raster : `optimiser_logo.py`.
2. **Nouvelle variante d'un élément existant** (cas le plus courant) : réutiliser son `element` exact, choisir une `variante` courte et distinctive (ex. « vertical bleu », « bandeau 2024 », « arabe seul ») et un `id` = `<element>-<variante-en-slug>`. Vérifier d'abord avec `--apercu` que ce n'est pas un doublon visuel d'une variante déjà présente (même dessin, simple différence de taille → garder la meilleure résolution, ne pas ajouter).
   **Nouvel élément** : nouvel `element` en slug (nom de l'organisme).
   Fichiers : `assets/logos/<categorie>/<id>.<ext>` ; entrée dans `catalogue.json` (`element`, `variante`, `id`, `categorie`, `description`, `fichiers` avec `px` pour le PNG).
3. Régénérer `catalogue.png` (`python3 scripts/planche_catalogue.py`), mettre à jour le tableau ci-dessus et celui du `README.md`, cocher la ligne correspondante dans `to-add.md` du dépôt et la déplacer dans « Fait », puis repackager : `./build.sh` à la racine du dépôt (vérifie que `assets/`, `catalogue.json`, `SKILL.md` et `README.md` listent les mêmes logos, puis crée `dist/logos-officiels-maroc.zip`).

## Formulaires prêts (A4, vectoriels, optimisés impression N&B)

```bash
python3 scripts/formulaire_cessation_reprise.py sortie.pdf   # 2 pages : 2× cessation, 2× reprise (ligne de coupe)
python3 scripts/formulaire_note_stage.py sortie.pdf          # Note de stage de 5ème année (SRES Marrakech)
```

Dépendances : `pip install --break-system-packages reportlab arabic-reshaper python-bidi cairosvg scipy pillow`.
Polices : Liberation Serif (latin) et FreeSerif (arabe) — `/usr/share/fonts/truetype/{liberation,freefont}/`.
Arabe avec reportlab : toujours `get_display(arabic_reshaper.reshape(texte))`, sinon lettres détachées et inversées.
Fidélité aux originaux scannés : textes, ordre et en-têtes conservés ; seules corrections : « cessaion » → « cessation », « المؤسسات الصحة » → « المؤسسات الصحية ». Ne pas ajouter de tableau à la note de stage sans demande explicite.
