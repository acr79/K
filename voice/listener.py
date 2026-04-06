"""Voice input — Whisper STT, runs locally on Mac."""

import tempfile
import os
from ..core.config import WHISPER_MODEL


def listen(timeout: int = 10) -> str | None:
    """Record from microphone and transcribe. Returns text or None."""
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
        import whisper
    except ImportError:
        raise RuntimeError(
            "Voice dependencies not installed.\n"
            "Run: pip install openai-whisper sounddevice soundfile numpy"
        )

    SAMPLE_RATE = 16000
    print("Listening...", end="", flush=True)

    audio = sd.rec(int(timeout * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype="float32")
    sd.wait()
    print(" done.")

    # Trim silence
    audio = audio.flatten()
    if np.abs(audio).max() < 0.01:
        return None  # silence

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, SAMPLE_RATE)
        tmp_path = f.name

    try:
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(tmp_path, language="en")
        text = result["text"].strip()
        return text if text else None
    finally:
        os.unlink(tmp_path)
