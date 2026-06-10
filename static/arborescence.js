window.categorieFiltre = null;

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
    ligne.textContent = "📄 " + fichier;
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
  }catch(e){}
}

window.chargerArbre = chargerArbre;
chargerArbre();
