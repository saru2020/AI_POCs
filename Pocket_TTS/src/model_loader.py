#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model loading utilities for Pocket TTS.
"""

import logging
import os
import time
from pathlib import Path


def load_model(token=None, local_model_path=None, no_voice_cloning=False):
    """Load the TTS model
    
    Args:
        token: HuggingFace token for authentication
        local_model_path: Path to locally downloaded model weights
        no_voice_cloning: If True, use the model without voice cloning (no auth required)
    """
    try:
        from pocket_tts import TTSModel
        
        # Save token to HuggingFace cache before loading model
        # This is more reliable than just environment variables
        if token:
            os.environ['HUGGINGFACE_HUB_TOKEN'] = token
            os.environ['HF_TOKEN'] = token
            try:
                # Try to save token to cache (more reliable)
                from huggingface_hub import HfFolder
                HfFolder.save_token(token)
                print("✓ Token saved to HuggingFace cache")
            except Exception as e:
                print(f"⚠️  Could not save token to cache: {e}")
                print("Continuing with environment variable...")
        
        logger = logging.getLogger("pocket_tts")
        load_start = time.time()

        # Determine which model to load
        if local_model_path:
            print(f"Loading TTS model from local path: {local_model_path}")
            local_path = Path(local_model_path)
            
            if not local_path.exists():
                raise FileNotFoundError(f"Local model path not found: {local_model_path}")
            
            # Find the safetensors file
            safetensors_files = list(local_path.glob("*.safetensors"))
            if safetensors_files:
                print(f"Found model weights: {[f.name for f in safetensors_files]}")
            else:
                print(f"⚠️  No .safetensors files found in {local_model_path}")
                print("Available files:", list(local_path.iterdir()))
            
            # Try to load from local path
            # The pocket_tts library may support different loading methods
            try:
                # Method 1: Try passing the directory path
                model = TTSModel.load_model(str(local_path))
                print("✓ Model loaded from local directory!")
            except Exception as e1:
                print(f"Method 1 (directory) failed: {e1}")
                try:
                    # Method 2: Try passing the safetensors file directly
                    if safetensors_files:
                        model = TTSModel.load_model(str(safetensors_files[0]))
                        print("✓ Model loaded from safetensors file!")
                    else:
                        raise FileNotFoundError("No safetensors files found")
                except Exception as e2:
                    print(f"Method 2 (safetensors file) failed: {e2}")
                    # Method 3: Set HF_HOME to local path and try default loading
                    try:
                        os.environ['HF_HOME'] = str(local_path.parent)
                        os.environ['HUGGINGFACE_HUB_CACHE'] = str(local_path.parent)
                        model = TTSModel.load_model()
                        print("✓ Model loaded with HF_HOME override!")
                    except Exception as e3:
                        print(f"Method 3 (HF_HOME override) failed: {e3}")
                        raise RuntimeError(
                            f"Could not load model from local path. "
                            f"Tried: directory, safetensors file, HF_HOME override. "
                            f"Last error: {e3}"
                        )
        
        elif no_voice_cloning:
            print("Loading TTS model WITHOUT voice cloning (no authentication required)...")
            print("Note: You can only use predefined voices (alba, marius, etc.)")
            model = TTSModel.load_model("kyutai/pocket-tts-without-voice-cloning")
            print("✓ Model loaded (without voice cloning)!")
            return model
        
        else:
            print("Loading TTS model from HuggingFace...")
            print("(This may download model weights if not already cached)")
            print("(Voice cloning weights will be downloaded if token is valid and terms are accepted)")
            model = TTSModel.load_model()
        
        logger.info("Model loaded in %.2fs", time.time() - load_start)

        # Check if voice cloning is available
        if hasattr(model, 'has_voice_cloning'):
            if model.has_voice_cloning:
                print("✓ Voice cloning is available!")
            else:
                print("⚠️  Voice cloning weights not loaded")
                print("This might mean:")
                print("  - Terms not accepted at https://huggingface.co/kyutai/pocket-tts")
                print("  - Token not valid or not properly authenticated")
                print("  - Model will try to download weights when needed")
        else:
            print("⚠️  Could not check voice cloning status")
        
        print("✓ Model loaded successfully!")
        return model
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        raise
