"""Local voice (Chatterbox on Guillaume's RTX 5080) through a GitHub queue — cloud side.

The cloud task cannot reach Guillaume's PC, and the PC cannot be reached from the cloud either, so both talk
through the orphan branch `voice-queue` of this repo:
  cloud  -> jobs/<id>.json                       (this tool, `send`)
  PC     -> results/<id>/voice.flac + starts.json (atelier_voix.py, polls the branch every ~20 s)
  cloud  <- results/<id>/...                     (this tool, `wait`), converted to the engine's inputs.

Usage (from the repo root, after the episode module is final):
  python3 tools/voice_queue.py status                         # last sign of life of the PC workshop
  python3 tools/voice_queue.py send  kit/episodes/X.py         # prints the job id
  python3 tools/voice_queue.py wait  JOB_ID OUTDIR --timeout 900
      -> OUTDIR/voice.mp3 + OUTDIR/starts.json ; exit 0
      -> exit 2 on timeout (PC off / workshop not running): use the fallback described in kit/METHOD.md
  python3 tools/voice_queue.py voice kit/episodes/X.py OUTDIR --timeout 900   # send + wait in one go
  send/voice accept --pause S (silence between beats) --exaggeration X --cfg-weight Y (PC defaults: 0.35 / 0.9 / 0.3)
Then:  cd kit && python3 -m cogwise.run build episodes/X.py OUT --voice OUTDIR/voice.mp3 --starts OUTDIR/starts.json
"""
import argparse, json, os, subprocess, sys, tempfile, time, datetime as dt, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRANCH = "voice-queue"


def git(*args, cwd=None, check=True):
    r = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()[:400]}")
    return r.stdout


def remote_url():
    return git("remote", "get-url", "origin").strip()


def fetch():
    git("fetch", "-q", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")


def show(path):
    r = subprocess.run(["git", "show", f"origin/{BRANCH}:{path}"], cwd=ROOT, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def captions_of(episode):
    sys.path.insert(0, os.path.join(ROOT, "kit"))
    from cogwise import engine
    mod = engine.load_episode(os.path.abspath(episode))
    return mod.META["slug"], [b["caption"] for b in engine.Episode(mod).beats]


def send(episode, settings=None):
    slug, beats = captions_of(episode)
    now = dt.datetime.now(dt.timezone.utc)
    jid = f"{slug}-{now:%Y%m%d-%H%M%S}"
    job = {"id": jid, "slug": slug, "beats": beats, "created_at": now.isoformat(timespec="seconds")}
    job.update(settings or {})
    tmp = tempfile.mkdtemp(prefix="vq-")
    try:
        git("clone", "-q", "--depth", "1", "--branch", BRANCH, remote_url(), tmp, cwd=tmp)
        json.dump(job, open(os.path.join(tmp, "jobs", jid + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        git("add", "-A", cwd=tmp)
        git("-c", "user.name=Cogwise task", "-c", "user.email=noreply@anthropic.com", "commit", "-qm", f"voice job {jid}", cwd=tmp)
        for _ in range(4):  # the PC may push at the same moment
            if subprocess.run(["git", "push", "-q", "origin", BRANCH], cwd=tmp, capture_output=True).returncode == 0:
                break
            git("pull", "-q", "--rebase", "origin", BRANCH, cwd=tmp); time.sleep(2)
        else:
            raise RuntimeError("push of the voice job failed 4 times")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(jid)
    return jid, len(" ".join(beats))


def status():
    fetch()
    raw = show("status/worker.json")
    if not raw:
        print("atelier : aucun signe de vie enregistré"); return None
    st = json.loads(raw)
    print(f"atelier : vu le {st.get('last_seen')} ({st.get('state')}, GPU {st.get('gpu')})")
    return st


def wait(jid, outdir, timeout):
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    while time.time() - t0 < timeout:
        fetch()
        err = show(f"results/{jid}/error.txt")
        if err:
            print("ÉCHEC côté atelier :", err.decode("utf-8", "replace")[:800]); sys.exit(3)
        meta = show(f"results/{jid}/starts.json")
        ext, aud = "flac", show(f"results/{jid}/voice.flac")
        if not aud: ext, aud = "ogg", show(f"results/{jid}/voice.ogg")
        if meta and aud:
            src = os.path.join(outdir, "voice." + ext); open(src, "wb").write(aud)
            m = json.loads(meta)
            json.dump({"beat_starts": m["beat_starts"], "duration": m.get("duration"), "engine": "chatterbox-local",
                       "settings": m.get("settings"), "job": jid}, open(os.path.join(outdir, "starts.json"), "w"), indent=1)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-b:a", "160k",
                            os.path.join(outdir, "voice.mp3")], check=True)
            print(f"voix locale reçue : {m.get('duration')} s, {len(m['beat_starts'])} beats, "
                  f"générée en {m.get('seconds')} s -> {outdir}/voice.mp3 + starts.json")
            return 0
        time.sleep(20)
    print(f"TIMEOUT : pas de voix après {timeout} s (PC éteint ou atelier arrêté). Job {jid} laissé dans la file.")
    sys.exit(2)


def settings(a):
    """Optional voice settings for the PC workshop (defaults there = « Chatterbox 3 »: exaggeration 0.9, cfg 0.3, pause 0.35 s)."""
    out = {"pause": a.pause, "exaggeration": a.exaggeration, "cfg_weight": a.cfg_weight}
    return {k: v for k, v in out.items() if v is not None}


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    sp.add_parser("status")
    s = sp.add_parser("send"); s.add_argument("episode")
    for q in (s,):
        q.add_argument("--pause", type=float); q.add_argument("--exaggeration", type=float); q.add_argument("--cfg-weight", type=float)
    w = sp.add_parser("wait"); w.add_argument("job"); w.add_argument("outdir"); w.add_argument("--timeout", type=int, default=900)
    v = sp.add_parser("voice"); v.add_argument("episode"); v.add_argument("outdir"); v.add_argument("--timeout", type=int, default=900)
    v.add_argument("--pause", type=float); v.add_argument("--exaggeration", type=float); v.add_argument("--cfg-weight", type=float)
    a = ap.parse_args()
    if a.cmd == "status": status()
    elif a.cmd == "send": send(a.episode, settings(a))
    elif a.cmd == "wait": sys.exit(wait(a.job, a.outdir, a.timeout))
    else:
        jid, _ = send(a.episode, settings(a)); sys.exit(wait(jid, a.outdir, a.timeout))


if __name__ == "__main__":
    main()
