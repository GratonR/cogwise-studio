# voice-queue — file d'attente de l'atelier voix (branche orpheline, purgeable)

Le cloud (tâche Cogwise) dépose `jobs/<id>.json` ; l'atelier voix du PC de Guillaume (RTX 5080, Chatterbox)
le lit, génère la voix, puis écrit `results/<id>/voice.ogg` + `results/<id>/starts.json` et supprime le job.
`status/worker.json` = dernier signe de vie de l'atelier.

Format d'un job : {"id", "slug", "beats": ["phrase du beat 1", ...], "created_at", réglages optionnels
(exaggeration, cfg_weight, pause, lead, seed)}. Outil côté cloud : `tools/voice_queue.py` (branche main).
Cette branche ne contient que des fichiers temporaires : elle peut être recréée à vide à tout moment.
