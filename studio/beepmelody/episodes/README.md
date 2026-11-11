# BeepMelody — épisodes

## altitude (pilote, 2026-11-08) — « How high have humans been? »
- Module `altitude.py` + données `altitude.csv` (28 records de hauteur humaine, 1783 → 2026, 2 sources par ligne).
- Scène : échelle verticale logarithmique (vue de côté), escalier des records, repères Tour Eiffel 330 m / Everest 8 849 m / 100 km / Lune ≈384 400 km ; frise du bas = record en fonction de l'année.
- Palette ambre (records / histoire), POP_STYLE v1, 67,0 s.
- Son : chaque record = une note carrée ; hauteur = log(hauteur) + rang (chaque record un peu plus haut que le précédent, les grands sauts font un bond) ; une montée rapide de notes = la taille du saut ; arpège sur Artemis II.
- Choix de données : 1803 (Robertson) et 1839 (Green), records déclarés mais contestés, ne sont pas retenus ; Gray 1927 est retenu (non homologué). Les valeurs ≈ sont marquées « ≈ » à l'écran. Apollo 8 / Apollo 13 / Artemis II = distance à la Terre (records FAI / Guinness).
- Le 1970 → 2026 sans nouveau record est montré tel quel (« N YEARS · NOBODY WENT HIGHER »).

Commandes : voir `../README.md` (`<ep>` = `altitude`).

## altitude_v3 (pilote v3, 2026-11-08) — retour de Guillaume sur la v1 : « pas assez de records, rythme lent, changer la musique, autre accord »
- Module `altitude_v3.py` + `altitude_v3.csv` : **44 records** (29 records absolus de hauteur humaine + 15 records d'altitude en avion), 2 sources par ligne.
  Nouveau record absolu ajouté : Sadi-Lecointe, 30 oct. 1923, 11 145 m (Guinness : premier avion à battre le record humain des ballons).
  Écartés faute de 2 sources concordantes : Callizo 1924 (barographe truqué), Guidi 1916, Casale 1919, Pezzi 1937, Cunningham 1948, Everest X-1 1949, Walker juil. 1963.
  Dates retenues quand les sources divergent : Adam 30 juin 1937 (AFA), Macready 28 sept. 1921 (This Day in Aviation), Pezzi 1938 = 17 083 m (FAI, pas 17 330).
- Image : même DA (ambre, POP_STYLE v1) ; deuxième escalier bleu ciel pour les records en avion, bannières bleues « PLANE RECORD ».
- Son : 150 BPM droit (au lieu de 112→128), grille de croches, nouvelle grille d'accords **F – G – Em – Am** (IV–V–iii–vi, résout sur l'accord final de la mineur),
  basse en octaves à la croche, arpège en doubles croches sur les accords (évite les notes de données), records absolus = carré (lead), records avion = cloche + triangle.
- 67,8 s. Rendu : `python3 altitude_v3.py render|final`, musique `MOD=altitude_v3 python3 pi_audio.py` (moteur non modifié).

## altitude_v4 (pilote v4, 2026-11-08) — retour de Guillaume sur la v3 : « c'est pas mal mais le bip est trop strident »
- Même données (`altitude_v3.csv`), même image (vidéo de la v3 réutilisée telle quelle), même arrangement (150 BPM, F – G – Em – Am).
- Seule la voix des records change : `altitude_v4.py` retire du flux donné au moteur les notes de données (`digit`, `edigit`) et les clochettes (`chime`),
  et `soft_lead.py` (propre à BeepMelody) les rend avec un timbre rond : sinus + triangle doux, une octave plus bas (plafond La5 = 880 Hz au lieu de La6),
  attaque 8 ms, filtre passe-bas 2,5 kHz, petite réverbe ; clochettes → glockenspiel grave et court. Moteur non modifié.
- Mesure : part d'énergie 2–8 kHz sur les notes de record 1,8 % (v3) → 0,1 % (v4) ; les notes restent ≈ +4,5 dB au-dessus de la moyenne du mix.
- Rendu :
  ```bash
  cd studio/this-melody-is/engine; EP=../../beepmelody/episodes; OUT=$EP/out_altitude_v4; export PYTHONPATH=$EP
  MOD=altitude_v4 python3 pi_audio.py $OUT/backing.wav
  python3 $EP/soft_lead.py altitude_v4 $OUT/backing.wav $OUT/music.wav     # LEAD_GAIN=2.5 par défaut
  ffmpeg -i <vidéo v3 sans son> -i $OUT/music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest beepmelody_altitude_v4.mp4
  ```

## landspeed (2026-11-10) — « From 63 km/h to the speed of sound »
- Module `landspeed.py` + `landspeed.csv` : 57 records de vitesse terrestre qui relèvent la marque absolue (1898 → 1997), trois couloirs
  (électrique + vapeur / moteur à pistons / jet + fusée), 2 sources par ligne, FIA + Guinness pour le record final (1 227,985 km/h, Mach 1,02).
- Image : DA claire (ciel + lac salé), graphe log km/h, voitures pixel par couloir, bannières en bas à droite du graphe ; final = 1 km en temps réel
  ThrustSSC / Blue Bird / Jamais Contente / Jeantaud.
- Son (co-pilote « beep agressif, high tempo ») : 172 BPM breakbeat chiptune, synthé propre au module (`landspeed.py audio`), bang supersonique.
- 67,0 s. Rendu : `python3 landspeed.py audio|render|final` (moteur non modifié).

## everest (2026-11-10) — « The queue to the top »
- Module `everest.py` + `everest.csv` : sommets de l'Everest par an 1953 → 2025 (Himalayan Database ; recoupé HA Expeditions + Alan Arnette ; 2025 = estimation).
- Une année = 1,5 temps à 120 BPM ; chaque année avec sommets = une note (log du nombre) + pas dans la neige ; années à zéro = silence.
- Trois époques, trois voix comme « race to the sky » : cloche 1953-89, marimba 1990-2009, synthé doux 2010-25. DA claire, Everest de profil, file de grimpeurs (1 point = 10 sommets), histogramme linéaire en bas.
- 67,5 s. Rendu : `python3 everest.py audio|render|final` (moteur non modifié).

## kyoto-cherry (co-pilote, 2026-11-10) — « Kyoto's cherry trees now bloom 2 weeks early »
- Module `kyoto_cherry.py` + `kyoto_cherry.csv` : date de pleine floraison à Kyoto, 812 → 2026, 838 années (série Aono, Kazui & Saito,
  miroir GMU ; recoupée OWID / R. Olson 2026 ; JMA pour 2021-2026, colonne `jma_somei_yoshino`). Dates comparées en jour calendaire (année non bissextile).
- Découpage : moyenne par décennie 810s → 2010s (118 notes, 820s/840s/870s sans archive = silence), puis chaque printemps 2020 → 2026 (7 notes). Plus tôt = plus aigu.
- Son (co-pilote « instrument japonais ») : koto sur gamme « in » de La, taiko doux, flûte en bourdon, 72 BPM ; quarte grave ajoutée dès 1870 (la courbe monte), cloche rin sur 2021 et 2023.
- Image : DA claire de printemps, cerisier au bord de la rivière, carte-calendrier, graphe date / année (le haut = plus tôt, « ^ EARLIER »), lignes « AVG APR 14 » et « OLD RECORD MAR 27 ».
- 68,75 s. Rendu : `python3 kyoto_cherry.py audio|render|final` (moteur non modifié).
- Contrôle des frames (étape 3) : 812 = 1er avril ; 27 mars en 1236, 1409, 1612 (record jusqu'en 2021) ; 2021 = 26 mars (19 j avant la moyenne) ; 2023 = 25 mars (20 j) ;
  moyenne 1 200 ans = 14 avril ; 812-1899 = 15 avril ; 2020-2026 = 31 mars (≈ 2 semaines) ; 1990s = 6 avril. Axes : haut = plus tôt, annoncé. Rien de coupé (étiquettes d'axe déplacées, libellé « 1,200-YR AVG » retiré car il chevauchait la courbe).
- Étape 3/4 tranchée : « night » + « une scene en mouvement » → hanami de nuit (panneaux sombres, lune qui monte, étoiles, lanternes, rivière animée, barque, feuillage qui ondule, pétales continus). Données inchangées ; contrôle des frames refait (voir outbox/.../CONTROLE.md). Rendu final 68,73 s.

## life-timeline (co-pilote, 2026-11-11) — « Life on Earth almost ended 5 times. Listen to it come back. »
- Module `life_timeline.py` + `life_timeline.csv` : 31 événements, 4 540 Ma → aujourd'hui (apparitions des grands groupes + les 5 extinctions de masse), 2 sources par ligne
  (ICS 2024-12 pour les limites, Barnosky et al. 2011 Nature via OWID pour les %, papiers/musées pour les apparitions). Le brouillon `life_timeline_draft.csv` est conservé pour l'historique.
- Image : DA claire vert bio, horloge 24 h (« if Earth's history were one day »), frise 4,54 Ga + zoom 540 Ma en bas, extinctions en rouge (flash + secousse + bannière « xx% of species gone », puis « ...and life came back »).
- Son (co-pilote « Mix A C ») : 104 BPM ; A chaud (marimba, shaker, kick doux, basse ronde Am–F–C–G) avant le Cambrien, groove de C (kick/caisse claire, basse en octaves, kalimba) ensuite ;
  extinction = coup sourd + note cassée qui tombe + craquement, la rythmique se coupe 2 temps puis revient avec une crash. Avant le Cambrien 1 événement = 4 temps, ensuite 2 temps.
- 66,9 s. Rendu : `python3 life_timeline.py audio|render|final` (moteur non modifié). Contrôle : outbox/beepmelody/2026-11-11_life-timeline/CONTROLE.md.
