#!/usr/bin/env python3
"""Gradnja hifz.db iz besplatnih, javnih izvora (bez kljuceva).

Izvori:
  - Tekst:   https://api.alquran.cloud  (quran-uthmani, bs.korkut, en.sahih)
  - Audio:   https://everyayah.com      (Alafasy_128kbps / Husary_128kbps) — samo URL-ovi

Rezultat: ./hifz.db sa tabelama sure, ajeti, meta, savjet_cache, napredak.
Pokretanje:  python3 tools/build_db.py
"""
import os, json, sqlite3, urllib.request, time

API = "https://api.alquran.cloud/v1"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(HERE, "hifz.db")


def get(url, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(1.5 * (i + 1))


def schema(con):
    con.executescript("""
    CREATE TABLE IF NOT EXISTS sure (broj INTEGER PRIMARY KEY, naziv_ar TEXT, naziv_translit TEXT,
        naziv_bs TEXT, prijevod_naziva TEXT, broj_ajeta INTEGER, tip TEXT, redoslijed_objave INTEGER);
    CREATE TABLE IF NOT EXISTS ajeti (id INTEGER PRIMARY KEY, sura INTEGER, ajet INTEGER,
        tekst_ar TEXT, tekst_bs TEXT, tekst_en TEXT, broj_rijeci INTEGER, juz INTEGER, page INTEGER,
        audio_alafasy TEXT, audio_husary TEXT);
    CREATE TABLE IF NOT EXISTS meta (k TEXT PRIMARY KEY, v TEXT);
    CREATE TABLE IF NOT EXISTS savjet_cache (k TEXT PRIMARY KEY, savjet TEXT, ts INTEGER);
    CREATE TABLE IF NOT EXISTS napredak (id INTEGER PRIMARY KEY AUTOINCREMENT, cid TEXT, ts INTEGER,
        mod TEXT, sura INT, ajet INT, skor INT, n INT);
    CREATE INDEX IF NOT EXISTS idx_ajeti_sura ON ajeti(sura, ajet);
    """)


def main():
    con = sqlite3.connect(DB); schema(con)
    meta = get(f"{API}/meta")
    if meta.get("data"):
        con.execute("INSERT OR REPLACE INTO meta(k,v) VALUES('meta',?)", (json.dumps(meta["data"], ensure_ascii=False),))
    for s in get(f"{API}/surah").get("data", []):
        con.execute("INSERT OR REPLACE INTO sure VALUES(?,?,?,?,?,?,?,?)", (
            s["number"], s.get("name", ""), s.get("englishName", ""), s.get("englishNameTranslation", ""),
            s.get("englishNameTranslation", ""), s.get("numberOfAyahs", 0),
            "mekkanska" if s.get("revelationType") == "Meccan" else "medinska", 0))
    ar = {}
    for ed in ("quran-uthmani", "bs.korkut", "en.sahih"):
        d = get(f"{API}/quran/{ed}").get("data", {})
        for s in d.get("surahs", []):
            for a in s.get("ayahs", []):
                key = (s["number"], a["numberInSurah"])
                ar.setdefault(key, {})[ed] = a.get("text", "")
                ar[key]["juz"] = a.get("juz"); ar[key]["page"] = a.get("page")
    for (sura, ajet), v in sorted(ar.items()):
        alafasy = f"https://everyayah.com/data/Alafasy_128kbps/{sura:03d}{ajet:03d}.mp3"
        husary = f"https://everyayah.com/data/Husary_128kbps/{sura:03d}{ajet:03d}.mp3"
        txt = v.get("quran-uthmani", "")
        con.execute("INSERT OR REPLACE INTO ajeti VALUES(?,?,?,?,?,?,?,?,?,?,?)", (
            sura * 1000 + ajet, sura, ajet, txt, v.get("bs.korkut"), v.get("en.sahih"),
            len(txt.split()), v.get("juz"), v.get("page"), alafasy, husary))
    con.commit()
    print("OK:", con.execute("select count(*) from ajeti").fetchone()[0], "ajeta,",
          con.execute("select count(*) from sure").fetchone()[0], "sura")


if __name__ == "__main__":
    main()
