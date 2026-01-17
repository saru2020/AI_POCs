#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging utilities for Pocket TTS.
"""

import logging
import os
import sys
import wave
from pathlib import Path


def setup_logging(output_file):
    """Setup logging to stdout and a debug file."""
    output_path = Path(output_file)
    log_dir = output_path.parent if output_path.parent else Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "pocket_tts_debug.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
    )
    logging.info("Debug log: %s", log_path)
    return log_path


def log_audio_info(file_path, label="audio"):
    """Log audio file properties; fall back gracefully if unsupported."""
    logger = logging.getLogger("pocket_tts")
    try:
        file_size = os.path.getsize(file_path)
        logger.info("%s file size: %s bytes", label, file_size)
    except OSError as exc:
        logger.warning("Failed to read %s size: %s", label, exc)

    try:
        with wave.open(file_path, "rb") as wav:
            channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            sample_rate = wav.getframerate()
            frames = wav.getnframes()
            duration = frames / float(sample_rate) if sample_rate else 0.0
        logger.info(
            "%s wav info: channels=%s width=%s rate=%s frames=%s duration=%.2fs",
            label,
            channels,
            sample_width,
            sample_rate,
            frames,
            duration,
        )
        return channels, sample_width, sample_rate
    except wave.Error as exc:
        logger.warning("%s wav parse failed: %s", label, exc)
    except OSError as exc:
        logger.warning("%s wav open failed: %s", label, exc)
    return None


def log_process_memory(label="process"):
    """Log memory info from /proc when available (Linux containers)."""
    logger = logging.getLogger("pocket_tts")
    status_path = Path("/proc/self/status")
    if not status_path.exists():
        return
    try:
        content = status_path.read_text()
    except OSError:
        return
    keys = ("VmRSS", "VmHWM", "VmSize", "Threads")
    for line in content.splitlines():
        if any(line.startswith(key) for key in keys):
            logger.info("%s %s", label, line.strip())
