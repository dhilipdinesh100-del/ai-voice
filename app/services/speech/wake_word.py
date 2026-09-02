from typing import Optional, Callable
from app.logging_config import logger

class WakeWordService:
    """
    WakeWordService provides an extensible abstraction for voice activation 
    (e.g., Porcupine, OpenWakeWord, or browser-based keyword spotting).
    Per SPECS.md Section 11: Real wake-word engines can be plugged in without
    rewriting the voice pipeline.
    """
    def __init__(self, wake_word: str = "Hey Nova"):
        self.wake_word = wake_word
        self.is_active = False
        self._callback: Optional[Callable] = None

    def start_listening(self, callback: Callable):
        self.is_active = True
        self._callback = callback
        logger.info("WakeWordService armed for phrase: '%s'", self.wake_word)

    def stop_listening(self):
        self.is_active = False
        self._callback = None
        logger.info("WakeWordService disarmed.")

    def trigger(self):
        if self.is_active and self._callback:
            logger.info("Wake word detected: '%s'", self.wake_word)
            self._callback()

wake_word_service = WakeWordService()
