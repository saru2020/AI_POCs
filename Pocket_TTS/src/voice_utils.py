#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice state utilities for Pocket TTS.
"""

import logging
import os
import sys
import threading
import time

from audio_utils import convert_audio_to_wav, trim_wav_if_needed
from logging_utils import log_audio_info, log_process_memory


def get_voice_state(model, voice_or_file, token=None, max_prompt_seconds=30):
    """Get voice state from predefined voice or audio file"""
    # Ensure token is available when trying to download voice cloning weights
    if token:
        os.environ['HUGGINGFACE_HUB_TOKEN'] = token
        os.environ['HF_TOKEN'] = token
        try:
            from huggingface_hub import HfFolder
            HfFolder.save_token(token)
        except Exception:
            pass  # Token might already be saved
    
    logger = logging.getLogger("pocket_tts")
    
    try:
        # Check if it's a predefined voice
        predefined_voices = ['alba', 'marius', 'javert', 'jean', 'fantine', 'cosette', 'eponine', 'azelma']
        if voice_or_file in predefined_voices:
            print(f"Using predefined voice: {voice_or_file}")
            return model.get_state_for_audio_prompt(voice_or_file)
        else:
            # Assume it's a file path
            if not os.path.exists(voice_or_file):
                raise FileNotFoundError(f"Audio file not found: {voice_or_file}")
            
            # Convert to WAV if necessary (pocket_tts only supports WAV format)
            audio_file = convert_audio_to_wav(voice_or_file)
            audio_file = trim_wav_if_needed(audio_file, max_prompt_seconds)
            
            log_audio_info(audio_file, label="voice prompt")
            print(f"Cloning voice from: {audio_file}")
            print("(Downloading voice cloning weights if needed...)")
            sys.stdout.flush()  # Ensure output is visible before potentially crashing
            
            try:
                stop_event = threading.Event()

                def heartbeat():
                    start = time.time()
                    while not stop_event.wait(10):
                        logger.info(
                            "Voice cloning still running (%.1fs elapsed)...",
                            time.time() - start,
                        )
                        log_process_memory("voice cloning")

                thread = threading.Thread(target=heartbeat, daemon=True)
                thread.start()
                start = time.time()
                log_process_memory("before voice cloning")
                result = model.get_state_for_audio_prompt(audio_file)
                stop_event.set()
                if result is None:
                    raise RuntimeError("Voice cloning returned no state")
                logger.info(
                    "Voice cloning completed in %.2fs", time.time() - start
                )
                log_process_memory("after voice cloning")
                print("✓ Voice cloned successfully!")
                sys.stdout.flush()
                return result
            except Exception as inner_e:
                print(f"✗ Voice cloning failed: {inner_e}")
                import traceback
                traceback.print_exc()
                sys.stdout.flush()
                raise
    except ValueError as e:
        error_msg = str(e)
        if "could not download the weights" in error_msg.lower() or "voice cloning" in error_msg.lower():
            print("\n" + "="*70)
            print("⚠️  Voice Cloning Model Not Available")
            print("="*70)
            print("\nThis error means the voice cloning model weights cannot be downloaded.")
            print("\nEven though you've accepted terms, this might be because:")
            print("\n1. ✅ VERIFY TERMS ACCEPTANCE:")
            print("   → Go to: https://huggingface.co/kyutai/pocket-tts")
            print("   → Make sure you see the repository content (not 'Accept terms' button)")
            print("   → If you see 'Accept terms', click it and wait a few minutes")
            print("\n2. ✅ TOKEN VERIFICATION:")
            print("   → Check token at: https://huggingface.co/settings/tokens")
            print("   → Make sure it's active and has 'Read' permissions")
            print("   → Try generating a NEW token and use that")
            print("\n3. ✅ CLEAR CACHE AND RETRY:")
            print("   → The model might have cached the 'no voice cloning' state")
            print("   → Try deleting: ~/.cache/huggingface/ or /app/.cache/huggingface/")
            print("   → Then run the command again")
            print("\n4. ✅ ALTERNATIVE: Use predefined voices")
            print("   → Predefined voices work without voice cloning:")
            print("   → ./run.sh run --voice alba --text 'Hello' --output /app/output/test.wav")
            print("="*70)
        raise
    except Exception as e:
        print(f"✗ Error getting voice state: {e}")
        raise
