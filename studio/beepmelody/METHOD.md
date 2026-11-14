# BeepMelody — méthode de production d'un épisode

BeepMelody = chaîne anglophone de shorts **data + musique, sans voix** (pixel art, 1080×1920, 30 fps).
Une vidéo = un phénomène, une période ou une série d'événements qu'on **entend** : chaque événement de la donnée
est une note, donc l'image et le son restent synchrones par construction. Public visé : curieux, attention courte (TDAH).

Format du registre : `data-sonification` (`studio/FORMATS.json`). Moteur réutilisé tel quel :
`studio/this-melody-is/engine` (v2.py, pi.py, pi_audio.py). **On ne modifie pas ces fichiers** ; tout ce qui est
propre à BeepMelody vit dans `studio/beepmelody/episodes/`.

## Référence d'inspiration (Guillaume, 11 nov.) — `studio/beepmelody/references/this-melody-is-us/`
La vidéo « This Melody Is Us » (moteur `pop4.py`) est l'esprit de la chaîne : **une scène vivante où chaque note se voit arriver
quelque part** (globe, carte, lieu, objet), la règle « every bip = … » annoncée d'entrée, le rythme qui suit la densité de la donnée,
des événements dramatiques (boom, écran rouge), un HUD discret et des jalons qui claquent. Lis son README avant de proposer des angles.
À éviter : un épisode qui n'est qu'un tableau, des barres ou une courbe. Le graphe reste un petit repère, jamais le cœur de l'image.
Dans chaque carte « Données et titre », au moins une option doit être une scène de ce type.

## Règles non négociables
- **Jamais de publication sans le « go »** dans le Control Room (carte de validation).
- **Durée : 62 à 75 s** (cible 64–70 s). Jamais sous 62 s (rémunération TikTok > 1 min, marge contre le rognage). Trop court → un événement ou un palier de plus ; trop long → on retire des événements, on ne change pas le tempo pour tricher.
- **Exactitude** : chaque chiffre, date, record vérifié sur **≥ 2 sources fiables** ; la donnée est un CSV avec colonne source, à côté du module. Pas de valeur inventée « pour la mélodie ». Si une donnée est un modèle ou une estimation, l'écran le dit (« est. », « model »).
- **Unités : SI d'abord, puis l'équivalent US** à l'écran (« 39 045 m · 128 100 ft », « -56 °C · -69 °F »).
- **Aucune mention d'IA**, ni de la fabrication, nulle part (écran, titres, légendes, tags).
- **Contrôle des frames preview avant tout rendu complet** (étape 5).
- **Une seule idée par épisode** : une série de données, un record final.

## Direction artistique retenue (2026-11-08) — « A · Pixel classique », en système
- Base `POP_STYLE=v1` (la plus lisible). Couche art 180×320 agrandie, couche texte 360×640, police VT323.
- **Cadre fixe** d'un épisode à l'autre : HUD en haut (`v2.panel` : titre de la période, valeur courante, sous-valeur), bannière d'événement au centre, **frise / graphe en bas** (courbe de la donnée, échelle log si elle explose).
- **Scène centrale selon le sujet** : carte/globe (pop4), vue de côté (altitude, profondeur), microscope (cellule, atome), orbites (espace).
- **Palette selon le thème**, définie DANS le module de l'épisode (constantes de couleur locales, pas dans v2.py) :
  néon (`POP_STYLE=neon`) pour espace/tech · ambre pour records/histoire · rouge ciné (`POP_STYLE=cine`) pour catastrophes · vert bio pour le vivant.
- Écran qui bouge dès la 1re seconde ; l'accroche (titre + première note) avant 1,5 s ; le « moment » (record, basculement) annoncé visuellement.

## Son retenu (2026-11-08) — « A · Chiptune 8-bit programmé »
- `pi_audio.py` lit la liste d'événements du module (`MOD=<module>`). Rien d'externe, pas de voix.
- ~128 BPM, pentatonique mineure ; mélodie carrée (pulse 12,5/25 %) = la donnée, hauteur selon log(valeur) ; basse triangle ; batterie bruit blanc ; arpège montant (fondamentale, quinte, octave, douzième) sur le record final.
- Les événements se resserrent vers la fin : la musique accélère avec la donnée.
- Variante de timbre possible selon le thème (ex. marimba pour le vivant), à valider épisode par épisode.
- Musique : adaptée au sujet (sombre pour une guerre, haut BPM pour la vitesse…). Règle et signature constante : `studio/beepmelody/music/README.md` (section RULE). Pas de gamme imposée.

## Structure d'un épisode (≈ 64–70 s)
| Temps | Bloc | Contenu |
|---|---|---|
| 0–4 s | intro | Titre-anomalie à l'écran (« THE SKY HAS A CEILING »), première note immédiatement, légende du code (« EVERY BEEP = A NEW RECORD ») |
| 4–50 s | 4 à 7 scènes | Les périodes de la donnée ; chaque événement = note + flash/étiquette ; HUD qui défile ; 2–4 bannières sur les jalons qui surprennent |
| 50–60 s | climax | Les événements se resserrent, montée, record final + arpège + bannière en gros |
| 60–68 s | outro | Valeur finale, source en petit (« DATA: FAI, NASA »), fondu |

## Faire un épisode avec ce moteur
1. **Choisir l'épisode de référence** (champ `new_episode` de FORMATS.json) :
   - série dans le temps sur une carte → copier `pop4.py` (meilleure référence, HUD + graphe + bannières + caméra) ;
   - suite de nombres / chiffres → copier `pi.py` (contient aussi le moteur FX/glitch partagé : ne pas le modifier, l'importer).
   Pour une scène qui n'est pas une carte (vue de côté, microscope…), partir de `pop4.py` et remplacer seulement les fonctions de scène (`SCENEFN`), en gardant `v2.compose`, `panel`, le graphe et la mécanique `EV/ev()`.
2. **Copier** dans `studio/beepmelody/episodes/<ep>.py` (ex. `altitude.py`). En tête du module, remplacer le `sys.path.insert` par le chemin du moteur :
   ```python
   ENGINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "this-melody-is", "engine")
   sys.path.insert(0, ENGINE)
   ```
   et charger les fichiers (geo, CSV) par chemin absolu depuis `__file__`.
3. **Données** : `studio/beepmelody/episodes/<ep>.csv`, colonnes au minimum `date,value,label,source_url`. Remplacer le chargeur de données et la liste d'événements (`SC`, `EVENTS`, `build()`), changer `TITLES`, `SCALE`, palette.
4. **Infos de contrôle** : `python3 <ep>.py info out` → durée totale et nombre d'événements par type. Ajuster `SHORTD` pour tomber dans 62–75 s.
5. **CONTRÔLE avant rendu (obligatoire)** : `python3 <ep>.py preview out <scène>:<s> …` aux moments chargés (intro, chaque bannière, climax, record, outro). Lire les PNG et vérifier :
   - chiffres affichés = CSV = sources (valeur, unité SI + US, date) ;
   - sens des axes et de la courbe (le haut = plus grand ; échelle log annoncée « (LOG) ») ;
   - lisibilité : rien de coupé, pas de chevauchement HUD/bannière/graphe, texte lisible en petit (téléphone) ;
   - aucun mot sur l'IA ou la fabrication.
6. **Rendu** (depuis le dossier du moteur, pour que `pi_audio` trouve le module) :
   ```bash
   cd studio/this-melody-is/engine
   EP=../../beepmelody/episodes; OUT=$EP/out_<ep>
   export PYTHONPATH=$EP POP_STYLE=v1 PI_FX=0.8
   MOD=<ep> python3 pi_audio.py $OUT/music.wav
   python3 $EP/<ep>.py render $OUT
   python3 $EP/<ep>.py final $OUT <ep>.mp4
   ```
7. **Vérifier le MP4** : `ffprobe` (durée 62–75 s, piste audio), planche contact `ffmpeg -i x.mp4 -vf fps=1/4,scale=270:-1,tile=6x3 sheet.png`, l'écouter : chaque flash a sa note.
8. **Outbox** : copier le MP4 (+ `music.wav`, module, CSV) dans `outbox/beepmelody/YYYY-MM-DD_<sujet>/`, stems pour l'onglet Montage :
   `python3 tools/stems.py make --video <final.mp4> --track music=<out>/music.wav --out outbox/beepmelody/<dossier>/stems`. Commit, push (pas les dossiers `out_*`).
9. **Validation (obligatoire)** : carte dans le Control Room (`channel:"beepmelody"`) avec vidéo, durée, sources, contrôle effectué, textes par plateforme écrits par **Bip** (voir PERSONA.md), chaque légende finissant par une question (pas de commentaire épinglé depuis le 10 nov.). Notification push. **Attendre le « go ».**
10. Publication et journal : seulement après le « go », par la tâche de publication de la chaîne (à brancher, voir README.md).

## Retravail (bouton « À retravailler » du Control Room) — PHASE R

Message reçu : « RETRAVAIL (PHASE R) : Guillaume a cliqué « À corriger » / « À retravailler » sur l'épisode <slug> … Sa remarque : … ».
- On retravaille **le même épisode** (même idée, même slug, même dossier outbox). Jamais de carte `choose_topic`, jamais d'autres sujets proposés, jamais « en banque ».
- Le brouillon porte `drafts/<slug>.rework = {note, asked_at, request, done:false}` : il ne doit être ni planifié ni publié tant que `done` est false (le Planner l'ignore).
- Remarque sur le **fond** (sujet, angle, pas assez de données/stats, musique pas intéressante) : reprendre le co-pilote à l'étape concernée (1 = angle/données, 2 = ambiance, 3 = visuel) avec une carte `decision` qui propose 3 nouvelles pistes **pour cette même idée**, en tenant compte de la remarque mot pour mot.
- Retouche **simple** (texte, timing, une valeur) : corriger directement, re-rendre.
- À la fin : nouvelle carte `validate_video` (même slug), `rework.done = true`, `rework.done_at`.

## Couverture (obligatoire, Guillaume 14 nov.)
Les vidéos BeepMelody démarrent sur un écran vide : sans couverture, la grille du profil (Instagram, TikTok, Facebook) n'affiche
que des cases blanches ou noires. Après le rendu final et AVANT l'outbox, poser la couverture (1re image de la vidéo = image clé
+ titre en gros, invisible au visionnage : 1/30 s) :
`python3 tools/cover.py apply --video <mp4 final> --title "<titre court en anglais, ≤ 6 mots si possible>" [--at 0.7]`
(--at = moment de l'image de fond : 0.7 par défaut ; choisir un moment où la scène est bien remplie). Regarder le .cover.jpg produit
(titre lisible, rien de coupé dans le centre 3:4), le garder dans l'outbox à côté du MP4.

## Sources de données acceptées
Organismes et bases citables : FAI (records aériens), NASA, ESA, USGS, NOAA, ONU (WPP), OMS, Our World in Data (avec la source primaire), Banque mondiale, publications scientifiques (DOI). Wikipedia sert à trouver la source primaire, pas comme source finale.
