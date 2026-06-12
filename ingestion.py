import os

import chromadb
import ollama

import config
import extraction


def vectoriser(texte):
    reponse = ollama.embeddings(model=config.EMBED_MODEL, prompt=config.EMBED_PREFIXE_DOC + texte)
    return reponse["embedding"]


def decouper(texte, taille=config.TAILLE_CHUNK, chevauchement=config.CHEVAUCHEMENT):
    mots = texte.split()
    morceaux = []
    debut = 0
    while debut < len(mots):
        fin = debut + taille
        morceaux.append(" ".join(mots[debut:fin]))
        debut = fin - chevauchement
    return morceaux


def ouvrir_collection():
    client = chromadb.PersistentClient(path=config.DOSSIER_BASE)
    return client.get_or_create_collection(config.NOM_COLLECTION)


def chemin_parse(chemin):
    relatif = os.path.relpath(chemin, config.DOSSIER_DOCS)
    return os.path.join(config.DOSSIER_PARSED, relatif + ".txt")


def enregistrer_parse(chemin, texte):
    cible = chemin_parse(chemin)
    os.makedirs(os.path.dirname(cible), exist_ok=True)
    with open(cible, "w", encoding="utf-8") as fichier:
        fichier.write(texte)


def supprimer_parse(chemin):
    cible = chemin_parse(chemin)
    if os.path.isfile(cible):
        os.remove(cible)


def purger_absents(collection):
    donnees = collection.get(include=["metadatas"])
    chemins = {m.get("chemin") for m in donnees["metadatas"] if m}
    for chemin in chemins:
        if chemin and not os.path.exists(chemin):
            collection.delete(where={"chemin": chemin})
            supprimer_parse(chemin)
            print(f"  - {chemin} (supprimé du disque)")


def ingerer():
    collection = ouvrir_collection()
    purger_absents(collection)
    compteur = 0
    for racine, dossiers, fichiers in os.walk(config.DOSSIER_DOCS):
        for nom in fichiers:
            if nom.startswith(".") or "Zone.Identifier" in nom:
                continue
            chemin = os.path.join(racine, nom)
            texte = extraction.extraire_texte(chemin)
            if not texte.strip():
                continue
            categorie = os.path.relpath(racine, config.DOSSIER_DOCS)
            if categorie == ".":
                categorie = "general"
            enregistrer_parse(chemin, texte)
            collection.delete(where={"chemin": chemin})
            morceaux = decouper(texte)
            for i, morceau in enumerate(morceaux):
                collection.add(
                    ids=[f"{chemin}::{i}"],
                    documents=[morceau],
                    embeddings=[vectoriser(morceau)],
                    metadatas=[{"source": nom, "categorie": categorie, "chemin": chemin}],
                )
            compteur += len(morceaux)
            print(f"  + {chemin} ({len(morceaux)} morceaux)")
    print(f"Terminé : {compteur} morceaux indexés.")


if __name__ == "__main__":
    ingerer()
