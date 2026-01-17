#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio generation utilities for Pocket TTS.
"""

import logging
import time
from pathlib import Path


def generate_audio(model, voice_state, text, output_file):
    """Generate audio from text using the voice state"""
    try:
        print(f"Generating audio...")
        print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        
        if voice_state is None:
            raise RuntimeError("Voice state is empty; cannot generate audio")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        start = time.time()
        audio = model.generate_audio(voice_state, text)
        if audio is None:
            raise RuntimeError("Model returned no audio data")

        try:
            audio_size = int(audio.numel()) if hasattr(audio, "numel") else None
        except Exception:
            audio_size = None

        if audio_size == 0:
            raise RuntimeError("Model returned empty audio tensor")

        # Save audio
        import scipy.io.wavfile

        audio_numpy = audio.detach().cpu().numpy() if hasattr(audio, "detach") else audio
        logger = logging.getLogger("pocket_tts")
        logger.info(
            "Audio generated in %.2fs; dtype=%s; shape=%s",
            time.time() - start,
            getattr(audio_numpy, "dtype", "unknown"),
            getattr(audio_numpy, "shape", "unknown"),
        )
        scipy.io.wavfile.write(str(output_path), model.sample_rate, audio_numpy)

        if not output_path.exists() or output_path.stat().st_size == 0:
            raise RuntimeError(f"Audio file was not written: {output_path}")

        file_size = output_path.stat().st_size / 1024  # KB
        print(f"✓ Audio generated successfully!")
        print(f"✓ Saved to: {output_path} ({file_size:.1f} KB)")
        return str(output_path)
    except Exception as e:
        print(f"✗ Error generating audio: {e}")
        raise
