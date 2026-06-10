import ollama

import config
import ingestion

collection = ingestion.ouvrir_collection()

GABARIT = """Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni.
Le contexte contient plusieurs passages séparés par "---" ; certains peuvent être hors sujet.
Sers-toi UNIQUEMENT des passages qui concernent directement la question et ignore les autres.
Ne résume pas le contexte : réponds précisément et seulement à la question posée.
Entoure OBLIGATOIREMENT de doubles astérisques les éléments précis qui répondent
concrètement à la question : chiffres, montants, dates, délais, pourcentages, noms propres.
Exemple de format attendu (sans guillemets autour de la réponse) :
Le délai de paiement est de **30 jours** et un escompte de **2 %** s'applique sous **8 jours**.
Si la réponse ne figure dans aucun passage pertinent, réponds exactement :
"Je n'ai pas cette information dans les documents fournis."
Ne fais aucune supposition. Réponds en français, clairement et brièvement.

Contexte :
{contexte}

Question : {question}

Réponse (avec chaque élément clé entouré de **doubles astérisques**) :"""


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


def _essayer(question, categorie, n, seuil):
    morceaux, sources = chercher(question, n=n, categorie=categorie, seuil=seuil)
    if not morceaux:
        return "Je n'ai pas cette information dans les documents fournis.", []
    contexte = "\n\n---\n\n".join(morceaux)
    prompt = GABARIT.format(contexte=contexte, question=question)
    reponse = ollama.chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": config.TEMPERATURE},
    )
    texte = reponse["message"]["content"]
    if _sans_reponse(texte):
        return texte, []
    noms = sorted({s["source"] for s in sources})
    return texte, noms


def repondre(question, categorie=None, insister=None):
    if insister is None:
        insister = config.INSISTER
    texte, noms = _essayer(question, categorie, config.N_RESULTATS, config.SEUIL_PERTINENCE)
    if insister and _sans_reponse(texte):
        texte, noms = _essayer(question, None, config.N_INSISTANCE, config.SEUIL_INSISTANCE)
    return texte, noms


if __name__ == "__main__":
    question = input("Votre question : ")
    reponse, sources = repondre(question)
    print("\n" + reponse)
    print("\nSources :", ", ".join(sources) if sources else "aucune")
