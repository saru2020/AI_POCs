#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cache management utilities for Pocket TTS.
"""

import os
import shutil
from pathlib import Path


def clear_huggingface_cache():
    """Clear HuggingFace cache to force fresh downloads"""
    cache_dirs = [
        Path.home() / ".cache" / "huggingface",
        Path("/app/.cache/huggingface"),  # Docker path
        Path(os.environ.get("HUGGINGFACE_HUB_CACHE", "")) if os.environ.get("HUGGINGFACE_HUB_CACHE") else None,
        Path(os.environ.get("HF_HOME", "")) if os.environ.get("HF_HOME") else None,
    ]
    
    cleared = False
    for cache_dir in cache_dirs:
        if cache_dir and cache_dir.exists():
            print(f"Found cache at: {cache_dir}")
            
            # Look for pocket-tts specific cache
            hub_dir = cache_dir / "hub"
            if hub_dir.exists():
                for item in hub_dir.iterdir():
                    if "pocket-tts" in item.name.lower() or "kyutai" in item.name.lower():
                        print(f"  Removing: {item.name}")
                        try:
                            if item.is_dir():
                                shutil.rmtree(item)
                            else:
                                item.unlink()
                            cleared = True
                        except Exception as e:
                            print(f"  Warning: Could not remove {item}: {e}")
    
    if cleared:
        print("✓ Cache cleared! Fresh download will occur on next run.")
    else:
        print("No pocket-tts cache found to clear.")
    
    return cleared


def show_download_instructions():
    """Show instructions for manually downloading model weights"""
    print("""
================================================================================
MANUAL MODEL DOWNLOAD INSTRUCTIONS
================================================================================

Since HuggingFace authentication is failing, you can manually download the
model weights from the website and use them locally.

STEP 1: Accept Terms on HuggingFace (in your browser)
-------------------------------------------------------
   1. Go to: https://huggingface.co/kyutai/pocket-tts
   2. Log in with your HuggingFace account
   3. Click "Agree and access repository" to accept the terms
   4. Wait 2-3 minutes for access to propagate

STEP 2: Download Model Files
-----------------------------
   Go to the "Files and versions" tab and download these files:
   
   From https://huggingface.co/kyutai/pocket-tts/tree/main:
   - tts_b6369a24.safetensors (main model weights ~236MB)
   - config.json (if available)
   - tokenizer.model (if available)
   
   Save them to a folder, e.g., ./models/pocket-tts/

STEP 3: Use Local Model
------------------------
   ./run.sh run --local-model /app/models \\
                --audio-file /app/input/your_voice.wav \\
                --text "Hello world" \\
                --output /app/output/result.wav

   Or without Docker:
   python src/pocket_tts_demo.py --local-model ./models/pocket-tts \\
                             --audio-file voice.wav \\
                             --text "Hello world"

ALTERNATIVE: Use Without Voice Cloning
---------------------------------------
   The model without voice cloning doesn't require authentication:
   
   ./run.sh run --no-voice-cloning --voice alba --text "Hello world"

================================================================================
""")
