# Security policy — gama-hifz

Report to **renato@gamatrade.ba** with `[gama-hifz-security]`.

## Scope

The app is a single stdlib HTTP server that reads a local `hifz.db` and calls optional
TTS/ASR providers. Things that matter:

- path traversal or arbitrary file read through a route (`/audio`, `/quran/…`);
- server-side request forgery: `HIFZ_MOTOR_URL` or a TTS URL is fetched on behalf of a caller;
- a template or JSON response that reflects unescaped user input;
- secrets in `hifz.db` or logs (`CLOUD_TTS_KEY`, `GEMINI_TTS_KEY` must never be echoed).

Not in scope: the content of the Qur'an or translations (report those upstream), and the
accuracy of ASR/translation models.

The app is meant for a trusted LAN or a single user's machine. There is no authentication
on the routes; exposing it directly to the internet is a deployment error, not a bug.
