"""Vérifie que assets/, catalogue.json, SKILL.md et README.md décrivent les mêmes logos.

Outil du dépôt (hors skill) — lancé par ./build.sh.

Usage :
  python3 outils/verifier_catalogue.py      # code 1 + liste des écarts s'il y en a

Contrôles :
  - chaque fichier cité dans assets/catalogue.json existe, est nommé <id>.<format>
    et rangé dans assets/logos/<categorie>/ ; chaque entrée a un PNG ;
  - aucun fichier de assets/logos/ n'est absent du catalogue ;
  - chaque id du catalogue figure dans les tableaux de SKILL.md et de README.md ;
  - le nombre annoncé (« bibliothèque de N logos ») dans SKILL.md et README.md est le bon.
"""
import json, os, re, sys

RACINE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CAT = json.load(open(os.path.join(RACINE, "assets", "catalogue.json"), encoding="utf-8"))


def erreurs():
    out, cites = [], set()
    for e in CAT:
        for f in e["fichiers"]:
            cites.add(f["fichier"])
            if not os.path.exists(os.path.join(RACINE, f["fichier"])):
                out.append(f"fichier manquant : {f['fichier']}")
            if f["fichier"] != f"assets/logos/{e['categorie']}/{e['id']}.{f['format']}":
                out.append(f"chemin inattendu pour {e['id']} : {f['fichier']}")
        if not any(f["format"] == "png" for f in e["fichiers"]):
            out.append(f"pas de PNG pour {e['id']}")
    for r, _, fs in os.walk(os.path.join(RACINE, "assets", "logos")):
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), RACINE)
            if rel not in cites:
                out.append(f"fichier hors catalogue : {rel}")
    for doc in ("SKILL.md", "README.md"):
        texte = open(os.path.join(RACINE, doc), encoding="utf-8").read()
        out += [f"{doc} : id absent des tableaux : {e['id']}" for e in CAT if f"| `{e['id']}` |" not in texte]
        out += [f"{doc} : annonce {n} logos, le catalogue en a {len(CAT)}"
                for n in re.findall(r"[Bb]iblioth[eè]que de \**(\d+) logos", texte) if int(n) != len(CAT)]
    return out


def main():
    err = erreurs()
    for x in err:
        print("ERREUR", x)
    if err:
        sys.exit(1)
    print(f"OK : {len(CAT)} logos, assets/ = catalogue.json = SKILL.md = README.md")


if __name__ == "__main__":
    main()
