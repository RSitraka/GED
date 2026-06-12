let categoriesDossiers = [];

function rendreListeCategories(chemins){
  const liste = document.getElementById("catListe");
  if(!liste) return;
  liste.innerHTML = "";
  for(const chemin of chemins){
    const item = document.createElement("div");
    item.className = "combo-item";
    item.textContent = chemin;
    item.onclick = () => {
      document.getElementById("catUpload").value = chemin;
      fermerListeCategories();
    };
    liste.appendChild(item);
  }
}

function ouvrirListeCategories(filtre){
  const liste = document.getElementById("catListe");
  if(!liste) return;
  let items = categoriesDossiers;
  if(filtre){
    const bas = filtre.toLowerCase();
    const filtres = categoriesDossiers.filter(c => c.toLowerCase().includes(bas));
    if(filtres.length > 0) items = filtres;
  }
  rendreListeCategories(items);
  if(items.length > 0) liste.classList.add("ouvert");
}

function fermerListeCategories(){
  const liste = document.getElementById("catListe");
  if(liste) liste.classList.remove("ouvert");
}

window.remplirListeCategories = function(chemins){
  categoriesDossiers = chemins;
};

(function brancher(){
  const champ = document.getElementById("catUpload");
  const fleche = document.getElementById("catFleche");
  const liste = document.getElementById("catListe");
  if(!champ || !fleche || !liste) return;
  fleche.onclick = (e) => {
    e.stopPropagation();
    liste.classList.contains("ouvert") ? fermerListeCategories() : ouvrirListeCategories("");
  };
  champ.onfocus = () => ouvrirListeCategories("");
  champ.oninput = () => ouvrirListeCategories(champ.value);
  liste.onclick = (e) => e.stopPropagation();
  document.addEventListener("click", fermerListeCategories);
})();
