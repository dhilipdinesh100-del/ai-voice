import uuid
import math
import struct
import wave
from pathlib import Path
from typing import Optional
from app.config import settings
from app.logging_config import logger

class TextToSpeechProvider:
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_format: str = "mp3"
    ) -> Path:
        raise NotImplementedError

class OpenAITTSProvider(TextToSpeechProvider):
    def __init__(self, api_key: str, model: str = "tts-1"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_format: str = "mp3"
    ) -> Path:
        voice = voice or settings.OPENAI_TTS_VOICE or "alloy"
        output_path = settings.AUDIO_DIR / f"nova_speech_{uuid4_hex()}.mp3"
        
        # Clamp speed between 0.25 and 4.0 as per OpenAI API specs
        speed_clamped = max(0.25, min(4.0, float(speed)))
        
        with self.client.audio.speech.with_streaming_response.create(
            model=self.model,
            voice=voice,
            input=text,
            speed=speed_clamped,
            response_format="mp3"
        ) as response:
            response.stream_to_file(output_path)
            
        return output_path

class SynthesizedFallbackTTSProvider(TextToSpeechProvider):
    """
    Generates a valid audio waveform file (PCM WAV) using Python's standard library wave.
    Provides a real, audio-reactive harmonic chime so frontend audio visualizer and playback
    work even when an OpenAI API key is not yet configured.
    """
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_format: str = "wav"
    ) -> Path:
        output_path = settings.AUDIO_DIR / f"nova_fallback_{uuid4_hex()}.wav"
        
        # Generate an audio pulse based on text length (between 1.5 and 4.0 seconds)
        duration_sec = max(1.5, min(4.0, len(text.split()) * 0.35))
        sample_rate = 22050
        total_samples = int(duration_sec * sample_rate)
        
        # Generate a gentle pleasant futuristic chord (440Hz A4 + 554Hz C#5 + 659Hz E5)
        frequencies = [440.0, 554.37, 659.25]
        
        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(sample_rate)
            
            frames = bytearray()
            for i in range(total_samples):
                t = float(i) / sample_rate
                # Envelope: smooth attack and gentle decay
                envelope = math.sin(math.pi * (i / total_samples))
                sample_val = 0.0
                for f in frequencies:
                    sample_val += math.sin(2.0 * math.pi * f * t)
                sample_val = (sample_val / len(frequencies)) * envelope * 16000.0
                val_int = int(max(-32767, min(32767, sample_val)))
                frames.extend(struct.pack("<h", val_int))
                
            wav_file.writeframes(frames)
            
        logger.info("Generated fallback audio at %s (duration: %.2fs)", output_path.name, duration_sec)
        return output_path

def uuid4_hex() -> str:
    return uuid.uuid4().hex

def get_tts_provider() -> TextToSpeechProvider:
    if settings.has_real_openai_key:
        try:
            return OpenAITTSProvider(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_TTS_MODEL
            )
        except Exception as e:
            logger.error("Failed to initialize OpenAI TTS provider: %s", e)
    return SynthesizedFallbackTTSProvider()
