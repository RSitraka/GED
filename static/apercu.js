const APERCU_TEXTE = ["txt","md","markdown","log","csv","json","xml","yaml","yml","html","htm","py","js","css","rtf"];
const APERCU_IMAGE = ["png","jpg","jpeg","gif","bmp","webp","svg","tif","tiff"];
const APERCU_AUDIO = ["mp3","wav","m4a","flac","ogg","aac","wma"];
const APERCU_VIDEO = ["mp4","webm","mov","mkv","m4v","avi"];

function apercu(chemin, nom){
  const ext = nom.toLowerCase().split(".").pop();
  const url = "/apercu?chemin=" + encodeURIComponent(chemin);
  const corps = document.getElementById("apercuCorps");
  document.getElementById("apercuTitre").textContent = nom;
  corps.innerHTML = "";

  if(ext === "pdf"){
    const cadre = document.createElement("iframe");
    cadre.src = url;
    corps.appendChild(cadre);
  } else if(APERCU_IMAGE.includes(ext)){
    const img = document.createElement("img");
    img.src = url;
    corps.appendChild(img);
  } else if(APERCU_AUDIO.includes(ext)){
    const audio = document.createElement("audio");
    audio.src = url;
    audio.controls = true;
    corps.appendChild(audio);
  } else if(APERCU_VIDEO.includes(ext)){
    const video = document.createElement("video");
    video.src = url;
    video.controls = true;
    corps.appendChild(video);
  } else if(APERCU_TEXTE.includes(ext)){
    const pre = document.createElement("pre");
    pre.textContent = "Chargement…";
    corps.appendChild(pre);
    fetch(url).then(r => r.text()).then(t => { pre.textContent = t; })
      .catch(() => { pre.textContent = "Aperçu indisponible."; });
  } else {
    const message = document.createElement("p");
    message.className = "apercuMessage";
    message.innerHTML = "Aperçu direct non disponible pour ce type de fichier. "
      + '<a class="apercuLien" href="' + url + '" target="_blank">Ouvrir dans un nouvel onglet</a>';
    corps.appendChild(message);
  }

  document.getElementById("apercuModal").style.display = "flex";
}

function fermerApercu(){
  document.getElementById("apercuModal").style.display = "none";
  document.getElementById("apercuCorps").innerHTML = "";
}

window.apercu = apercu;
window.fermerApercu = fermerApercu;

document.addEventListener("keydown", (e) => {
  if(e.key === "Escape") fermerApercu();
});
