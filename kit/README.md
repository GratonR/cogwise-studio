# Cogwise studio kit

Explainer shorts in the Cogwise style (vintage manual: cream paper, ink, red / mustard / teal),
1080x1920, 30 fps, English voice-over by ElevenLabs, synthesized SFX, burned-in captions.

## Layout of this repo
```
cogwise/            the kit (style, engine, audio, voice, CLI)
episodes/           one Python module per episode (fridge.py = reference episode)
outbox/YYYY-MM-DD_slug/   finished videos waiting to be published (public raw URLs for Zapier)
METHOD.md           the daily routine, step by step
requirements.txt
```
The ElevenLabs key is NEVER committed here: it lives in `Cogwise/config/cogwise_config.json` on the Cogwise Google Drive.

## Commands
```bash
pip install --break-system-packages -r requirements.txt
python -m cogwise.run stills  episodes/NAME.py /tmp/stills 3 12 25 40 66   # key frames, design timeline
python -m cogwise.run build   episodes/NAME.py out/ --tts config.json        # final video (ElevenLabs)
python -m cogwise.run build   episodes/NAME.py out/ --voice voice.mp3        # final video (existing voice)
```
`build` outputs `<slug>.mp4`, `<slug>.srt`, `<slug>_voice.mp3`, `<slug>_meta.json`, `<slug>_script.txt`.

## Writing an episode (copy episodes/fridge.py)
- `META` slug / title / description / hashtags
- `BEATS` list of `dict(dur, title, caption, card)`; the engine appends the outro beat
  ("Cogwise: how things work. Follow for the next one!") and the owl + wordmark end card.
- `draw(ctx, t, E)` draws the stage at design time `t` (seconds on the BEATS timeline).
  The engine warps design time onto the real voice timing, beat by beat.
- `CARDS = {'name': fn(ctx, t, lt, a)}` inset zoom cards: call `card_frame(ctx, TITLE, a, LABEL, color)`
  then draw inside x 110..970, y 250..540. The stage shrinks to 78 % automatically while a card shows.
- `SFX = [(t, 'pop'|'click'|'whoosh'|'sizzle'|'ding')]`, `HUM = [(t0, t1)]` (design times).
  Intro pop, card whooshes, outro whoosh + bell are automatic.
- Zones: title y 60-170, cards y 150-610, stage y 300-1500, floor 1500-1650, captions 1650-1920.
- Keep it uncluttered: one cut-away object, at most one or two backdrop props (`window()`, `counter()`).
