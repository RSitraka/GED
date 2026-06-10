import os

import ollama

import config
import ingestion

collection = ingestion.ouvrir_collection()

GABARIT = """Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni.
Le contexte contient des passages numérotés ; chaque passage commence par son numéro et son
fichier source, par exemple "[2] (tva.txt)".
Sers-toi UNIQUEMENT des passages qui concernent directement la question et ignore les autres.
Ne résume pas le contexte : réponds précisément et seulement à la question posée.
Après CHAQUE information, indique entre crochets le numéro du passage d'où elle vient : [1], [2]...
N'invente aucun numéro : n'utilise que ceux réellement présents dans le contexte.
Entoure de doubles astérisques les éléments précis : chiffres, montants, dates, délais, pourcentages, noms propres.
Exemple : Le délai de paiement est de **30 jours** [1] et un escompte de **2 %** s'applique sous **8 jours** [1].
Si la réponse ne figure dans aucun passage pertinent, réponds exactement :
"Je n'ai pas cette information dans les documents fournis."
Ne fais aucune supposition. Réponds en français, clairement et brièvement.

Contexte :
{contexte}

Question : {question}

Réponse (avec citations [n] et éléments clés en **gras**) :"""


def chercher(question, n=config.N_RESULTATS, categorie=None, seuil=config.SEUIL_PERTINENCE):
    vecteur = ollama.embeddings(
        model=config.EMBED_MODEL,
        prompt=config.EMBED_PREFIXE_REQUETE + question,
    )["embedding"]
    filtre = {"categorie": categorie} if categorie else None
    resultats = collection.query(
        query_embeddings=[vecteur],
        n_results=n,
        where=filtre,
        include=["documents", "metadatas", "distances"],
    )
    morceaux = resultats["documents"][0]
    sources = resultats["metadatas"][0]
    distances = resultats["distances"][0]
    if not morceaux:
        return [], []
    limite = distances[0] * (1 + seuil)
    gardes_m = []
    gardes_s = []
    for morceau, source, distance in zip(morceaux, sources, distances):
        if distance <= limite:
            gardes_m.append(morceau)
            gardes_s.append(source)
    return gardes_m, gardes_s


def _sans_reponse(texte):
    return "Je n'ai pas cette information" in texte


def _extrait(morceau, maxi=600):
    texte = morceau.strip()
    if len(texte) > maxi:
        return texte[:maxi].rstrip() + "…"
    return texte


def _references(morceaux, sources):
    references = []
    for numero, (morceau, source) in enumerate(zip(morceaux, sources), start=1):
        chemin = source.get("chemin", "")
        relatif = ""
        if chemin:
            relatif = os.path.relpath(chemin, config.DOSSIER_DOCS).replace(os.sep, "/")
        references.append({
            "numero": numero,
            "source": source.get("source", ""),
            "chemin": relatif,
            "extrait": _extrait(morceau),
        })
    return references


def _essayer(question, categorie, n, seuil):
    morceaux, sources = chercher(question, n=n, categorie=categorie, seuil=seuil)
    if not morceaux:
        return "Je n'ai pas cette information dans les documents fournis.", []
    references = _references(morceaux, sources)
    contexte = "\n\n---\n\n".join(
        f"[{r['numero']}] ({r['source']})\n{m}" for r, m in zip(references, morceaux)
    )
    prompt = GABARIT.format(contexte=contexte, question=question)
    reponse = ollama.chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": config.TEMPERATURE},
    )
    texte = reponse["message"]["content"]
    if _sans_reponse(texte):
        return "Je n'ai pas cette information dans les documents fournis.", []
    return texte.strip(), references


def repondre(question, categorie=None, insister=None):
    if insister is None:
        insister = config.INSISTER
    texte, references = _essayer(question, categorie, config.N_RESULTATS, config.SEUIL_PERTINENCE)
    if insister and _sans_reponse(texte):
        texte, references = _essayer(question, None, config.N_INSISTANCE, config.SEUIL_INSISTANCE)
    return texte, references


if __name__ == "__main__":
    question = input("Votre question : ")
    reponse, references = repondre(question)
    print("\n" + reponse)
    noms = sorted({r["source"] for r in references})
    print("\nSources :", ", ".join(noms) if noms else "aucune")
