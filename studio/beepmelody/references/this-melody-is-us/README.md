# Référence de Guillaume : « This Melody Is Us » (la vidéo qui a donné l'idée de la chaîne)

Fichiers : `this_melody_is_us.mp4` (copie allégée 540 px, 92 s), `frames.png` (8 images clés).
Rendue par le moteur maison : `studio/this-melody-is/engine/pop4.py` (+ `pi_audio.py` avec `MOD=pop4`, globe = `../geo/land_clean.npy`).
Ce moteur est la base à réutiliser quand le sujet s'y prête (importer ses fonctions ; ne pas modifier le fichier).

## Ce qui la rend forte (à reproduire, pas à copier)
- **Une scène vivante, pas un graphique.** Un globe terrestre en pixel art qui tourne lentement, sur fond d'étoiles.
  La donnée se voit SUR le monde : chaque bip = des gens qui naissent, et un point de lumière s'allume à l'endroit réel
  (Afrique d'abord, puis l'Asie, l'Europe…). Le globe se remplit de lumière au fil du temps.
- **Règle annoncée en 1 phrase dès le début** : « EVERY BIP = PEOPLE BEING BORN », puis « EVERY BOOM = PEOPLE DYING TOO SOON ».
- **Le son suit la densité** : quelques bips isolés au début (préhistoire), puis ça s'accélère jusqu'au mur de son
  (≈ 3 attaques/s au début → ≈ 30/s à la fin). Le rythme EST la donnée.
- **Événements dramatiques** : peste de Justinien, peste noire → écran rouge, gros « boom », cercles d'impact sur la carte,
  étiquette « 75-200 M DEAD ». Glitchs/scanlines au moment fort.
- **HUD discret mais riche** : ère (OUT OF AFRICA, FARMING, CITIES & EMPIRES, THE BLACK DEATH, 1492, INDUSTRY, WARS & PANDEMICS, THE BOOM),
  année en gros, POP, BIRTHS / YEAR ; petite courbe « WORLD POPULATION (LOG) » en bas = repère, pas le sujet.
- **Jalons qui claquent** : « 7 BILLION ! », fin « 8.3 BILLION ALIVE RIGHT NOW », « ≈117 BILLION BORN SINCE THE DAWN OF OUR SPECIES »,
  dernière ligne « EVERY BIP WAS SOMEONE. »
- Durée 92 s (trop longue pour la chaîne : viser 62–75 s).

## Ce qu'il faut éviter (retour de Guillaume, 11 nov.)
Des épisodes qui ne sont que des tableaux / barres / courbes. Le graphe peut rester en petit repère ; le cœur de l'image doit être une scène
(globe, carte, objet, lieu) où chaque note se VOIT arriver quelque part.
