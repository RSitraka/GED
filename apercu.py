import mimetypes
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

import config
import extraction
import ingestion

routeur = APIRouter()


def _chemin_sur(chemin):
    base = os.path.abspath(config.DOSSIER_DOCS)
    cible = os.path.abspath(os.path.join(base, chemin))
    if cible != base and not cible.startswith(base + os.sep):
        raise HTTPException(status_code=403, detail="Chemin non autorisé")
    if not os.path.isfile(cible):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    return cible


@routeur.get("/apercu")
def apercu(chemin: str):
    cible = _chemin_sur(chemin)
    type_mime = mimetypes.guess_type(cible)[0] or "application/octet-stream"
    return FileResponse(cible, media_type=type_mime, content_disposition_type="inline")


@routeur.get("/lire")
def lire(chemin: str):
    cible = _chemin_sur(chemin)
    parse = ingestion.chemin_parse(cible)
    if os.path.isfile(parse):
        with open(parse, encoding="utf-8", errors="ignore") as fichier:
            return PlainTextResponse(fichier.read())
    texte = extraction.extraire_texte(cible)
    return PlainTextResponse(texte or "(Aucun texte lisible n'a pu être extrait de ce fichier.)")
