from mcp.server.fastmcp import FastMCP

import rag

mcp = FastMCP("base-de-connaissance")


@mcp.tool()
def chercher_dans_la_base(question: str, categorie: str = "") -> str:
    """Cherche dans la base documentaire et renvoie une réponse fondée
    UNIQUEMENT sur les documents, accompagnée de ses sources.

    question : la question posée par l'utilisateur
    categorie : (optionnel) limiter la recherche à un sous-dossier,
    par exemple "juridique" ou "comptabilite"
    """
    cat = categorie or None
    reponse, sources = rag.repondre(question, categorie=cat)
    liste = ", ".join(sources) if sources else "aucune"
    return f"{reponse}\n\nSources : {liste}"


@mcp.tool()
def lister_categories() -> str:
    """Renvoie la liste des catégories (sous-dossiers) disponibles."""
    metas = rag.collection.get()["metadatas"]
    cats = sorted({m["categorie"] for m in metas if m})
    return ", ".join(cats) if cats else "aucune catégorie"


if __name__ == "__main__":
    mcp.run()
