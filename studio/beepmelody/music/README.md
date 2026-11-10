# BeepMelody — music

## RULE (Guillaume, 2026-11-10) — supersedes the "one fixed style" decisions below
BeepMelody is **data shown as music**, not one genre. The music fits the subject, episode by episode:
- war, disasters, deaths → slow, dark, sparse (low drones, muted bells, no cute sounds);
- speed, records, races → high BPM, punchy (house/funk, drums, stabs — like the 100 m episode);
- climate, ice, long trends → ambient, slow build;
- space, discoveries → wide, airy synths; the living world → warm, organic (marimba, kalimba, strings).
A scale or key is optional: if the data reads better as pitch, rhythm, density or noise, use that.

What stays constant (the channel signature, so a new beat never needs a new channel):
1. **one data event = one audible hit** (note, drum, click…), placed exactly on the event — the listener *hears* the data;
2. the hit gets **denser/faster when the data does** (the music follows the data, never the reverse);
3. the short **"beep" sting** at the very start and on the final value (same sound every episode = the brand);
4. pixel-art visuals of the channel, light or dark palette matched to the mood.
Choose the mood in PHASE B and say it in one line on the validation card ("mood: dark, 70 BPM, drones + muted bell").

---
## History (kept for reference)

Choice: **A · Chiptune 8-bit, programmed** (not generated). Reference clip: demo_styles.py style A.

- Every data event = one note; pitch = scale degree from log(value) (minor pentatonic, ~2 octaves).
- ~128 BPM backing: triangle bass (Cm–Ab–Bb–G), noise kick/snare/hat; square/pulse lead (duty 12.5/25 %) with a 3/4-beat echo.
- Events get denser toward the climax; the final record gets a rising arpeggio (root, 5th, octave, 12th).
- Implementation for episodes: the event-driven synth in studio/this-melody-is/engine/pi_audio.py (same principle). Theme variants (e.g. marimba for living things) are possible, validated per episode.
- demo_styles.py also keeps the rejected B (synthwave) and C (cinematic) for reference.

## Update 2026-11-08 (pilot v2 feedback)
Guillaume asked for music in the spirit of "Mirage Melody" (Patrick Patrikios, YouTube Audio Library): chill lo-fi.
Pilot v2 (`episodes/altitude_lofi.py`, `python3 altitude_lofi.py audio <wav>`) keeps "every record = one note" but on a lo-fi bed:
88 BPM, e-piano chords Fmaj7–Em7–Dm7–Cmaj7, soft swung drums, round sub bass, vinyl crackle; data notes = kalimba-like bell
on C major pentatonic, one step up per record, dotted-8th echo. Visual style: light "clear sky" palette instead of neon.

## Update 2026-11-08 (pilot v3 feedback on v1: "slow rhythm, change the music, another chord")
`episodes/altitude_v3.py`: 150 BPM straight (8th-note grid, events snapped to it), progression F–G–Em–Am instead of Cm–Ab–Bb–G,
8th-note octave bass, 16th chord arpeggio in busy sections, two data voices (square lead = all-time records, bell + triangle = plane records).
Still the shared pi_audio.py synth, unmodified.
