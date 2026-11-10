# BeepMelody · pilote (variante lo-fi claire) · HOW HIGH HAVE WE GONE? (2026-11-08)

Vidéo : `beepmelody_altitude_lofi.mp4` · 1080×1920 · 30 fps · 68,9 s · 88 BPM
Retours de Guillaume sur la v1 (fission) appliqués : sujet = records d'altitude, DA **claire** (ciel clair, encre marine, corail/or — plus de néon), musique dans l'esprit de « Mirage Melody » (Patrick Patrikios, bibliothèque audio YouTube) : bed lo-fi détendu, accords e-piano Fmaj7–Em7–Dm7–Cmaj7, batterie douce swinguée, basse ronde, craquement vinyle. La donnée reste la mélodie : chaque record = une note de cloche, une marche plus haut sur la gamme.
Module : `studio/beepmelody/episodes/altitude_lofi.py` (moteur partagé importé, non modifié ; musique écrite dans le module, `python3 altitude_lofi.py audio`). Données : `altitude_lofi.csv`, `altitude_landmarks.csv`.
NON PUBLIÉ — attend le « go » dans le Control Room.

## Titre (toutes plateformes)
how high have humans gone? every note is a new record ♪

## Légendes (Pip)
- **TikTok / Reels / Facebook** : wait— every note is a new height record.\n1783: a hot-air balloon at ~1 km.\nguess which note leaves earth. ♪
- **YouTube Shorts** (titre) : How high have humans gone? 1783 → 2026 #shorts · description : every note = a new record for the highest humans have ever been. from a hot-air balloon to Artemis II. sources in the pinned comment.
- **X** : 1783: ~1 km up in a balloon.\n2026: 406,771 km from earth.\none note per record. listen to it climb ♪

## Commentaire épinglé
every note = one record, 1783 → 2026 (selected records). top: Artemis II, 406,771 km from Earth on 6 April 2026, beating Apollo 13 (400,171 km, 1970). sources: FAI, NASA, Smithsonian, Centennial of Flight. which note got you?

## Hashtags
#space #history #aviation #artemis #sonification #pixelart #lofi #adhd

## Contrôle
- 15 records, chacun sur ≥ 2 sources (colonnes source_1 / source_2 de altitude_lofi.csv) ; valeurs incertaines marquées « ~ » à l'écran (1783, 1862, Gemini 11) ; Artemis II : record annoncé, ratification FAI en attente.
- « SELECTED RECORDS » affiché à l'intro et à l'outro (certains records intermédiaires, contestés ou non vérifiés sur 2 sources, sont omis : Robertson 1803, ballons 1839/1927/1933-34, Voskhod 2, autres missions lunaires).
- Repères : Everest 8 849 m, ligne de Kármán 100 km, distance moyenne Terre-Lune 384 400 km (altitude_landmarks.csv).
- Frames preview + planche contact relues (contact.png) ; aucun mot sur l'IA ni la fabrication.
