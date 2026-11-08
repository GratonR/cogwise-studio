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
