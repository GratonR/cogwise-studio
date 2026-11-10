# outbox — one folder per episode

```
outbox/
  cogwise/AAAA-MM-JJ_<slug>/      Cogwise : <slug>.mp4 (final), script/épisode, voix, stems/ (pistes + aperçus)
  beepmelody/AAAA-MM-JJ_<slug>/   BeepMelody : MP4 final, music.wav, module, CSV des données, stems/
  <chaîne>/AAAA-MM-JJ_<slug>/     toute nouvelle chaîne suit le même modèle
  _essais/                        rendus de test et pilotes écartés (gardés pour référence, jamais publiés)
  _drafts/                        divers (échantillons de voix)
```
The Control Room links to these files through raw URLs
`https://raw.githubusercontent.com/GratonR/cogwise-studio/main/outbox/<chaîne>/<dossier>/<fichier>.mp4`.
Moving a folder means updating those links in the database (drafts.video, episodes.links.video, requests.video/link).
