#!/usr/bin/env python3
"""Predgenerisanje SVIH medija lokalno — aplikacija posle radi 100% offline i instant.

Snima:
  1) audio karija  -> data/audio_cache/<reciter>_<sura>_<ajet>.mp3   (everyayah.com, javno)
  2) bosanski TTS  -> data/tts_<sura>_<ajet>.mp3                     (edge-tts, besplatno)

Sve je resumable (preskace postojece) i moze se prekinuti/ponovo pokrenuti.

Primjeri:
  python3 tools/prefetch_media.py --reciters alafasy,husary --tts --workers 6
  python3 tools/prefetch_media.py --tts --limit 100          # proba na 100 ajeta
"""
import argparse, asyncio, os, sqlite3, sys, time, urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "hifz.db")
CACHE = os.path.join(HERE, "data", "audio_cache")
VOICE = os.environ.get("HIFZ_TTS_VOICE", "bs-BA-GoranNeural")


def rows(limit=0):
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    sql = "SELECT sura, ajet, tekst_bs, audio_alafasy, audio_husary FROM ajeti ORDER BY sura, ajet"
    if limit: sql += f" LIMIT {int(limit)}"
    return [dict(r) for r in con.execute(sql)]


def fetch(url, dest, tries=3):
    if os.path.exists(dest) and os.path.getsize(dest) > 512:
        return "skip"
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "gama-hifz/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r, open(dest + ".part", "wb") as f:
                f.write(r.read())
            os.replace(dest + ".part", dest)
            return "ok"
        except Exception:
            if i == tries - 1: return "err"
            time.sleep(1 + i)
    return "err"


def do_audio(reciters, items, workers):
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(CACHE, exist_ok=True)
    jobs = []
    for it in items:
        for r in reciters:
            u = it.get("audio_" + r)
            if u:
                jobs.append((r, it["sura"], it["ajet"], u, os.path.join(CACHE, f"{r}_{it['sura']}_{it['ajet']}.mp3")))
    done = ok = 0
    def work(j):
        nonlocal done, ok
        r = fetch(j[3], j[4]); done += 1
        if r == "ok": ok += 1
        if done % 200 == 0: print(f"  audio {done}/{len(jobs)} (novih {ok})", flush=True)
        return r
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, jobs))
    print(f"AUDIO gotovo: {len(jobs)} zadataka, novih {ok}", flush=True)


async def do_tts(items, concurrency=4):
    import edge_tts
    sem = asyncio.Semaphore(concurrency)
    done = [0]; ok = [0]
    async def one(it):
        out = os.path.join(HERE, "data", f"tts_{it['sura']}_{it['ajet']}.mp3")
        if os.path.exists(out) and os.path.getsize(out) > 512:
            done[0] += 1; return
        txt = it.get("tekst_bs")
        if not txt:
            done[0] += 1; return
        async with sem:
            for attempt in range(3):
                try:
                    await edge_tts.Communicate(txt, VOICE).save(out)
                    ok[0] += 1; break
                except Exception:
                    await asyncio.sleep(2.0 * (attempt + 1))
        done[0] += 1
        if done[0] % 100 == 0: print(f"  tts {done[0]}/{len(items)} (novih {ok[0]})", flush=True)
    await asyncio.gather(*(one(it) for it in items))
    print(f"TTS gotovo: {len(items)} ajeta, novih {ok[0]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reciters", default="alafasy,husary")
    ap.add_argument("--tts", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    if not os.path.exists(DB):
        sys.exit("nema hifz.db — pokreni tools/build_db.py prvo")
    items = rows(a.limit)
    print(f"ajeta: {len(items)} | reciteri: {a.reciters} | tts: {a.tts}", flush=True)
    t0 = time.time()
    rec = [x.strip() for x in a.reciters.split(",") if x.strip()]
    if rec: do_audio(rec, items, a.workers)
    if a.tts: asyncio.run(do_tts(items))
    print(f"UKUPNO {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
