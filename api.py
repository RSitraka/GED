import os
import shutil

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import apercu
import arborescence
import config
import ingestion
import rag

app = FastAPI(title="Mon NotebookLM privé")
app.include_router(arborescence.routeur)
app.include_router(apercu.routeur)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


class Question(BaseModel):
    texte: str
    categorie: str | None = None
    insister: bool | None = None


@app.post("/demander")
def demander(q: Question):
    reponse, sources = rag.repondre(q.texte, categorie=q.categorie, insister=q.insister)
    return {"reponse": reponse, "sources": sources}


@app.post("/televerser")
def televerser(categorie: str, fichier: UploadFile = File(...)):
    dossier = os.path.join(config.DOSSIER_DOCS, categorie)
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, fichier.filename)
    with open(chemin, "wb") as f:
        shutil.copyfileobj(fichier.file, f)
    ingestion.ingerer()
    return {"message": f"{fichier.filename} ajouté à {categorie}."}


@app.get("/categories")
def categories():
    metas = rag.collection.get()["metadatas"]
    cats = sorted({m["categorie"] for m in metas if m})
    return {"categories": cats}


@app.get("/", response_class=HTMLResponse)
def page_chat():
    with open("chat.html", encoding="utf-8") as f:
        return f.read()
