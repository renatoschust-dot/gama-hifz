# GAMA HIFZ — učenje Kur'ana (besplatno, offline, samostalno)

Self-hosted aplikacija za **hifz** (učenje/memorisanje Kur'ana) koja radi na običnom
serveru ili računaru, **bez plaćenih servisa i bez API ključeva**.

- 📖 **114 sura / 6236 ajeta** — arapski (Uthmani), prijevod na **bosanskom** i engleskom
- 🎧 **Audio** (Alafasy, Husary) — javni izvori (everyayah.com)
- 🗣️ **TTS na bosanskom** — 3 motora sa automatskim fallbackom:
  **Google Cloud TTS** (Chirp3-HD, najprirodniji) → **Gemini TTS** → `edge-tts` (potpuno besplatno)
- 🎙️ **ASR provjera učenja** — `faster-whisper` (lokalno, CPU, int8, bez interneta)
- 🤖 **Opciono: „savjet“** — kratak savjet preko **bilo kog OpenAI-kompatibilnog endpointa**
  (npr. Ollama/vLLM lokalno, ili neki besplatni endpoint) — `HIFZ_MOTOR_URL`
- 📱 Radi kao **web aplikacija na telefonu** (jedan URL)

## Brzo pokretanje (Linux)

```bash
git clone https://github.com/renatoschust-dot/gama-hifz && cd gama-hifz
python3 -m pip install -r requirements.txt

python3 tools/build_db.py            # gradi hifz.db iz javnih izvora (bez ključeva)
bash tools/install_model.sh          # skida besplatni ASR model (Arabic, int8)

# (opciono) sve snimi lokalno -> posle radi 100% offline i trenutno:
python3 tools/prefetch_media.py --reciters alafasy,husary --tts --tts-engine auto --workers 6

python3 app.py                       # -> http://127.0.0.1:8085
```

Kao servis:

```bash
sudo cp -r . /opt/gama-hifz
sudo cp hifz.service /etc/systemd/system/
sudo systemctl enable --now gama-hifz
```

## API (headless)

| Ruta | Opis |
|---|---|
| `GET /` | web aplikacija |
| `GET /api/sure` | lista sura |
| `GET /api/ajet/<sura>/<ajet>` | tekst (ar/bs/en) |
| `GET /api/sura/<sura>` | cijela sura |
| `GET /api/audio?...` | audio ajeta (proxy/cache) |
| `GET /api/tts_bs?...` | bosanski TTS (edge-tts) |
| `GET /api/tts_sura?...` | TTS cijele sure |
| `GET /api/savjet` | savjet (traži `HIFZ_MOTOR_URL`) |
| `POST /api/check`, `/api/check_sura`, `/api/check_range` | ASR provjera učenja |
| `GET /api/progress` | napredak |

## Konfiguracija (env)

| Varijabla | Default | Opis |
|---|---|---|
| `HIFZ_PORT` | `8085` | port |
| `HIFZ_MOTOR_URL` | *(prazno)* | OpenAI-kompatibilan `/v1/chat/completions` za „savjet“ |
| `HIFZ_TTS_ENGINE` | `auto` | `auto` / `cloud` / `gemini` / `edge` |
| `CLOUD_TTS_KEY` | *(prazno)* | Google Cloud TTS ključ (GCP, `texttospeech`) — **najprirodniji glas** |
| `CLOUD_TTS_VOICE` | `hr-HR-Chirp3-HD-Charon` | Cloud glas (bs-BA ne postoji; hr-HR ≈ bosanski) |
| `GEMINI_TTS_KEY` | *(prazno)* | Gemini TTS ključ (govori bosanski nativno) |
| `HIFZ_TTS_VOICE` | `bs-BA-GoranNeural` | edge-tts glas (besplatno) |

## Zahtjevi

- Python 3.10+
- ~400 MB za ASR model, ~5 MB za bazu
- Radi na **ARM i x86**, bez GPU

## Licenca

MIT — vidi `LICENSE`. Tekst Kur'ana i prijevodi preuzimaju se iz javnih izvora;
audio se linkuje sa javnih servera (everyayah.com).
