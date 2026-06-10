import os

from fastapi import APIRouter

import config

routeur = APIRouter()


def construire_arbre(racine):
    dossiers = []
    fichiers = []
    if os.path.isdir(racine):
        for nom in sorted(os.listdir(racine)):
            if nom.startswith("."):
                continue
            chemin = os.path.join(racine, nom)
            if os.path.isdir(chemin):
                dossiers.append(construire_arbre(chemin))
            else:
                fichiers.append(nom)
    relatif = os.path.relpath(racine, config.DOSSIER_DOCS)
    return {
        "nom": os.path.basename(racine),
        "chemin": "" if relatif == "." else relatif.replace(os.sep, "/"),
        "dossiers": dossiers,
        "fichiers": fichiers,
    }


@routeur.get("/arborescence")
def arborescence():
    return construire_arbre(config.DOSSIER_DOCS)
