#!/bin/sh
# Mix the untouched narration with the original music bed and effects -> public/mix_v1.wav
# Narration: dual-mono at unity (same as the narration-only draft). Music -9 dB, effects -4 dB,
# master -1 dB, then a true-peak-safe limiter at -1.5 dBFS.
cd "$(dirname "$0")/.."
MUSIC_DB=${MUSIC_DB:--9}
SFX_DB=${SFX_DB:--4}
ffmpeg -y -hide_banner -loglevel error \
  -i public/narration_v1.wav -i public/music_bed_v1.wav -i public/sfx_v1.wav \
  -filter_complex "[0:a]pan=stereo|c0=c0|c1=c0[n];[1:a]volume=${MUSIC_DB}dB[m];[2:a]volume=${SFX_DB}dB[s];\
[n][m][s]amix=inputs=3:normalize=0:duration=longest,volume=-1dB,aresample=192000,alimiter=limit=0.84:attack=1:release=60:level=disabled,aresample=48000" \
  -c:a pcm_s24le public/mix_v1.wav
