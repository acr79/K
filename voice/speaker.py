"""Voice output — TTS, uses macOS say command (upgrade to neural TTS later)."""

import subprocess
import platform


# macOS voices — 'Siri' quality voices available on macOS 14+
MAC_VOICE = "Evan"   # natural-sounding male voice on macOS


def speak(text: str):
    """Speak text aloud."""
    if platform.system() == "Darwin":
        _speak_macos(text)
    else:
        _speak_fallback(text)


def _speak_macos(text: str):
    """Use macOS say command — works out of the box, no install needed."""
    # Clean text for voice (remove markdown)
    clean = _clean_for_voice(text)
    subprocess.run(["say", "-v", MAC_VOICE, clean], check=False)


def _speak_fallback(text: str):
    """Fallback TTS using pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(_clean_for_voice(text))
        engine.runAndWait()
    except ImportError:
        print(f"[TTS unavailable] {text}")


def _clean_for_voice(text: str) -> str:
    """Strip markdown and formatting that sounds bad when read aloud."""
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)   # bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)         # italic
    text = re.sub(r'#{1,6}\s', '', text)              # headers
    text = re.sub(r'`(.+?)`', r'\1', text)            # inline code
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # links
    text = re.sub(r'^\s*[-•]\s*', '', text, flags=re.MULTILINE)  # bullets
    return text.strip()
