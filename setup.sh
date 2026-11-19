#!/usr/bin/env bash
# One-time setup for a fresh workspace: Python packages + Hindi voice model.
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q skia-python soundfile pillow numpy coqui-tts torch torchaudio torchcodec 2>&1 | grep -v -i warning || true
which ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
if [ ! -f models/ai4b/hi/fastpitch/best_model.pth ]; then
  mkdir -p models/ai4b && cd models/ai4b
  curl -sSL -o hi.zip https://github.com/AI4Bharat/Indic-TTS/releases/download/v1-checkpoints-release/hi.zip
  unzip -q hi.zip && rm hi.zip && cd ../..
fi
python3 - <<'PY'
import json, os
b = os.path.abspath('models/ai4b/hi/fastpitch')
c = json.load(open(b + '/config.json'))
c['speakers_file'] = b + '/speakers.pth'; c['model_args']['speakers_file'] = b + '/speakers.pth'
json.dump(c, open(b + '/config_fixed.json', 'w'))
print('voice model ready')
PY
