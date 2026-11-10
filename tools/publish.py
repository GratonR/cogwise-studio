#!/usr/bin/env python3
"""Publish one validated short to every platform of a channel, deterministically.

Why a script: the scheduled tasks used to improvise each API call; the same steps written once are
faster, auditable and identical for every channel. The caller (a person's click relayed by a task, or
Claude in a chat) is responsible for the "go"; this script only does what it is told.

  python3 tools/publish.py --draft draft.json --shared keys.env --chan-keys chan_keys.txt \
      --out result.json [--platforms youtube,facebook,instagram,tiktok,x] [--dry-run]

--draft      the drafts/<slug> document (JSON): video (raw URL), youtube{title,description,tags},
             captions{instagram,tiktok,facebook,x}, pinned_comment, court/titre.
--shared     KEY=value file with YT_CLIENT_ID, YT_CLIENT_SECRET (OAuth app shared by all channels).
--yt-refresh optional file with just the YouTube refresh token; --yt-category optional categoryId.
--chan-keys  KEY=value file of the channel: YT_CHANNEL_ID, YT_REFRESH_TOKEN, FB_PAGE_ID, FB_PAGE_TOKEN,
             BUFFER_API_KEY, BUFFER_ORG_ID (for Cogwise, the shared file holds them all: pass it twice).
Writes result.json = {links:{platform:url}, ids:{...}, errors:{platform:msg}, pinned:{platform:bool}}.
Never prints a key.
"""
import argparse, json, sys, time, urllib.error, urllib.parse, urllib.request

G = "https://graph.facebook.com/v21.0/"
BUFFER = "https://api.buffer.com"


def read_keys(path):
    out = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip().replace("\\_", "_")
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def http(url, data=None, headers=None, method=None, timeout=300):
    if isinstance(data, dict):
        data = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method or ("POST" if data is not None else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, dict(r.headers), (json.loads(body) if body[:1] in (b"{", b"[") else body)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")[:500]


def short(err):
    return str(err).replace("\n", " ")[:300]


# ---------------- YouTube ----------------
def youtube(d, K, video, res, pin):
    st, _, tok = http("https://oauth2.googleapis.com/token", {"client_id": K["YT_CLIENT_ID"], "client_secret": K["YT_CLIENT_SECRET"],
                                                             "refresh_token": K["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"})
    if st != 200:
        raise RuntimeError(("autorisation YouTube à renouveler" if "invalid_grant" in str(tok) else "jeton YouTube refusé") + f" ({st})")
    auth = {"Authorization": "Bearer " + tok["access_token"]}
    y = d.get("youtube") or {}
    title = (y.get("title") or d.get("titre") or d.get("court"))[:100]
    # duplicate guard: same title already in the channel's latest uploads
    st, _, ch = http(f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", headers=auth)
    try:
        up = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        st, _, pl = http(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&maxResults=15&playlistId={up}", headers=auth)
        for it in (pl.get("items") or []) if isinstance(pl, dict) else []:
            if it["snippet"]["title"].strip().lower() == title.strip().lower():
                vid = it["snippet"]["resourceId"]["videoId"]
                res["links"]["youtube"] = "https://youtube.com/shorts/" + vid; res["ids"]["youtube"] = vid; res["notes"].append("YouTube : déjà en ligne, pas de doublon")
                break
    except Exception:
        pass
    if "youtube" not in res["links"]:
        meta = {"snippet": {"title": title, "description": y.get("description", ""), "tags": y.get("tags", []), "categoryId": str(y.get("categoryId") or K.get("YT_CATEGORY") or "28"), "defaultLanguage": "en", "defaultAudioLanguage": "en"},
                "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False}}
        st, h, b = http("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", json.dumps(meta).encode(),
                        {**auth, "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(len(video))})
        loc = h.get("Location") or h.get("location")
        if not loc:
            raise RuntimeError(f"YouTube : session d'envoi refusée ({st}) {short(b)}")
        st, _, b = http(loc, video, {**auth, "Content-Type": "video/mp4"}, method="PUT", timeout=900)
        if st not in (200, 201):
            raise RuntimeError(f"YouTube : envoi échoué ({st}) {short(b)}")
        res["links"]["youtube"] = "https://youtube.com/shorts/" + b["id"]; res["ids"]["youtube"] = b["id"]
    if pin:
        body = {"snippet": {"videoId": res["ids"]["youtube"], "topLevelComment": {"snippet": {"textOriginal": pin}}}}
        st, _, b = http("https://www.googleapis.com/youtube/v3/commentThreads?part=snippet", json.dumps(body).encode(), {**auth, "Content-Type": "application/json"})
        res["pinned"]["youtube"] = st in (200, 201)


# ---------------- Facebook Reel ----------------
def facebook(d, K, video, res, pin):
    T, P = K["FB_PAGE_TOKEN"], K["FB_PAGE_ID"]
    st, _, s = http(G + P + "/video_reels", {"upload_phase": "start", "access_token": T})
    if st != 200:
        raise RuntimeError(f"Facebook : démarrage refusé ({st}) {short(s)}")
    vid = s["video_id"]
    st, _, u = http(f"https://rupload.facebook.com/video-upload/v21.0/{vid}", video, {"Authorization": "OAuth " + T, "offset": "0", "file_size": str(len(video))})
    if st != 200:
        raise RuntimeError(f"Facebook : envoi échoué ({st}) {short(u)}")
    cap = (d.get("captions") or {}).get("facebook", "")
    st, _, f = http(G + P + "/video_reels", {"upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED", "description": cap, "access_token": T})
    if st != 200:
        raise RuntimeError(f"Facebook : publication refusée ({st}) {short(f)}")
    for _ in range(16):
        st, _, s = http(G + vid + "?fields=status&access_token=" + urllib.parse.quote(T))
        vs = (s.get("status") or {}).get("video_status") if isinstance(s, dict) else None
        if vs in ("ready", "error"):
            break
        time.sleep(15)
    res["links"]["facebook"] = "https://www.facebook.com/reel/" + vid; res["ids"]["facebook"] = vid
    if pin:
        st, _, b = http(G + vid + "/comments", {"message": pin, "access_token": T})
        res["pinned"]["facebook"] = st == 200


# ---------------- Buffer: Instagram, TikTok, X ----------------
def buffer_q(K, query, variables=None):
    st, _, b = http(BUFFER, json.dumps({"query": query, "variables": variables or {}}).encode(),
                    {"Authorization": "Bearer " + K["BUFFER_API_KEY"], "Content-Type": "application/json"})
    if st != 200 or not isinstance(b, dict) or b.get("errors"):
        raise RuntimeError(f"Buffer ({st}) {short(b)}")
    return b["data"]


def buffer_all(d, K, platforms, res):
    org = K.get("BUFFER_ORG_ID") or buffer_q(K, "query { account { organizations { id } } }")["account"]["organizations"][0]["id"]
    chans = buffer_q(K, 'query($o: OrganizationId!){ channels(input:{organizationId:$o}) { id name service isDisconnected } }', {"o": org})["channels"]
    caps = d.get("captions") or {}
    meta = {"tiktok": {"tiktok": {"title": (d.get("court") or d.get("titre") or "")[:90]}}, "instagram": {"instagram": {"type": "reel", "shouldShareToFeed": True}}, "twitter": None}
    want = {"instagram": "instagram", "tiktok": "tiktok", "x": "twitter"}
    M = ("mutation($input: CreatePostInput!){ createPost(input:$input){ __typename ... on PostActionSuccess { post { id externalLink status } } "
         "... on InvalidInputError { message } ... on LimitReachedError { message } ... on UnexpectedError { message } ... on UnauthorizedError { message } } }")
    sent = {}
    for p in platforms:
        if p not in want:
            continue
        c = next((c for c in chans if c["service"] == want[p]), None)
        if not c:
            res["errors"][p] = "pas de compte " + p + " dans Buffer"; continue
        if c.get("isDisconnected"):
            res["errors"][p] = "compte " + p + " déconnecté dans Buffer (à reconnecter)"; continue
        inp = {"channelId": c["id"], "text": caps.get(p, ""), "mode": "shareNow", "schedulingType": "automatic", "needsApproval": False,
               "assets": [{"video": {"url": d["video"]}}]}
        if meta[want[p]]:
            inp["metadata"] = meta[want[p]]
        try:
            r = buffer_q(K, M, {"input": inp})["createPost"]
        except Exception as e:
            res["errors"][p] = short(e); continue
        if r.get("__typename") != "PostActionSuccess":
            res["errors"][p] = r.get("message") or r.get("__typename"); continue
        sent[p] = r["post"]
    # poll until sent / error (max ~4 min)
    for _ in range(16):
        pend = [p for p, x in sent.items() if x.get("status") not in ("sent", "error")]
        if not pend:
            break
        time.sleep(15)
        try:
            edges = buffer_q(K, 'query($o: OrganizationId!){ posts(first:20, input:{organizationId:$o}) { edges { node { id status externalLink error { message } } } } }', {"o": org})["posts"]["edges"]
        except Exception:
            continue
        by = {e["node"]["id"]: e["node"] for e in edges}
        for p in pend:
            n = by.get(sent[p]["id"])
            if n:
                sent[p] = {**sent[p], **n}
    for p, x in sent.items():
        if x.get("status") == "sent":
            res["links"][p] = x.get("externalLink") or ""; res["ids"][p] = x["id"]
        else:
            res["errors"][p] = ((x.get("error") or {}).get("message") if isinstance(x.get("error"), dict) else None) or ("statut " + str(x.get("status")))


def instagram_pin(K, res, pin):
    T, P = K["FB_PAGE_TOKEN"], urllib.parse.quote(K["FB_PAGE_TOKEN"])
    st, _, pg = http(G + K["FB_PAGE_ID"] + "?fields=instagram_business_account&access_token=" + P)
    ig = ((pg or {}).get("instagram_business_account") or {}).get("id") if isinstance(pg, dict) else None
    if not ig:
        return
    st, _, m = http(G + ig + "/media?fields=id,permalink,timestamp&limit=5&access_token=" + P)
    items = (m or {}).get("data") or [] if isinstance(m, dict) else []
    link = res["links"].get("instagram") or ""
    target = next((x for x in items if link and x.get("permalink", "").rstrip("/") == link.rstrip("/")), items[0] if items else None)
    if not target:
        return
    res["links"]["instagram"] = res["links"].get("instagram") or target.get("permalink")
    st, _, b = http(G + target["id"] + "/comments", {"message": pin, "access_token": T})
    res["pinned"]["instagram"] = st == 200


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True); ap.add_argument("--shared", required=True); ap.add_argument("--chan-keys", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--platforms", default="youtube,facebook,instagram,tiktok,x")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pin", action="store_true", help="also post draft.pinned_comment under the video (off by default since 10 Nov: no API can pin it, the manual pinning cost too much)")
    ap.add_argument("--yt-category", help="YouTube categoryId (Cogwise 27 Education, BeepMelody 28 Science & Technology); default 28 or draft.youtube.categoryId")
    ap.add_argument("--yt-refresh", help="file holding only the channel's YouTube refresh token (Cogwise keeps it apart from its keys file)")
    a = ap.parse_args()
    d = json.load(open(a.draft, encoding="utf-8"))
    d = d.get("data", d)
    K = {**read_keys(a.shared), **read_keys(a.chan_keys)}
    if a.yt_refresh:
        raw = open(a.yt_refresh, encoding="utf-8-sig").read().strip()
        for line in raw.splitlines():   # accepts a bare token or a "YT_REFRESH_TOKEN=..." line
            line = line.strip()
            if line.startswith("YT_REFRESH_TOKEN="):
                raw = line.split("=", 1)[1].strip().strip('"'); break
        K["YT_REFRESH_TOKEN"] = raw.splitlines()[0].strip() if "\n" in raw else raw
    if a.yt_category:
        K["YT_CATEGORY"] = a.yt_category
    plats = [p.strip() for p in a.platforms.split(",") if p.strip()]
    res = {"slug": d.get("slug"), "links": {}, "ids": {}, "errors": {}, "pinned": {}, "notes": []}
    if a.dry_run:
        res["notes"].append("dry-run : clés présentes " + ", ".join(sorted(k for k in K if K[k])))
        json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False)); return
    st, _, video = http(d["video"], timeout=300)
    if st != 200 or not isinstance(video, bytes):
        raise SystemExit(f"vidéo introuvable ({st}) : {d['video']}")
    pin = (d.get("pinned_comment") or "") if a.pin else ""
    for p, fn in (("youtube", youtube), ("facebook", facebook)):
        if p in plats:
            try:
                fn(d, K, video, res, pin)
            except Exception as e:
                res["errors"][p] = short(e)
    if any(p in plats for p in ("instagram", "tiktok", "x")):
        if K.get("BUFFER_API_KEY"):
            try:
                buffer_all(d, K, plats, res)
            except Exception as e:
                for p in ("instagram", "tiktok", "x"):
                    if p in plats and p not in res["links"]:
                        res["errors"][p] = short(e)
        else:
            for p in ("instagram", "tiktok", "x"):
                if p in plats:
                    res["errors"][p] = "pas de clé Buffer pour cette chaîne"
    if pin and "instagram" in res["links"]:
        try:
            instagram_pin(K, res, pin)
        except Exception as e:
            res["notes"].append("épinglage Instagram : " + short(e))
    json.dump(res, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: res[k] for k in ("links", "errors", "pinned", "notes")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
