import os

DOSSIER_DOCS = os.environ.get("GED_DOCS", "documents")
DOSSIER_BASE = os.environ.get("GED_VECTOR_STORE", "vector_store")
NOM_COLLECTION = os.environ.get("GED_COLLECTION", "connaissance")

EMBED_MODEL = os.environ.get("GED_EMBED_MODEL", "nomic-embed-text")
LLM_MODEL = os.environ.get("GED_LLM_MODEL", "mistral")
VISION_MODEL = os.environ.get("GED_VISION_MODEL", "llava")
WHISPER_MODEL = os.environ.get("GED_WHISPER_MODEL", "base")
WHISPER_DEVICE = os.environ.get("GED_WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE = os.environ.get("GED_WHISPER_COMPUTE", "int8")

TAILLE_CHUNK = int(os.environ.get("GED_TAILLE_CHUNK", "800"))
CHEVAUCHEMENT = int(os.environ.get("GED_CHEVAUCHEMENT", "150"))
N_RESULTATS = int(os.environ.get("GED_N_RESULTATS", "4"))
TEMPERATURE = float(os.environ.get("GED_TEMPERATURE", "0.1"))

NB_IMAGES_VIDEO = int(os.environ.get("GED_NB_IMAGES_VIDEO", "4"))

EXTENSIONS_IMAGE = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp")
EXTENSIONS_AUDIO = (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac", ".wma")
EXTENSIONS_VIDEO = (".mp4", ".mkv", ".avi", ".mov", ".webm", ".m4v", ".mpeg", ".mpg")
