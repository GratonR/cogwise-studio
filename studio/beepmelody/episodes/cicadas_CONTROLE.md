# Contrôle — cicadas (« These cicadas wait 13 years. Those wait 17. ») · 2026-11-24

Pitch Rédac p-mwtnz28e0, mode autonome. Module `cicadas.py`, données `cicadas.csv` (32 sorties : 18 × Brood XIX, 14 × Brood XIII).

## Données (≥ 2 sources)
- Sortie commune 1803 et 2024, prochaine 2245 : Smithsonian (2024), National Geographic (14 mars 2024), MU Extension (29 janv. 2024) — les trois concordent.
- Brood XIII = 17 ans (Northern Illinois Brood : 1990, 2007, 2024, 2041) ; Brood XIX = 13 ans (Great Southern Brood : 1998, 2011, 2024, 2037) : table UConn Periodical Cicada Project ; MU Extension confirme XIX en 2011.
- Années antérieures à 1990 : calculées depuis les cycles (13 et 17 ans), dit à l'écran (« YEARS BEFORE 1990 FROM THE 13- AND 17-YEAR CYCLES »). Asserts dans le module : pas de 13/17, intersection = {1803, 2024}, 13 × 17 = 221.
- Lieu « Central Illinois » : seule zone de contact (NatGeo, Kritsky : « a few miles » ; Smithsonian : central Illinois + eastern Iowa).
- « Thomas Jefferson is president » en 1803 : Smithsonian + NatGeo.
- Presque-rencontres affichées : 1854/1855 et 1972/1973 (1 an), 1905/1907 et 1920/1922 (2 ans) — vérifiées depuis le CSV.
- Unités : années seulement (pas de grandeur physique, pas d'équivalent US à donner). Le chiffre « 1 trillion » (Smithsonian seul, contesté par NatGeo) n'est PAS utilisé.

## Frames (preview t = 0.3, 1.5, 3.5, 5.4, 6.5, 8, 10.4, 18.9, 19.1, 25.6, 31.7, 40.6, 48.6, 58, 59.6, 61.25, 61.6, 62.6, 63.9, 66.5, 69)
- HUD année = horloge (1 an = 0,25 s ; 1811 à 8,0 s ; 1854 à 18,75 s ; 2024 à 61,25 s) ✓.
- Jauges « UNDERGROUND k/13 · k/17 » = années depuis la dernière sortie de la couvée ✓ (ex. 2017 : XIX 6/13, XIII 10/17).
- Frise du bas : traits rouges tous les 13 ans, verts tous les 17, 1803 et 2024 en or, tête de lecture correcte ; sens gauche → droite = temps ✓.
- Bannières lisibles, rien de coupé, pas de chevauchement HUD/bannière/jauges ; aucun mot sur l'IA ou la fabrication ✓.
- Intro : accroche + première note avant 1,5 s (note à 0,05 s) ✓.

## Son (règle « musicalité d'abord »)
Boucle : D–Bm–G–A 120 BPM · donnée → degré dans l'accord (écart à l'autre couvée : 1 an = aigu, 8 ans = fondamentale, 1,5 octave max) · XIX = voix carrée, XIII = triangle une octave dessous · polyrythmie 13 vs 17 croches issue de la donnée · arrangement qui s'épaissit (pluck dès 1871, shaker dès 1939) · breaks batterie sur 1854/55, 1972/73 et 2016→2024 · drop 2024 = deux voix + arpège.
Pas de glissando ni d'aigu strident : note max A5 (880 Hz) filtrée ; énergie > 3 kHz = 0,6 % (passage 17–21 s), 1 % au drop. Niveaux par seconde homogènes (−19 à −32 dB), pas de trou après réglage du riser.

## Rendu
70,0 s (ffprobe), 1080×1920, vidéo + audio. Planche contact relue. Couverture « Together every 221 years » (--at 1.5).

## Retravail r1 — visuel seul (24 nov. 2026)
Remarque de Guillaume : « Les cigales peuvent être plus mignonnes ». Choix : piste B « Kawaii qui chantent ».
- Changé : chaque cigale = sprite 11 px (gros yeux avec reflet, joues roses, ailes blanches qui battent), nuées à 30 % de la densité, petites notes ♪ au-dessus pendant le chant ; nymphes sous terre = petites larves avec un œil (1 sur 2).
- Identique : CSV, années, couleurs (rouge = Brood XIX 13 ans, vert = Brood XIII 17 ans), HUD, jauges, frise, bannières, musique (music.wav inchangé), timing.
- Contrôle des frames : 2024 (intro), rewind, 1803, 1854/1855, 1960, 1972/1973, drop 2024, outro : jauges et frise conformes au CSV, aucune cigale coupée par le cadre, bannières lisibles (quelques ♪ passent derrière la bannière, voulu). Durée ffprobe 70,0 s.
