#!/usr/bin/env python3
"""Storage report + lightening of published episodes (Control Room → Système → Stockage).

    python3 tools/storage.py scan --repo . --db DUMP_DIR --out storage.json
    python3 tools/storage.py lighten --repo . --folders outbox/2026-11-02_brake outbox/... --out log.json

Why: every episode adds 12–25 MB of MP4 (+ stems) to git. HEAD stays what tasks clone (--depth 1), the
history is what GitHub counts (soft limit ~1 GB). A published video lives on the platforms, and the
episode can be re-rendered bit-for-bit from its source: <slug>.py + stems/voice.m4a + <slug>_meta.json
(beat_starts) with `cogwise.run build --voice --starts` — no new TTS. So "lighten" keeps the source and
the voice, removes the heavy renders, and writes ARCHIVE.md (what was removed, sizes, sha256, how to rebuild).
Nothing is ever deleted here without the list coming from Guillaume's click in the Control Room.
"""
import argparse, datetime as dt, glob, hashlib, json, os, re, subprocess, sys

KEEP = [r".*\.py$", r".*_meta\.json$", r".*\.srt$", r".*_script\.txt$", r".*_edit\.json$", r".*\.md$",
        r"stems/voice\.m4a$", r"stems/stems\.json$", r".*_voice\.mp3$"]
GH_SOFT_MB = 1000

def mb(n): return round(n / 1048576, 2)

def folder_size(p):
    t = n = 0
    for root, _, files in os.walk(p):
        for f in files:
            t += os.path.getsize(os.path.join(root, f)); n += 1
    return t, n

def heavy_files(p):
    out = []
    for root, _, files in os.walk(p):
        for f in files:
            full = os.path.join(root, f); rel = os.path.relpath(full, p).replace(os.sep, "/")
            if not any(re.match(k, rel) for k in KEEP): out.append((rel, full))
    return out

def load_docs(db, col):
    docs = {}
    for f in glob.glob(os.path.join(db, col, "*.json")):
        try: d = json.load(open(f))
        except Exception: continue
        docs[os.path.splitext(os.path.basename(f))[0]] = d.get("data", d)
    return docs

def gh_size_mb():
    try:
        out = subprocess.run(["gh", "api", "repos/GratonR/cogwise-studio", "--jq", ".size"], capture_output=True, text=True, timeout=30)
        return round(int(out.stdout.strip()) / 1024, 1)
    except Exception: return None

EPDIR = r"/main/(outbox/(?:[^/]+/)*?\d{4}-\d{2}-\d{2}_[^/]+)/"

def scan(a):
    eps = load_docs(a.db, "episodes"); drafts = load_docs(a.db, "drafts")
    vid2ep = {}
    for slug, e in eps.items():
        v = ((e.get("links") or {}).get("video") or "")
        m = re.search(EPDIR, v)
        if m: vid2ep[m.group(1)] = slug
    def ep_for(name):   # fallback when episodes.links.video is missing: match the folder slug (brake ~ brakes, wing-v2 ~ wing)
        base = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", name); base = re.sub(r"-v\d+$", "", base)
        for slug in eps:
            if slug == base or slug.rstrip("s") == base.rstrip("s"): return slug
        return None
    draft_dirs = set()
    for d in drafts.values():
        for k in ("video", "video_original"):
            m = re.search(EPDIR, d.get(k) or "")
            if m: draft_dirs.add(m.group(1))
    today = dt.date.today(); folders = []; head = 0
    # episode folders live at any depth: outbox/cogwise/<date>_<slug>, outbox/beepmelody/…, outbox/_essais/…
    cands = [p for p in glob.glob(os.path.join(a.repo, "outbox", "**", "*"), recursive=True)
             if os.path.isdir(p) and (re.match(r"\d{4}-\d{2}-\d{2}_", os.path.basename(p)) or os.path.basename(p) == "_drafts")
             and "/stems" not in p.replace(os.sep, "/")]
    for p in sorted(cands):
        rel = os.path.relpath(p, a.repo).replace(os.sep, "/"); size, n = folder_size(p); head += size
        name = os.path.basename(p); m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)", name)
        date = m.group(1) if m else None; age = (today - dt.date.fromisoformat(date)).days if date else None
        light = os.path.exists(os.path.join(p, "ARCHIVE.md"))
        ep = vid2ep.get(rel) or (None if rel in draft_dirs else ep_for(name))
        rebuild = bool(glob.glob(os.path.join(p, "*.py"))) and (os.path.exists(os.path.join(p, "stems", "voice.m4a")) or bool(glob.glob(os.path.join(p, "*_voice.mp3"))))
        heavy = sum(os.path.getsize(f) for _, f in heavy_files(p)) if not light else 0
        if light: kind = "allégé"
        elif name.startswith("_"): kind = "divers"
        elif "/_essais/" in rel: kind = "essai"         # test renders and rejected pilots, kept for reference       # e.g. _drafts/voices: voice samples, never touched automatically
        elif rel in draft_dirs: kind = "stock"
        elif rel in vid2ep: kind = "publié"
        elif ep and ep in vid2ep.values(): kind = "ancienne version"   # the episode was published from another folder (wing → wing-v2)
        elif ep: kind = "publié"
        elif "test" in name: kind = "test"
        else: kind = "ancienne version"   # a render that was replaced (wing → wing-v2) or never published
        folders.append({"path": rel, "mb": mb(size), "files": n, "kind": kind, "episode": ep, "rebuildable": rebuild,
                        "date": date, "age_days": age, "heavy_mb": mb(heavy),
                        "can_lighten": kind in ("publié", "ancienne version", "test") and heavy > 0 and (age is None or age >= a.min_age)})
    for p in ["kit", "studio", "tools", "docs"]:
        full = os.path.join(a.repo, p)
        if os.path.isdir(full): head += folder_size(full)[0]
    total = gh_size_mb()
    cand = [f for f in folders if f["can_lighten"]]
    rep = {"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "github": {"repo_mb": total, "head_mb": mb(head), "history_mb": round(total - mb(head), 1) if total else None, "soft_limit_mb": GH_SOFT_MB},
           "folders": sorted(folders, key=lambda f: -f["mb"]),
           "lighten": {"count": len(cand), "mb": round(sum(f["heavy_mb"] for f in cand), 1), "folders": [f["path"] for f in cand]}}
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(rep, open(a.out, "w"), indent=2, ensure_ascii=False)
    print(json.dumps({"repo_mb": total, "head_mb": rep["github"]["head_mb"], "lighten_mb": rep["lighten"]["mb"], "candidates": len(cand)}))

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def lighten(a):
    log = []
    for rel in a.folders:
        p = os.path.join(a.repo, rel)
        if not os.path.isdir(p) or os.path.exists(os.path.join(p, "ARCHIVE.md")):
            log.append({"path": rel, "status": "ignoré", "reason": "absent ou déjà allégé"}); continue
        removed = [{"file": r, "bytes": os.path.getsize(f), "sha256": sha(f)} for r, f in heavy_files(p)]
        if not removed:
            log.append({"path": rel, "status": "ignoré", "reason": "rien de lourd"}); continue
        kept = sorted(os.path.relpath(os.path.join(root, f), p).replace(os.sep, "/") for root, _, fs in os.walk(p) for f in fs
                      if not any(x["file"] == os.path.relpath(os.path.join(root, f), p).replace(os.sep, "/") for x in removed))
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}_", "", os.path.basename(p))
        can_rebuild = any(k.endswith(".py") for k in kept) and ("stems/voice.m4a" in kept or any(k.endswith("_voice.mp3") for k in kept))
        md = [f"# Archived {dt.date.today().isoformat()}", "",
              "Heavy renders removed from the working tree to keep the repo small (the video is published on the platforms;",
              "earlier versions stay in git history until the history is compacted).", "", "## Removed", ""]
        md += [f"- `{x['file']}` — {mb(x['bytes'])} MB — sha256 `{x['sha256'][:16]}…`" for x in removed]
        md += ["", "## Kept", ""] + [f"- `{k}`" for k in kept] + ["", "## Rebuild", ""]
        md += ([f"`cd kit && python3 -m cogwise.run build ../{rel}/{slug}.py OUT --voice ../{rel}/stems/voice.m4a --starts ../{rel}/{slug}_meta.json`"
                " (same voice, same timing, no new TTS)."] if can_rebuild else
               ["No separate voice track was kept for this episode (made before stems existed): a rebuild would need a new voice."])
        for x in removed: os.remove(os.path.join(p, x["file"]))
        for root, dirs, files in sorted(os.walk(p, topdown=False)):
            if root != p and not os.listdir(root): os.rmdir(root)
        open(os.path.join(p, "ARCHIVE.md"), "w").write("\n".join(md) + "\n")
        log.append({"path": rel, "status": "allégé", "freed_mb": mb(sum(x["bytes"] for x in removed)), "removed": [x["file"] for x in removed],
                    "kept": kept, "rebuildable": can_rebuild})
    json.dump(log, open(a.out, "w"), indent=2, ensure_ascii=False)
    print(json.dumps([{k: v for k, v in l.items() if k in ("path", "status", "freed_mb", "rebuildable")} for l in log], ensure_ascii=False))

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("--repo", default="."); s.add_argument("--db", required=True); s.add_argument("--out", required=True)
    s.add_argument("--min-age", type=int, default=2, help="published at least N days ago before it can be lightened")
    l = sub.add_parser("lighten"); l.add_argument("--repo", default="."); l.add_argument("--folders", nargs="+", required=True); l.add_argument("--out", required=True)
    a = ap.parse_args()
    scan(a) if a.cmd == "scan" else lighten(a)

if __name__ == "__main__":
    main()
