# BeepMelody — atelier de la chaîne

Shorts data + musique, sans voix, en anglais, 62–75 s, 1080×1920. Persona écrite : Bip.

```
studio/beepmelody/
  METHOD.md     méthode d'un épisode (règles, DA, son, structure, contrôle, validation)
  PERSONA.md    Bip, la voix écrite de la chaîne
  music/        direction musicale A (chiptune programmé) + prototype demo_styles.py
  episodes/     un module <ep>.py + son CSV de données par épisode (à créer au pilote)
```

## Moteur
Format `data-sonification` → moteur partagé **`studio/this-melody-is/engine`** (non copié, non modifié) :
`v2.py` (dessin, HUD, compose), `pi.py` (FX/glitch), `pi_audio.py` (synthé chiptune piloté par les événements).
Épisode de référence à copier : `pop4.py` (série temporelle + HUD + graphe + bannières), ou `pi.py` pour une suite de nombres.

Vérifié le 2026-11-08 : `pop4.py preview` (3 frames, POP_STYLE v1), rendu de la scène intro (4,5 s) et `pi_audio.py` (88,5 s de musique) tournent sans erreur.

## Commandes
```bash
cd studio/this-melody-is/engine
EP=../../beepmelody/episodes; OUT=$EP/out_<ep>
export PYTHONPATH=$EP POP_STYLE=v1 PI_FX=0.8          # POP_STYLE: v1 | cine | neon
python3 $EP/<ep>.py info out                          # durée + nb d'événements
python3 $EP/<ep>.py preview $OUT intro:2 climax:5     # PNG de contrôle
MOD=<ep> python3 pi_audio.py $OUT/music.wav           # musique depuis les événements
python3 $EP/<ep>.py render $OUT                       # scènes vidéo
python3 $EP/<ep>.py final $OUT <ep>.mp4               # assemblage vidéo + musique
```
Dépendances : python3, numpy, pillow, scipy, ffmpeg.

## Ce qui reste à brancher
- **Premier épisode** (`episodes/`) : action « pilote » — sujet proposé : records d'altitude atteinte par l'homme (vue de côté, palette ambre).
- **Palettes thématiques** (ambre, vert bio) : à définir dans chaque module d'épisode ; le moteur n'offre que v1 / cine / neon.
- **Scènes non cartographiques** (vue de côté, microscope, orbites) : à écrire dans le module de l'épisode à partir de pop4.py ; si une scène sert à plusieurs épisodes, la factoriser dans `studio/beepmelody/episodes/bm_scenes.py` (pas dans le moteur partagé).
- **Variante de timbre** (marimba pour le vivant) : pi_audio.py n'a que le chiptune ; à prototyper dans le module/à part si un épisode la demande.
- **Publication** : jetons YouTube et Meta sur le Drive (« Studio — clés beepmelody »), Buffer prêt pour TikTok/Instagram/X. Aucune tâche de publication BeepMelody n'existe encore ; rien n'est publié sans le « go » du Control Room.
