import os

from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

_api_key = os.getenv("ELEVENLABS_API_KEY")
_client = ElevenLabs(api_key=_api_key) if _api_key else None
_voice_id = os.getenv("ELEVENLABS_VOICE_ID")
_model_id = os.getenv("ELEVENLABS_TTS_MODEL")


def _get_voice_profile():
    try:
        stability = float(os.getenv("ELEVENLABS_STABILITY", "0.60"))
        similarity = float(os.getenv("ELEVENLABS_SIMILARITY", "0.60"))
        style = float(os.getenv("ELEVENLABS_STYLE", "0.20"))
        speed = float(os.getenv("ELEVENLABS_SPEED", "1.00"))
    except ValueError:
        stability, similarity, style, speed = 0.60, 0.60, 0.20, 1.00

    return {
        "stability": max(0.0, min(1.0, stability)),
        "similarity_boost": max(0.0, min(1.0, similarity)),
        "style": max(0.0, min(1.0, style)),
        "speed": max(0.7, min(1.3, speed)),
    }


def speech_to_text(audio_file):
    if not _client:
        return ""
    result = _client.speech_to_text.convert(
        file=audio_file,
        model_id=os.getenv("ELEVENLABS_STT_MODEL", "scribe_v1"),
    )
    return result.text


def text_to_speech(text):
    if not _client:
        return None

    voice_profile = _get_voice_profile()
    voice_settings = {
        "stability": voice_profile["stability"],
        "similarity_boost": voice_profile["similarity_boost"],
        "style": voice_profile["style"],
        "use_speaker_boost": True,
    }

    try:
        audio = _client.text_to_speech.convert(
            voice_id=_voice_id,
            text=text,
            model_id=_model_id,
            output_format="mp3_44100_128",
            voice_settings=voice_settings,
            speed=voice_profile["speed"],
        )
    except TypeError:
        audio = _client.text_to_speech.convert(
            voice_id=_voice_id,
            text=text,
            model_id=_model_id,
            output_format="mp3_44100_128",
            voice_settings=voice_settings,
        )

    return b"".join(audio)
