# BeepMelody — music

## RULE (Guillaume, 2026-11-23) — MUSICALITY FIRST. Supersedes the 2026-11-10 rule below.
Why: since 10 Nov the rule "one data event = one hit, placed exactly on the event, the music follows the data" produced
sirens: a smooth curve (e.g. day length in Tromsø) played note by note = a glissando that climbs into a shrill top.
Guillaume: "il faut de la musicalité ; pas grave si ça ne colle pas à 100 % à la data". Our best videos (launches
2026, births, towers, "banger" comments) have a beat, a motif and an accident.

1. **A song first.** A fixed loop runs from start to end: bass + drums on a chord progression of 4 bars (or 8).
   Everything is snapped to that grid (8th or 16th notes). Fidelity is to the *shape* of the data, not the milliseconds.
2. **The data picks, it never drives a raw frequency.** A value chooses a note *inside the current chord / the scale*,
   over 1.5 octaves at most. No continuous pitch, no glissando, nothing shrill.
3. **Continuous data drives the arrangement, not the pitch.** Smooth curves (temperature, day length, distance…) change
   density (notes per bar), which layers play, the filter, or which chord comes next. Notes are for *events*.
4. **Write the 4 beats before producing** (test of the topic): (a) a 2-bar motif you can hum, (b) the motif again with
   a variation, (c) a break: silence, wrong note, bass change, (d) the drop: the record, with the arpeggio.
   If (a) can't be written, the topic is not for Beep Melody — or find another reading of the data.
5. **No template.** Each topic must bring one musical thing that comes from its data: its own tempo, harmony or
   polyrhythm (e.g. cicadas 13 vs 17, TRAPPIST-1's intervals). Vary key, tempo, instruments from one video to the next.
6. **Mood still fits the subject** (dark/slow for disasters, punchy for speed, airy for space, warm for living things),
   and the listener still hears the data: events are audible, the record is the drop.
State it in one line on the validation card: "loop: Am–F–C–G 120 BPM · data → degree in chord · curve → density · drop: record".

## RULE (Guillaume, 2026-11-10) — replaced by the rule above, kept for history
BeepMelody is **data shown as music**, not one genre. The music fits the subject (dark for disasters, high BPM for speed,
ambient for long trends, airy for space, organic for the living world). Old signature: one data event = one audible hit
placed exactly on the event, denser when the data is. → produced unmusical sirens on smooth data; replaced on 2026-11-23.

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
