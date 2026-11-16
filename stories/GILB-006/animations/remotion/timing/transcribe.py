"""Word timestamps for the approved narration (faster-whisper small, local cache, CPU)."""
import json, sys, subprocess
import numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
raw = subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
audio = np.frombuffer(raw, np.float32)
segs, info = m.transcribe(audio, language="en", word_timestamps=True, beam_size=5, vad_filter=False)
out = []
for s in segs:
    out.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                "words": [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)} for w in s.words]})
    print(f"{s.start:7.2f}-{s.end:7.2f}  {s.text.strip()}")
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
