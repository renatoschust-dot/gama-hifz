#!/usr/bin/env bash
# Skida ASR model (tarteel-base-ar-ct2, besplatan) u ./data/models — bez kljuceva.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)/data/models"
mkdir -p "$DIR"
python3 - <<'PY'
import os
from faster_whisper import WhisperModel
d = os.environ.get("HIFZ_MODELS", "data/models")
m = WhisperModel("tarteel-ai/whisper-base-ar-quran", device="cpu", compute_type="int8", download_root=d)
print("Model spreman u:", d)
PY
