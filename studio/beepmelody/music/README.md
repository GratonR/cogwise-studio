# BeepMelody — music (decided 2026-11-08)

Choice: **A · Chiptune 8-bit, programmed** (not generated). Reference clip: demo_styles.py style A.

- Every data event = one note; pitch = scale degree from log(value) (minor pentatonic, ~2 octaves).
- ~128 BPM backing: triangle bass (Cm–Ab–Bb–G), noise kick/snare/hat; square/pulse lead (duty 12.5/25 %) with a 3/4-beat echo.
- Events get denser toward the climax; the final record gets a rising arpeggio (root, 5th, octave, 12th).
- Implementation for episodes: the event-driven synth in studio/this-melody-is/engine/pi_audio.py (same principle). Theme variants (e.g. marimba for living things) are possible, validated per episode.
- demo_styles.py also keeps the rejected B (synthwave) and C (cinematic) for reference.
