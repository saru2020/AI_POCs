#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency checking and installation utilities for Pocket TTS.
"""

import subprocess
import sys


def check_dependencies():
    """Check if required packages are installed"""
    try:
        import pocket_tts
        import scipy
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nAttempting to install dependencies...")
        print("(This may take a few minutes on first run)\n")
        
        # Install pocket-tts without deps first
        print("Step 1: Installing pocket-tts...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pocket-tts", "--no-deps"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                if "already satisfied" not in result.stdout.lower():
                    print(f"  Warning: {result.stderr}")
        except Exception as ex:
            print(f"  Warning: {ex}")
        
        # Install dependencies
        print("Step 2: Installing dependencies...")
        deps = [
            "beartype", "einops", "fastapi", "huggingface-hub", 
            "numpy<2.0", "pydantic", "python-multipart>=0.0.20",
            "requests", "safetensors", "scipy", "sentencepiece", "typer>=0.10.0"
        ]
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + deps,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"  Warning: Some dependencies may have failed to install")
                print(f"  Error: {result.stderr}")
        except Exception as ex:
            print(f"  Warning: {ex}")
        
        # Verify installation
        print("\nVerifying installation...")
        try:
            import pocket_tts
            import scipy
            print("✓ Dependencies installed successfully!")
            return True
        except ImportError as import_err:
            print(f"✗ Installation incomplete: {import_err}")
            print("\n" + "="*70)
            print("Installation Instructions:")
            print("="*70)
            print("\nOption 1 - Install in current environment:")
            print("  pip install pocket-tts --no-deps")
            print("  pip install beartype einops fastapi huggingface-hub 'numpy<2.0' pydantic 'python-multipart>=0.0.20' requests safetensors scipy sentencepiece 'typer>=0.10.0'")
            print("\nOption 2 - Use requirements.txt:")
            print("  pip install pocket-tts --no-deps")
            print("  pip install -r requirements.txt")
            print("\nOption 3 - If packages are in base conda environment:")
            print("  Deactivate venv: deactivate")
            print("  Run script with base Python: python src/pocket_tts_demo.py ...")
            print("="*70)
            return False
