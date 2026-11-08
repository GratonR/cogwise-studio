# BeepMelody — épisodes

## altitude (pilote, 2026-11-08) — « How high have humans been? »
- Module `altitude.py` + données `altitude.csv` (28 records de hauteur humaine, 1783 → 2026, 2 sources par ligne).
- Scène : échelle verticale logarithmique (vue de côté), escalier des records, repères Tour Eiffel 330 m / Everest 8 849 m / 100 km / Lune ≈384 400 km ; frise du bas = record en fonction de l'année.
- Palette ambre (records / histoire), POP_STYLE v1, 67,0 s.
- Son : chaque record = une note carrée ; hauteur = log(hauteur) + rang (chaque record un peu plus haut que le précédent, les grands sauts font un bond) ; une montée rapide de notes = la taille du saut ; arpège sur Artemis II.
- Choix de données : 1803 (Robertson) et 1839 (Green), records déclarés mais contestés, ne sont pas retenus ; Gray 1927 est retenu (non homologué). Les valeurs ≈ sont marquées « ≈ » à l'écran. Apollo 8 / Apollo 13 / Artemis II = distance à la Terre (records FAI / Guinness).
- Le 1970 → 2026 sans nouveau record est montré tel quel (« N YEARS · NOBODY WENT HIGHER »).

Commandes : voir `../README.md` (`<ep>` = `altitude`).
