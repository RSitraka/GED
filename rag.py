import ollama

import config
import ingestion

collection = ingestion.ouvrir_collection()

GABARIT = """Tu es un assistant qui répond UNIQUEMENT à partir du contexte fourni.
Si la réponse ne figure pas dans le contexte, réponds exactement :
"Je n'ai pas cette information dans les documents fournis."
Ne fais aucune supposition. Réponds en français, clairement et brièvement.

Contexte :
{contexte}

Question : {question}

Réponse :"""


def chercher(question, n=config.N_RESULTATS, categorie=None):
    vecteur = ollama.embeddings(model=config.EMBED_MODEL, prompt=question)["embedding"]
    filtre = {"categorie": categorie} if categorie else None
    resultats = collection.query(query_embeddings=[vecteur], n_results=n, where=filtre)
    morceaux = resultats["documents"][0]
    sources = resultats["metadatas"][0]
    return morceaux, sources


def repondre(question, categorie=None):
    morceaux, sources = chercher(question, categorie=categorie)
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
    noms = sorted({s["source"] for s in sources})
    return texte, noms


if __name__ == "__main__":
    question = input("Votre question : ")
    reponse, sources = repondre(question)
    print("\n" + reponse)
    print("\nSources :", ", ".join(sources) if sources else "aucune")
