import mimetypes
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

import config

routeur = APIRouter()


@routeur.get("/apercu")
def apercu(chemin: str):
    base = os.path.abspath(config.DOSSIER_DOCS)
    cible = os.path.abspath(os.path.join(base, chemin))
    if cible != base and not cible.startswith(base + os.sep):
        raise HTTPException(status_code=403, detail="Chemin non autorisé")
    if not os.path.isfile(cible):
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    type_mime = mimetypes.guess_type(cible)[0] or "application/octet-stream"
    return FileResponse(cible, media_type=type_mime, content_disposition_type="inline")
