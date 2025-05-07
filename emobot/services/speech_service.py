"""
Speech service for the emobot assistant.
Handles speech recognition and synthesis.
"""
import os
import tempfile
import logging
from typing import Optional, Tuple
import io
import speech_recognition as sr
from pydub import AudioSegment
import time

from emobot.core.config import STT_ENGINE, TTS_ENGINE, logger

class SpeechService:
    """Service for speech recognition and synthesis."""
    
    def __init__(self):
        """Initialize the speech service."""
        self.recognizer = sr.Recognizer()
        
        # Adjust recognition parameters for better accuracy
        self.recognizer.energy_threshold = 300  # Energy level threshold for speech detection
        self.recognizer.dynamic_energy_threshold = True  # Adapt to ambient noise
        self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio to consider a phrase complete
        
        # Maximum number of recognition attempts
        self.max_attempts = 3
    
    def convert_ogg_to_wav(self, ogg_path: str) -> str:
        """Convert OGG audio file to WAV format for speech recognition.
        
        Args:
            ogg_path: Path to OGG audio file
            
        Returns:
            Path to converted WAV file
        """
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name
        
        try:
            # Convert OGG to WAV
            audio = AudioSegment.from_ogg(ogg_path)
            # Normalize audio to improve recognition
            normalized_audio = self._normalize_audio(audio)
            normalized_audio.export(temp_wav_path, format="wav")
            logger.info(f"Converted OGG to WAV: {temp_wav_path}")
            return temp_wav_path
        except Exception as e:
            logger.error(f"Error converting OGG to WAV: {e}")
            if os.path.exists(temp_wav_path):
                os.unlink(temp_wav_path)
            raise
    
    def _normalize_audio(self, audio: AudioSegment) -> AudioSegment:
        """Normalize audio to improve recognition.
        
        Args:
            audio: Audio segment to normalize
            
        Returns:
            Normalized audio segment
        """
        # Ensure consistent volume level
        target_dBFS = -20.0
        change_in_dBFS = target_dBFS - audio.dBFS
        normalized_audio = audio.apply_gain(change_in_dBFS)
        
        # Convert to mono if stereo (improves speech recognition)
        if normalized_audio.channels > 1:
            normalized_audio = normalized_audio.set_channels(1)
        
        # Set sample rate to 16kHz (often better for speech recognition)
        normalized_audio = normalized_audio.set_frame_rate(16000)
        
        return normalized_audio
    
    def speech_to_text(self, audio_path: str) -> str:
        """Convert speech to text using the configured STT engine.
        
        Args:
            audio_path: Path to audio file (WAV format)
            
        Returns:
            Transcribed text
        """
        logger.info(f"Transcribing audio: {audio_path}")
        
        # Multiple recognition attempts with different engines
        errors = []
        
        # Try primary engine first
        try:
            text = self._attempt_recognition(audio_path)
            if text and text.strip():
                return text.strip()
        except Exception as e:
            errors.append(f"Primary engine error: {e}")
            
        # Try fallback engine
        try:
            text = self._attempt_recognition(audio_path, use_fallback=True)
            if text and text.strip():
                return text.strip()
        except Exception as e:
            errors.append(f"Fallback engine error: {e}")
        
        # If we get here, both engines failed
        error_msg = "; ".join(errors)
        logger.error(f"All speech recognition attempts failed: {error_msg}")
        raise ValueError("Could not transcribe audio after multiple attempts")
    
    def _attempt_recognition(self, audio_path: str, use_fallback: bool = False) -> str:
        """Attempt speech recognition with multiple retries.
        
        Args:
            audio_path: Path to audio file (WAV format)
            use_fallback: Whether to use fallback engine
            
        Returns:
            Transcribed text or empty string if failed
        """
        engine = "whisper" if use_fallback else STT_ENGINE.lower()
        logger.info(f"Attempting recognition with {engine} engine")
        
        for attempt in range(self.max_attempts):
            try:
                with sr.AudioFile(audio_path) as source:
                    # Adjust for ambient noise and record
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio_data = self.recognizer.record(source)
                    
                    # Use selected engine
                    if engine == "google":
                        text = self.recognizer.recognize_google(audio_data)
                    elif engine == "whisper":
                        try:
                            text = self.recognizer.recognize_whisper(audio_data)
                        except (AttributeError, ImportError):
                            logger.warning("Whisper not available, falling back to Google")
                            text = self.recognizer.recognize_google(audio_data)
                    else:
                        # Default to Google
                        text = self.recognizer.recognize_google(audio_data)
                    
                    if text and text.strip():
                        logger.info(f"Transcribed text (attempt {attempt+1}): {text}")
                        return text
                    
                    logger.warning(f"Empty transcription on attempt {attempt+1}")
                    
            except sr.UnknownValueError:
                logger.warning(f"Speech not understood (attempt {attempt+1})")
                # Wait briefly before retry
                time.sleep(0.5)
                continue
            except sr.RequestError as e:
                logger.error(f"Service request error (attempt {attempt+1}): {e}")
                raise
            except Exception as e:
                logger.error(f"Recognition error (attempt {attempt+1}): {e}")
                raise
        
        return ""
    
    def text_to_speech(self, text: str, output_path: Optional[str] = None) -> str:
        """Convert text to speech using the configured TTS engine.
        
        Args:
            text: Text to convert to speech
            output_path: Optional output path for the audio file
            
        Returns:
            Path to the generated audio file
        """
        logger.info(f"Converting text to speech: {text[:50]}...")
        
        # This is a placeholder - actual implementation would depend on
        # which TTS engines you want to integrate (Google TTS, ElevenLabs, etc.)
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                output_path = temp_audio.name
        
        logger.warning("TTS functionality not yet implemented")
        
        return output_path

    def test_speech_recognition(self, wav_path: str) -> Tuple[bool, str]:
        """Test speech recognition on a WAV file.
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Tuple of (success, transcribed_text or error_message)
        """
        try:
            text = self.speech_to_text(wav_path)
            logger.info(f"Test transcription: {text}")
            return True, text
        except Exception as e:
            logger.error(f"Test transcription failed: {e}")
            return False, str(e)