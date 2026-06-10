window.categorieFiltre = null;

function iconePour(nom){
  const ext = nom.toLowerCase().split(".").pop();
  if(ext === "pdf") return "📕";
  if(["doc","docx","odt","rtf"].includes(ext)) return "📘";
  if(["xls","xlsx","xlsm","ods","csv"].includes(ext)) return "📊";
  if(["ppt","pptx","odp"].includes(ext)) return "📙";
  if(["png","jpg","jpeg","gif","bmp","tif","tiff","webp","svg"].includes(ext)) return "🖼️";
  if(["mp3","wav","m4a","flac","ogg","aac","wma"].includes(ext)) return "🎵";
  if(["mp4","mkv","avi","mov","webm","m4v","mpeg","mpg"].includes(ext)) return "🎬";
  if(["html","htm"].includes(ext)) return "🌐";
  if(["json","xml","yaml","yml"].includes(ext)) return "🔧";
  if(["zip","rar","7z","tar","gz"].includes(ext)) return "🗜️";
  if(["md","markdown"].includes(ext)) return "📝";
  return "📄";
}

function definirFiltre(chemin, element){
  window.categorieFiltre = chemin || null;
  document.querySelectorAll("#arbo .btnFiltre").forEach(b => b.classList.remove("actif"));
  if(element) element.classList.add("actif");
  const label = document.getElementById("filtreActif");
  label.textContent = window.categorieFiltre
    ? "Filtre : " + window.categorieFiltre
    : "Filtre : toutes les catégories";
  const cible = document.getElementById("catUpload");
  if(cible) cible.value = window.categorieFiltre || "general";
}

function rendreNoeud(noeud, racine){
  const details = document.createElement("details");
  details.open = true;
  if(racine) details.className = "racine";

  const summary = document.createElement("summary");
  const nom = document.createElement("span");
  nom.className = "nomDossier";
  nom.textContent = racine ? "documents" : noeud.nom;
  summary.appendChild(nom);

  const filtrer = document.createElement("span");
  filtrer.className = "btnFiltre";
  filtrer.textContent = "⌖";
  filtrer.title = "Filtrer la recherche sur ce dossier";
  filtrer.onclick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    definirFiltre(noeud.chemin, filtrer);
  };
  summary.appendChild(filtrer);
  details.appendChild(summary);

  const enfants = document.createElement("div");
  enfants.className = "enfants";
  for(const sous of noeud.dossiers){
    enfants.appendChild(rendreNoeud(sous, false));
  }
  for(const fichier of noeud.fichiers){
    const ligne = document.createElement("div");
    ligne.className = "fichier";
    ligne.textContent = iconePour(fichier) + " " + fichier;
    const chemin = (noeud.chemin ? noeud.chemin + "/" : "") + fichier;
    ligne.title = "Aperçu : " + fichier;
    ligne.onclick = () => { if(window.apercu) window.apercu(chemin, fichier); };
    enfants.appendChild(ligne);
  }
  details.appendChild(enfants);
  return details;
}

async function chargerArbre(){
  try{
    const reponse = await fetch("/arborescence");
    const arbre = await reponse.json();
    const conteneur = document.getElementById("arbo");
    conteneur.innerHTML = "";
    conteneur.appendChild(rendreNoeud(arbre, true));
    definirFiltre(window.categorieFiltre, null);
    remplirCategories(arbre);
  }catch(e){}
}

function remplirCategories(arbre){
  const liste = document.getElementById("listeCategories");
  if(!liste) return;
  const chemins = [];
  (function parcourir(noeud){
    if(noeud.chemin) chemins.push(noeud.chemin);
    noeud.dossiers.forEach(parcourir);
  })(arbre);
  liste.innerHTML = "";
  for(const chemin of chemins.sort()){
    const option = document.createElement("option");
    option.value = chemin;
    liste.appendChild(option);
  }
}

window.chargerArbre = chargerArbre;
chargerArbre();
