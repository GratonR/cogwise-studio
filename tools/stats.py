#!/usr/bin/env python3
"""Cogwise stats collector — one run = all platforms, one snapshot.

Usage:
  python tools/stats.py --keys KEYS.env --yt-token TOKEN.txt --db DUMP_DIR --out OUT_DIR

KEYS.env      lines KEY=value (BUFFER_API_KEY, YOUTUBE_API_KEY, YT_CLIENT_ID, YT_CLIENT_SECRET, FB_PAGE_ID, FB_PAGE_TOKEN);
              other lines (explanations, BOM, YT_AUTH_URL) are ignored. Never printed.
TOKEN.txt     the YouTube refresh token (file "Cogwise — jeton YouTube" on the Drive).
DUMP_DIR      ArtifactData dumps (out_dir) of: episodes, comments, and the latest snapshot (collection "snapshots").
OUT_DIR       receives snapshot.json (one new document for collection "snapshots"), retention.json (doc meta/retention),
              daily.json (doc daily/<date>),
              comments_new_<n>.json (batch writes, <= 50 each) and summary.txt (French, short).

Nothing secret is ever written to OUT_DIR or stdout.
"""
import argparse, datetime as dt, glob, json, os, re, sys, urllib.error, urllib.parse, urllib.request

CHANNEL = "UCBEkBsO2B0x6rxt6hAWwIfQ"
BUFFER_ORG = "6ae8b02e8337954edea10196"
G = "https://graph.facebook.com/v21.0/"
UA = {"User-Agent": "cogwise-stats/1.0"}
ERRORS = []
CALLS = {"buffer": 0, "youtube": 0, "meta": 0}


def keys(path):
    env = {}
    for line in open(path, encoding="utf-8-sig"):
        m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
        if m:
            env[m[1]] = m[2].strip().strip("\"'")
    return env


def http(url, data=None, headers=None, method=None, kind=None, timeout=60):
    if kind:
        CALLS[kind] += 1
    h = dict(UA, **(headers or {}))
    if isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode()
    elif isinstance(data, str):
        data = data.encode()
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def safe(label, fn, default=None):
    try:
        return fn()
    except urllib.error.HTTPError as e:
        body = e.read()[:300].decode("utf-8", "replace")
        ERRORS.append(f"{label} : HTTP {e.code} {re.sub(r'access_token=[^&\" ]+', 'access_token=***', body)[:160]}")
    except Exception as e:  # network, parsing
        ERRORS.append(f"{label} : {type(e).__name__} {str(e)[:120]}")
    return default


def load_dir(path):
    out = {}
    for f in glob.glob(os.path.join(path, "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        out[os.path.basename(f)[:-5]] = d.get("data", d) if isinstance(d, dict) and set(d) >= {"data"} else d
    return out


def ep_for(episodes, platform, key=None, text="", date=None):
    """Match a post to an episode slug: by id/link in episodes.links, else by title words, else by date."""
    field = {"YouTube": "youtube", "Facebook": "facebook", "Instagram": "instagram", "TikTok": "tiktok", "X": "x"}[platform]
    for slug, e in episodes.items():
        link = str((e.get("links") or {}).get(field) or "") + " " + str((e.get("links_v1") or {}).get(field) or "")
        if key and key in link:
            return slug
    t = (text or "").lower()
    best, score = "", 0
    for slug, e in episodes.items():
        words = [w for w in re.findall(r"[a-z]{4,}", (str(e.get("yt_title") or "") + " " + str(e.get("titre") or "") + " " + slug).lower())
                 if w not in {"does", "what", "your", "with", "that", "this", "work", "works", "shorts", "howthingswork"}]
        s = sum(1 for w in set(words) if w in t)
        if s > score:
            best, score = slug, s
    if score >= 2 or (score == 1 and len(t) < 400):
        return best
    if date:
        for slug, e in episodes.items():
            if str(e.get("date", ""))[:10] == str(date)[:10]:
                return slug
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keys", required=True); ap.add_argument("--yt-token")
    ap.add_argument("--db", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    K = keys(a.keys)
    os.makedirs(a.out, exist_ok=True)
    episodes = load_dir(os.path.join(a.db, "episodes"))
    known_comments = set(load_dir(os.path.join(a.db, "comments")))
    prev = list(load_dir(os.path.join(a.db, "snapshots")).values())
    prev = max(prev, key=lambda s: s.get("at", "")) if prev else {}
    # retention curves live in meta/retention (kept out of snapshots so the page can load many snapshots cheaply)
    _rf = os.path.join(a.db, "meta", "retention.json")
    if os.path.exists(_rf):
        _r = json.load(open(_rf, encoding="utf-8")); _r = _r.get("data", _r) if isinstance(_r, dict) and "data" in _r and "curves" not in _r else _r
        if not prev.get("retention"): prev = dict(prev, retention=_r.get("curves") or {})
    now = dt.datetime.now(dt.timezone.utc)
    posts, new_comments, followers, retention = {}, [], {}, {}

    # ---------- YouTube ----------
    yk = K.get("YOUTUBE_API_KEY")
    Y = "https://www.googleapis.com/youtube/v3/"
    ch = safe("YouTube chaîne", lambda: http(f"{Y}channels?part=statistics,contentDetails&id={CHANNEL}&key={yk}", kind="youtube"))
    if ch and ch.get("items"):
        followers["youtube"] = int(ch["items"][0]["statistics"].get("subscriberCount", 0))
        up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        pl = safe("YouTube vidéos", lambda: http(f"{Y}playlistItems?part=contentDetails&maxResults=50&playlistId={up}&key={yk}", kind="youtube")) or {}
        ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
        if ids:
            vs = safe("YouTube stats", lambda: http(f"{Y}videos?part=statistics,snippet&id={','.join(ids)}&key={yk}", kind="youtube")) or {}
            for v in vs.get("items", []):
                st, sn = v["statistics"], v["snippet"]
                posts["yt-" + v["id"]] = {"platform": "YouTube", "episode": ep_for(episodes, "YouTube", v["id"], sn.get("title", ""), sn.get("publishedAt")),
                                          "link": "https://youtube.com/shorts/" + v["id"], "views": int(st.get("viewCount", 0)),
                                          "likes": int(st.get("likeCount", 0)), "comments": int(st.get("commentCount", 0)), "source": "API YouTube"}
                if int(st.get("commentCount", 0)) > 0:
                    ct = safe("YouTube commentaires", lambda: http(f"{Y}commentThreads?part=snippet&videoId={v['id']}&maxResults=100&textFormat=plainText&key={yk}", kind="youtube")) or {}
                    for t in ct.get("items", []):
                        s = t["snippet"]["topLevelComment"]["snippet"]
                        if (s.get("authorChannelId") or {}).get("value") == CHANNEL:
                            continue
                        cid = "yt-" + t["id"]
                        if cid not in known_comments:
                            new_comments.append((cid, {"platform": "YouTube", "episode": posts["yt-" + v["id"]]["episode"], "author": s.get("authorDisplayName", "?"),
                                                       "text": s.get("textDisplay", ""), "published_at": s.get("publishedAt"), "likes": s.get("likeCount", 0),
                                                       "replies": t["snippet"].get("totalReplyCount", 0), "link": f"https://www.youtube.com/watch?v={v['id']}&lc={t['id']}",
                                                       "reply_status": "à traiter"}))
        # retention (YouTube Analytics, 1-2 days lag)
        if a.yt_token and os.path.exists(a.yt_token):
            rt = open(a.yt_token, encoding="utf-8-sig").read().strip().split("=")[-1].strip()
            tok = safe("YouTube jeton", lambda: http("https://oauth2.googleapis.com/token", {"client_id": K["YT_CLIENT_ID"], "client_secret": K["YT_CLIENT_SECRET"],
                                                                                         "refresh_token": rt, "grant_type": "refresh_token"}))
            if tok and tok.get("access_token"):
                q = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": "2026-10-01", "endDate": now.date().isoformat(),
                                            "metrics": "views,averageViewDuration,averageViewPercentage", "dimensions": "video", "maxResults": 200, "sort": "-views"})
                an = safe("YouTube Analytics", lambda: http("https://youtubeanalytics.googleapis.com/v2/reports?" + q,
                                                            headers={"Authorization": "Bearer " + tok["access_token"]}, kind="youtube")) or {}
                for row in an.get("rows", []):
                    p = posts.get("yt-" + row[0])
                    if p:
                        p["avg_watch_s"], p["avg_pct"] = row[2], round(row[3], 1)
                # second-by-second retention curve (100 points), refreshed at most every 20 h per video
                old_rc = prev.get("retention") or {}
                for k_, p in posts.items():
                    if not k_.startswith("yt-") or not p.get("episode"):
                        continue
                    vid, o = k_[3:], old_rc.get(p["episode"]) or {}
                    if o.get("pts") and o.get("at") and (now - dt.datetime.fromisoformat(o["at"].replace("Z", "+00:00"))).total_seconds() < 20 * 3600:
                        retention[p["episode"]] = o; continue
                    q2 = urllib.parse.urlencode({"ids": "channel==MINE", "startDate": "2026-10-01", "endDate": now.date().isoformat(),
                                                 "metrics": "audienceWatchRatio,relativeRetentionPerformance", "dimensions": "elapsedVideoTimeRatio", "filters": "video==" + vid})
                    rc = safe("YouTube rétention", lambda: http("https://youtubeanalytics.googleapis.com/v2/reports?" + q2,
                                                               headers={"Authorization": "Bearer " + tok["access_token"]}, kind="youtube")) or {}
                    rows = rc.get("rows") or []
                    if rows:
                        retention[p["episode"]] = {"video": vid, "at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                   "pts": [[round(r[0], 2), round(r[1], 3), round(r[2], 3)] for r in rows]}
                    elif o:
                        retention[p["episode"]] = o

    # ---------- Facebook + Instagram (Meta Graph) ----------
    pid, pt = K.get("FB_PAGE_ID"), urllib.parse.quote(K.get("FB_PAGE_TOKEN", ""))
    g = lambda path: http(G + path + ("&" if "?" in path else "?") + "access_token=" + pt, kind="meta")
    page = safe("Facebook page", lambda: g(f"{pid}?fields=followers_count,instagram_business_account{{id,followers_count}}"))
    if page:
        followers["facebook"] = page.get("followers_count")
        reels = (safe("Facebook reels", lambda: g(f"{pid}/video_reels?fields=id,description,created_time&limit=50")) or {}).get("data", [])
        for r in reels:
            ins = safe("Facebook stats", lambda: g(f"{r['id']}/video_insights?metric=fb_reels_total_plays,blue_reels_play_count,post_video_avg_time_watched")) or {}
            m = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
            eng = safe("Facebook réactions", lambda: g(f"{r['id']}?fields=likes.summary(true).limit(0),comments.summary(true).limit(0)")) or {}
            slug = ep_for(episodes, "Facebook", r["id"], r.get("description", ""), r.get("created_time"))
            p = {"platform": "Facebook", "episode": slug, "link": "https://www.facebook.com/reel/" + r["id"], "source": "API Meta",
                 "likes": ((eng.get("likes") or {}).get("summary") or {}).get("total_count"),
                 "comments": ((eng.get("comments") or {}).get("summary") or {}).get("total_count")}
            if "fb_reels_total_plays" in m: p["views"] = m["fb_reels_total_plays"]
            if "blue_reels_play_count" in m: p["unique_plays"] = m["blue_reels_play_count"]
            if m.get("post_video_avg_time_watched") is not None: p["avg_watch_s"] = round(m["post_video_avg_time_watched"] / 1000, 1)
            posts["fb-" + r["id"]] = {k: v for k, v in p.items() if v is not None}
            if p.get("comments"):
                cs = (safe("Facebook commentaires", lambda: g(f"{r['id']}/comments?fields=id,from,message,created_time,like_count,comment_count&limit=100")) or {}).get("data", [])
                for c in cs:
                    if (c.get("from") or {}).get("id") == pid:
                        continue
                    cid = "fb-" + c["id"]
                    if cid not in known_comments:
                        new_comments.append((cid, {"platform": "Facebook", "episode": slug, "author": (c.get("from") or {}).get("name", "(anonyme)"),
                                                   "text": c.get("message", ""), "published_at": c.get("created_time"), "likes": c.get("like_count", 0),
                                                   "replies": c.get("comment_count", 0), "link": "https://www.facebook.com/reel/" + r["id"], "reply_status": "à traiter"}))
        ig = page.get("instagram_business_account") or {}
        if ig.get("id"):
            followers["instagram"] = ig.get("followers_count")
            media = (safe("Instagram médias", lambda: g(f"{ig['id']}/media?fields=id,caption,timestamp,permalink,like_count,comments_count&limit=50")) or {}).get("data", [])
            for md in media:
                ins = safe("Instagram stats", lambda: g(f"{md['id']}/insights?metric=views,reach,saved,shares,ig_reels_avg_watch_time")) or {}
                m = {d["name"]: d["values"][0]["value"] for d in ins.get("data", [])}
                slug = ep_for(episodes, "Instagram", md.get("permalink", "").rstrip("/").split("/")[-1], md.get("caption", ""), md.get("timestamp"))
                p = {"platform": "Instagram", "episode": slug, "link": md.get("permalink"), "source": "API Meta",
                     "views": m.get("views"), "reach": m.get("reach"), "likes": md.get("like_count"), "comments": md.get("comments_count"),
                     "saves": m.get("saved"), "shares": m.get("shares")}
                if m.get("ig_reels_avg_watch_time") is not None: p["avg_watch_s"] = round(m["ig_reels_avg_watch_time"] / 1000, 1)
                posts["ig-" + (slug or md["id"])] = {k: v for k, v in p.items() if v is not None}
                if md.get("comments_count"):
                    cs = (safe("Instagram commentaires", lambda: g(f"{md['id']}/comments?fields=id,username,text,timestamp,like_count&limit=100")) or {}).get("data", [])
                    for c in cs:
                        if c.get("username") == "cogwisehtw":
                            continue
                        cid = "ig-" + c["id"]
                        if cid not in known_comments:
                            new_comments.append((cid, {"platform": "Instagram", "episode": slug, "author": "@" + c.get("username", "?"), "text": c.get("text", ""),
                                                       "published_at": c.get("timestamp"), "likes": c.get("like_count", 0), "link": md.get("permalink"), "reply_status": "à traiter"}))

    # ---------- TikTok + X (Buffer) ----------
    q = '{ posts(first: 100, input:{organizationId:"%s"}){ edges{ node{ id channelService status externalLink sentAt text metrics{ type value } } } } }' % BUFFER_ORG
    bf = safe("Buffer", lambda: http("https://api.buffer.com", json.dumps({"query": q}),
                                     headers={"Authorization": "Bearer " + K.get("BUFFER_API_KEY", ""), "Content-Type": "application/json"}, kind="buffer")) or {}
    sent_this_month = 0
    for e in ((bf.get("data") or {}).get("posts") or {}).get("edges", []):
        n = e["node"]
        if n.get("status") != "sent":
            continue
        if str(n.get("sentAt", ""))[:7] == now.strftime("%Y-%m"):
            sent_this_month += 1
        m = {x["type"]: x["value"] for x in (n.get("metrics") or [])}
        link = n.get("externalLink") or ""
        svc = n.get("channelService")
        if svc == "tiktok":
            vid = (re.findall(r"/video/(\d+)", link) or [n["id"]])[0]
            posts["tt-" + vid] = {"platform": "TikTok", "episode": ep_for(episodes, "TikTok", vid, n.get("text", ""), n.get("sentAt")),
                                  "link": f"https://www.tiktok.com/@cogwisehtw/video/{vid}", "views": m.get("views"), "likes": m.get("reactions"),
                                  "comments": m.get("comments"), "shares": m.get("shares"), "reach": m.get("reach"), "avg_watch_s": m.get("averageTimeWatched"), "source": "API Buffer"}
        elif svc == "twitter":
            sid = (re.findall(r"/status/(\d+)", link) or [n["id"]])[0]
            p = {"platform": "X", "episode": ep_for(episodes, "X", sid, n.get("text", ""), n.get("sentAt")), "link": f"https://x.com/cogwisehtw/status/{sid}",
                 "likes": m.get("reactions"), "comments": m.get("comments"), "shares": m.get("reposts"), "source": "API Buffer"}
            if m.get("impressions"):
                p["views"] = m["impressions"]
            else:
                old = (prev.get("posts") or {}).get("x-" + sid) or {}
                if old.get("views"): p["views"] = old["views"]
            posts["x-" + sid] = p
    for k in list(posts):
        posts[k] = {a_: b for a_, b in posts[k].items() if b is not None}
    # keep last known values for posts a source failed to return this time
    for k, v in (prev.get("posts") or {}).items():
        posts.setdefault(k, dict(v, stale=True))
        # a metric that vanished or collapsed (>20 % drop) is a partial API answer, not a real fall: keep the last value
        cur = posts[k]
        for f in ("views", "likes", "avg_watch_s"):
            old_v, new_v = v.get(f), cur.get(f)
            if not old_v:
                continue
            if new_v is None or (f != "avg_watch_s" and new_v < 0.8 * old_v):
                cur[f] = old_v; cur["stale"] = True
    for k, v in (prev.get("retention") or {}).items():
        retention.setdefault(k, v)

    # ---------- totals, Buffer call counter ----------
    totals = {}
    for p in posts.values():
        t = totals.setdefault(p["platform"], {"posts": 0, "views": 0, "likes": 0, "comments": 0})
        t["posts"] += 1
        for f in ("views", "likes", "comments"):
            t[f] += p.get(f) or 0
    month = now.strftime("%Y-%m")
    pb = prev.get("buffer") or {}
    runs = (pb.get("stats_runs", 0) if pb.get("month") == month else 0) + 1
    buffer = {"month": month, "stats_runs": runs, "posts_sent": sent_this_month,
              "calls_estimated": runs + sent_this_month * 6, "limit_30d": 3000, "limit_24h": 600}
    paris = now.astimezone(dt.timezone(dt.timedelta(hours=1)))
    snap = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "date": paris.date().isoformat(), "followers": followers,
            "totals": totals, "posts": posts, "buffer": buffer, "calls": CALLS, "errors": ERRORS,
            "sources": "YouTube : API + Analytics · Facebook et Instagram : API Meta · TikTok, X : API Buffer"}
    json.dump(snap, open(os.path.join(a.out, "snapshot.json"), "w", encoding="utf-8"), ensure_ascii=False)
    # small side documents: meta/retention (curves) and daily/<date> (totals + followers, for the history chart)
    json.dump({"at": snap["at"], "curves": retention}, open(os.path.join(a.out, "retention.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"date": snap["date"], "at": snap["at"], "totals": totals, "followers": followers},
              open(os.path.join(a.out, "daily.json"), "w", encoding="utf-8"), ensure_ascii=False)

    for i in range(0, len(new_comments), 50):
        batch = [{"op": "set", "collection": "comments", "doc_id": cid, "data": d} for cid, d in new_comments[i:i + 50]]
        json.dump(batch, open(os.path.join(a.out, f"comments_new_{i // 50 + 1}.json"), "w", encoding="utf-8"), ensure_ascii=False)
    line = " · ".join(f"{p} {t['views']:,}".replace(",", " ") for p, t in sorted(totals.items(), key=lambda x: -x[1]["views"]))
    summary = f"Vues : {line}. Nouveaux commentaires : {len(new_comments)}. Buffer : ~{buffer['calls_estimated']}/3000 ce mois."
    if ERRORS:
        uniq = sorted(set(ERRORS)); snap["errors"] = uniq
        json.dump(snap, open(os.path.join(a.out, "snapshot.json"), "w", encoding="utf-8"), ensure_ascii=False)
        summary += " Échecs : " + " ; ".join(uniq[:4])
    open(os.path.join(a.out, "summary.txt"), "w", encoding="utf-8").write(summary)
    print(summary)


if __name__ == "__main__":
    main()
