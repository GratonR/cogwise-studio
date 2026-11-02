"""Voice-over: ElevenLabs TTS with character timestamps, or forced alignment of an existing MP3.

Both return (mp3_path, beat_starts[list of seconds], voice_len).
"""
import json, os, re, base64, subprocess

def _duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())

def _beat_offsets(captions):
    """Character offset of each caption inside the joined script."""
    offs, pos = [], 0
    for c in captions:
        offs.append(pos); pos += len(c) + 1
    return offs, " ".join(captions)

def elevenlabs(captions, out_mp3, api_key, voice_id, model_id="eleven_multilingual_v2",
               stability=0.45, similarity=0.8, style=0.15, speed=1.0):
    import requests
    offs, text = _beat_offsets(captions)
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps",
        params={"output_format": "mp3_44100_128"},
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": text, "model_id": model_id,
              "voice_settings": {"stability": stability, "similarity_boost": similarity,
                                 "style": style, "speed": speed}},
        timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"ElevenLabs error {r.status_code}: {r.text[:400]}")
    data = r.json()
    open(out_mp3, 'wb').write(base64.b64decode(data['audio_base64']))
    al = data.get('alignment') or data.get('normalized_alignment')
    st = al['character_start_times_seconds']
    starts = []
    for o in offs:
        k = o
        while k < len(text) and text[k] == ' ': k += 1
        starts.append(st[min(k, len(st) - 1)])
    json.dump({"starts": starts, "alignment": al}, open(out_mp3 + '.align.json', 'w'))
    return out_mp3, starts, _duration(out_mp3)

def align_existing(captions, mp3):
    """Forced alignment with pocketsphinx (offline). Use when the voice was made by hand in ElevenLabs."""
    from pocketsphinx import Decoder
    raw = mp3 + '.16k.raw'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mp3, '-ar', '16000', '-ac', '1', '-f', 's16le', raw], check=True)
    d = Decoder(samprate=16000, bestpath=False, loglevel="FATAL")
    words, owner = [], []
    for i, c in enumerate(captions):
        c = c.lower().replace("cogwise", "cog wise")
        for w in re.sub(r"[^a-z' ]", " ", c).split():
            if d.lookup_word(w) is not None: words.append(w); owner.append(i)
    d.set_align_text(" ".join(words))
    d.start_utt(); d.process_raw(open(raw, 'rb').read(), full_utt=True); d.end_utt()
    segs = [s for s in d.seg() if s.word not in ('<s>', '</s>', '<sil>', '(NULL)')]
    starts = {}
    for k, s in enumerate(segs[:len(words)]):
        starts.setdefault(owner[k], s.start_frame / 100)
    os.remove(raw)
    out = []
    for i in range(len(captions)):
        if i in starts: out.append(starts[i])
        else: out.append(out[-1] + 3.0 if out else 0.0)   # caption with no recognisable word
    return mp3, out, _duration(mp3)
