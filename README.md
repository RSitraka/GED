# Mon NotebookLM privé (RAG local)

Base de connaissance RAG locale + agent IA qui répond uniquement à partir de vos
documents. Prend en charge texte, PDF, Office, images (OCR + vision), audio et vidéo.

Pile : Python · Ollama (Mistral + nomic-embed-text + llava) · ChromaDB · FastAPI · MCP · Cloudflare Tunnel.

## 1. Prérequis

- **Python 3.11+** (sur Windows, cocher « Add Python to PATH »).
- **Ollama** : https://ollama.com
- Audio et vidéo fonctionnent sans outil système (PyAV + faster-whisper embarqués).
- **Tesseract OCR** (`apt install tesseract-ocr tesseract-ocr-fra`) : facultatif, améliore
  la lecture du texte dans les images ; le modèle de vision `llava` le lit déjà sans lui.
- **poppler-utils** : facultatif, OCR des PDF scannés.

Télécharger les modèles :

```
ollama pull mistral
ollama pull nomic-embed-text
ollama pull llava
```

## 2. Installation

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
```

## 3. Formats pris en charge

| Catégorie | Extensions | Traitement |
|-----------|------------|------------|
| Texte | txt, md, log, xml, yaml, json | lecture directe |
| Documents | pdf, docx, pptx, xlsx, csv, html, rtf | extraction de texte (OCR si PDF scanné) |
| Images | jpg, png, gif, bmp, tiff, webp | OCR (Tesseract) + description (modèle vision) |
| Audio | mp3, wav, m4a, flac, ogg, aac | transcription (faster-whisper) |
| Vidéo | mp4, mkv, avi, mov, webm, m4v | transcription audio + description d'images clés |

Les fonctionnalités image/audio/vidéo se désactivent silencieusement si la
dépendance correspondante (Tesseract, modèle vision `llava`) est absente ; le reste
continue de fonctionner. La vidéo est décodée par PyAV, sans binaire ffmpeg.

## 4. Utilisation

Rangez vos fichiers dans `documents/<categorie>/` puis indexez :

```
python ingestion.py
```

Tester le moteur en console :

```
python rag.py
```

Tester les outils MCP :

```
mcp dev mcp_server.py
```

Lancer l'application web :

```
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

Ouvrir http://localhost:8000 (chat) ou http://localhost:8000/docs (API).

## 5. Accès en ligne

```
cloudflared tunnel --url http://localhost:8000
```

## 6. Réglages

Tout est centralisé dans `config.py` et surchargeable par variables d'environnement
(`GED_LLM_MODEL`, `GED_EMBED_MODEL`, `GED_VISION_MODEL`, `GED_WHISPER_MODEL`,
`GED_N_RESULTATS`, `GED_TAILLE_CHUNK`, etc.).

## 7. Architecture modulaire (une fonctionnalité = un fichier)

Chaque nouvelle fonctionnalité vit dans son propre fichier pour garder le code léger :

- Backend : un module exposant un `APIRouter`, inclus dans `api.py` via
  `app.include_router(...)`. Exemple : `arborescence.py` → endpoint `/arborescence`.
- Front-end : un script dans `static/`, chargé par `chat.html`. Exemple :
  `static/arborescence.js` (panneau latéral repliable + filtre par dossier).

`api.py` reste ainsi le simple point d'assemblage des fonctionnalités.
