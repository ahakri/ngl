#!/usr/bin/env bash
# Re-creates the production toolchain in a fresh container (idempotent).
set -e
if ! [ -x /opt/bpyenv/bin/python ]; then
  uv venv -p 3.11 /opt/bpyenv && VIRTUAL_ENV=/opt/bpyenv uv pip install bpy
fi
if ! dpkg -s espeak-ng >/dev/null 2>&1; then
  apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    libegl1 libegl-mesa0 libgl1-mesa-dri libgles2 libxi6 libxxf86vm1 libxfixes3 \
    libxrender1 libxkbcommon0 libsm6 espeak-ng sox fonts-dejavu fonts-liberation
fi
mkdir -p /opt/tts
[ -f /opt/tts/kokoro-v1.0.onnx ] || curl -sL -o /opt/tts/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -f /opt/tts/voices-v1.0.bin ] || curl -sL -o /opt/tts/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
if ! [ -x /opt/ttsenv/bin/python ]; then
  uv venv -p 3.12 /opt/ttsenv && VIRTUAL_ENV=/opt/ttsenv uv pip install kokoro-onnx soundfile
fi
echo "toolchain ready"
mkdir -p /usr/local/share/fonts/studio && cp "$(dirname "$0")"/fonts/*.ttf /usr/local/share/fonts/studio/ && fc-cache -f >/dev/null
