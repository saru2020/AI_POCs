#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pocket TTS Demo - Standalone Python Script

This script demonstrates Kyutai Pocket TTS text-to-speech with voice cloning capabilities.
It can use predefined voices or clone voices from local audio files.

Supports:
- Loading from HuggingFace (default)
- Loading from local model directory (for manual downloads)
- Cache clearing to force fresh downloads

Usage:
    python src/pocket_tts_demo.py --voice alba --text "Hello world"
    python src/pocket_tts_demo.py --audio-file rajni_audio.wav --text "Hello world" --output output.wav
    python src/pocket_tts_demo.py --local-model /path/to/model --audio-file voice.wav --text "Hello"
    python src/pocket_tts_demo.py --clear-cache  # Clear HuggingFace cache
"""

import argparse
import faulthandler
import os
import signal
import sys

from audio_generator import generate_audio
from auth_utils import setup_huggingface_auth
from cache_utils import clear_huggingface_cache, show_download_instructions
from dependencies import check_dependencies
from logging_utils import setup_logging
from model_loader import load_model
from voice_utils import get_voice_state


def main():
    faulthandler.enable()
    try:
        faulthandler.register(signal.SIGTERM)
        faulthandler.register(signal.SIGABRT)
        faulthandler.register(signal.SIGSEGV)
        faulthandler.register(signal.SIGBUS)
        faulthandler.register(signal.SIGILL)
    except Exception:
        pass
    
    parser = argparse.ArgumentParser(
        description="Pocket TTS Demo - Text-to-Speech with Voice Cloning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use predefined voice
  python src/pocket_tts_demo.py --voice alba --text "Hello world"
  
  # Clone voice from audio file
  python src/pocket_tts_demo.py --audio-file my_voice.wav --text "Hello world"
  
  # With HuggingFace token for voice cloning
  python src/pocket_tts_demo.py --token YOUR_TOKEN --audio-file my_voice.wav --text "Hello world"
  
  # Use model without voice cloning (no auth required)
  python src/pocket_tts_demo.py --no-voice-cloning --voice alba --text "Hello world"
  
  # Use locally downloaded model weights
  python src/pocket_tts_demo.py --local-model ./models/pocket-tts --audio-file my_voice.wav --text "Hello"
  
  # Clear cache to force fresh download
  python src/pocket_tts_demo.py --clear-cache
  
  # Show download instructions
  python src/pocket_tts_demo.py --download-help
  
Predefined voices: alba, marius, javert, jean, fantine, cosette, eponine, azelma
        """
    )
    
    parser.add_argument(
        "--voice",
        type=str,
        choices=['alba', 'marius', 'javert', 'jean', 'fantine', 'cosette', 'eponine', 'azelma'],
        help="Use a predefined voice"
    )
    
    parser.add_argument(
        "--audio-file",
        type=str,
        help="Path to audio file for voice cloning (WAV, MP3, FLAC, M4A, OGG). In Docker, use /app/input/filename.ext"
    )
    
    parser.add_argument(
        "--text",
        type=str,
        help="Text to convert to speech"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output.wav",
        help="Output audio file path (default: output.wav). In Docker, use /app/output/filename.wav"
    )
    
    parser.add_argument(
        "--token",
        type=str,
        help="HuggingFace token for voice cloning (or set HUGGINGFACE_HUB_TOKEN env var)"
    )
    
    parser.add_argument(
        "--skip-auth",
        action="store_true",
        help="Skip HuggingFace authentication check (for predefined voices only)"
    )
    
    parser.add_argument(
        "--local-model",
        type=str,
        help="Path to locally downloaded model weights directory"
    )
    
    parser.add_argument(
        "--no-voice-cloning",
        action="store_true",
        help="Use the model without voice cloning (no HuggingFace auth required, predefined voices only)"
    )

    parser.add_argument(
        "--max-prompt-seconds",
        type=int,
        default=30,
        help="Max seconds of voice prompt to use (default: 30)"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear HuggingFace cache to force fresh model download"
    )
    
    parser.add_argument(
        "--download-help",
        action="store_true",
        help="Show instructions for manually downloading model weights"
    )
    
    args = parser.parse_args()

    setup_logging(args.output)
    
    # Handle utility commands first
    if args.clear_cache:
        print("="*70)
        print("Clearing HuggingFace Cache")
        print("="*70)
        clear_huggingface_cache()
        sys.exit(0)
    
    if args.download_help:
        show_download_instructions()
        sys.exit(0)
    
    # Validate arguments for TTS generation
    if not args.text:
        parser.error("--text is required for TTS generation")
    
    if not args.voice and not args.audio_file:
        parser.error("Either --voice or --audio-file must be specified")
    
    if args.voice and args.audio_file:
        parser.error("Cannot specify both --voice and --audio-file")
    
    if args.no_voice_cloning and args.audio_file:
        parser.error("Cannot use --audio-file with --no-voice-cloning (use --voice instead)")
    
    print("="*70)
    print("Pocket TTS Demo")
    print("="*70)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup authentication (required for voice cloning)
    token = args.token or os.environ.get('HUGGINGFACE_HUB_TOKEN')
    
    if args.audio_file and not args.skip_auth:
        if not setup_huggingface_auth(token):
            print("\n⚠️  Warning: Authentication failed. Voice cloning may not work.")
            print("You can skip this with --skip-auth if you only want to use predefined voices.")
            response = input("\nContinue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # Load model (pass token to ensure it's available during model loading)
    try:
        model = load_model(
            token=token,
            local_model_path=args.local_model,
            no_voice_cloning=args.no_voice_cloning
        )
    except Exception as e:
        if args.audio_file and not args.local_model:
            print("\n" + "="*70)
            print("TIP: If authentication keeps failing, try one of these:")
            print("="*70)
            print("\n1. Use --no-voice-cloning with predefined voices:")
            print("   python src/pocket_tts_demo.py --no-voice-cloning --voice alba --text 'Hello'")
            print("\n2. Clear cache and try again:")
            print("   python src/pocket_tts_demo.py --clear-cache")
            print("\n3. Download model manually:")
            print("   python src/pocket_tts_demo.py --download-help")
            print("="*70)
        sys.exit(1)
    
    # Get voice state (pass token again to ensure it's available)
    try:
        voice_source = args.voice or args.audio_file
        voice_state = get_voice_state(
            model,
            voice_source,
            token=token,
            max_prompt_seconds=args.max_prompt_seconds,
        )
    except Exception as e:
        print(f"✗ Failed to get voice state: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Generate audio
    try:
        output_file = generate_audio(model, voice_state, args.text, args.output)
        print("\n" + "="*70)
        print("✓ Success! Audio file created.")
        print(f"  File: {os.path.abspath(output_file)}")
        print("="*70)
    except Exception as e:
        print(f"✗ Failed to generate audio: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
