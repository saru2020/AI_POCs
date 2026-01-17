#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio processing utilities for Pocket TTS.
"""

import os
import subprocess
import tempfile
import wave
from pathlib import Path

from logging_utils import log_audio_info


def trim_wav_if_needed(input_path, max_seconds):
    """Trim WAV file to max_seconds if longer. Returns new path or original."""
    import logging
    logger = logging.getLogger("pocket_tts")
    
    if not max_seconds or max_seconds <= 0:
        return input_path

    try:
        with wave.open(str(input_path), "rb") as wav:
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            duration = frames / float(sample_rate) if sample_rate else 0.0
    except wave.Error as exc:
        logger.warning("Unable to read WAV duration for trimming: %s", exc)
        return input_path
    except OSError as exc:
        logger.warning("Unable to open WAV for trimming: %s", exc)
        return input_path

    if duration <= max_seconds:
        logger.info("Voice prompt duration %.2fs <= max %.2fs, no trim.", duration, max_seconds)
        return input_path

    logger.info("Trimming voice prompt from %.2fs to %.2fs", duration, max_seconds)
    temp_handle = tempfile.NamedTemporaryFile(
        suffix=".wav",
        prefix=f"{Path(input_path).stem}_trimmed_",
        delete=False,
        dir="/tmp",
    )
    output_path = Path(temp_handle.name)
    temp_handle.close()

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-t", str(max_seconds),
        "-ar", "24000",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        str(output_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        logger.warning("Trim failed: %s", result.stderr[:500] if result.stderr else "unknown error")
        return input_path

    if not output_path.exists() or output_path.stat().st_size == 0:
        logger.warning("Trim output missing or empty, using original.")
        return input_path

    log_audio_info(str(output_path), label="trimmed prompt")
    return str(output_path)


def convert_audio_to_wav(input_file, output_file=None):
    """Convert audio file to WAV format using ffmpeg.
    
    The pocket_tts library requires WAV format for voice cloning.
    This function converts M4A, MP3, FLAC, OGG and other formats to WAV.
    
    Args:
        input_file: Path to the input audio file
        output_file: Optional path for output WAV file. If None, creates a temp file.
    
    Returns:
        Path to the converted WAV file
    """
    import logging
    logger = logging.getLogger("pocket_tts")
    
    input_path = Path(input_file)

    # Check if already a WAV file and compatible with expected format
    if input_path.suffix.lower() == '.wav':
        wav_info = log_audio_info(str(input_path), label="input")
        if wav_info:
            channels, sample_width, sample_rate = wav_info
            if channels == 1 and sample_width == 2 and sample_rate == 24000:
                print(f"✓ Audio file is already in WAV format: {input_file}")
                logger.info("WAV format is compatible; skipping conversion.")
                return str(input_file)
            logger.info(
                "WAV format not compatible (channels=%s width=%s rate=%s). Converting.",
                channels,
                sample_width,
                sample_rate,
            )
        else:
            logger.info("WAV metadata unavailable; converting to standard format.")
    
    print(f"Converting {input_path.suffix.upper()} to WAV format...")
    
    # Determine output path
    if output_file is None:
        # Use a writable temp location (input mount can be read-only in Docker)
        temp_handle = tempfile.NamedTemporaryFile(
            suffix=".wav",
            prefix=f"{input_path.stem}_converted_",
            delete=False,
            dir="/tmp",
        )
        output_file = Path(temp_handle.name)
        temp_handle.close()
    
    output_file = str(output_file)
    
    # Check if ffmpeg is available
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            raise FileNotFoundError("ffmpeg not found")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("✗ ffmpeg not found. Please install ffmpeg:")
        print("  - macOS: brew install ffmpeg")
        print("  - Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  - Docker: ffmpeg should be pre-installed")
        raise RuntimeError("ffmpeg is required for audio conversion")
    
    # Convert to WAV using ffmpeg
    # -y: overwrite output file
    # -i: input file
    # -ar 24000: sample rate (pocket_tts uses 24kHz)
    # -ac 1: mono audio
    # -acodec pcm_s16le: 16-bit PCM (standard WAV format)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-ar", "24000",
        "-ac", "1",
        "-acodec", "pcm_s16le",
        output_file
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"✗ ffmpeg conversion failed:")
            print(f"  {result.stderr[:500] if result.stderr else 'Unknown error'}")
            raise RuntimeError(f"Audio conversion failed: {result.stderr[:200]}")
        
        # Verify output file exists and has content
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            raise RuntimeError("Converted file is empty or missing")
        
        file_size = os.path.getsize(output_file) / 1024
        print(f"✓ Converted to WAV: {output_file} ({file_size:.1f} KB)")
        log_audio_info(output_file, label="converted")
        return output_file
        
    except subprocess.TimeoutExpired:
        print("✗ Audio conversion timed out")
        raise RuntimeError("Audio conversion timed out after 60 seconds")
