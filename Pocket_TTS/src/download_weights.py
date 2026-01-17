#!/usr/bin/env python3
"""
Manual Weight Downloader for Pocket TTS Voice Cloning

This script helps you download the gated voice cloning weights manually
since the automatic download from HuggingFace is failing.

The weights are gated due to ethical concerns around voice cloning.
You must accept terms at https://huggingface.co/kyutai/pocket-tts first.
"""

import os
import sys
from pathlib import Path

def check_huggingface_cli():
    """Check if huggingface-cli is available"""
    import shutil
    return shutil.which("huggingface-cli") is not None


def download_with_cli(token=None):
    """Try to download using huggingface-cli which handles auth better"""
    import subprocess
    
    # Files to download
    files_to_download = [
        ("kyutai/pocket-tts", "tts_b6369a24.safetensors"),  # Main weights with voice cloning
    ]
    
    models_dir = Path(__file__).resolve().parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    print("="*70)
    print("Attempting to download voice cloning weights via huggingface-cli")
    print("="*70)
    
    # Login first if token provided
    if token:
        print(f"\nLogging in with provided token...")
        login_cmd = ["huggingface-cli", "login", "--token", token]
        result = subprocess.run(login_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Warning: Login failed: {result.stderr}")
        else:
            print("Login successful!")
    
    for repo_id, filename in files_to_download:
        print(f"\nDownloading {filename} from {repo_id}...")
        
        output_path = models_dir / filename
        
        cmd = [
            "huggingface-cli", "download",
            repo_id,
            filename,
            "--local-dir", str(models_dir),
            "--local-dir-use-symlinks", "False"
        ]
        
        if token:
            cmd.extend(["--token", token])
        
        print(f"Running: {' '.join(cmd[:6])}...")  # Don't print token
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"\nFailed to download {filename}")
            print(f"Error: {result.stderr}")
            
            if "401" in result.stderr or "403" in result.stderr or "gated" in result.stderr.lower():
                print("\n" + "="*70)
                print("ACCESS DENIED - You need to accept terms on HuggingFace website")
                print("="*70)
                print("\nPlease follow these steps:")
                print("1. Go to: https://huggingface.co/kyutai/pocket-tts")
                print("2. Log in with your HuggingFace account")
                print("3. Click 'Agree and access repository'")
                print("4. Wait 2-3 minutes for access to propagate")
                print("5. Run this script again")
                print("="*70)
            return False
        else:
            print(f"Successfully downloaded to: {output_path}")
    
    return True


def download_with_python(token=None):
    """Try to download using Python huggingface_hub"""
    try:
        from huggingface_hub import hf_hub_download, login
        
        models_dir = Path(__file__).resolve().parent.parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        print("="*70)
        print("Attempting to download voice cloning weights via Python API")
        print("="*70)
        
        if token:
            print("\nLogging in...")
            login(token=token)
            print("Login successful!")
        
        print(f"\nDownloading tts_b6369a24.safetensors from kyutai/pocket-tts...")
        
        downloaded_path = hf_hub_download(
            repo_id="kyutai/pocket-tts",
            filename="tts_b6369a24.safetensors",
            local_dir=str(models_dir),
            local_dir_use_symlinks=False,
            token=token
        )
        
        print(f"Successfully downloaded to: {downloaded_path}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\nFailed to download: {error_msg}")
        
        if "401" in error_msg or "403" in error_msg or "gated" in error_msg.lower() or "Access" in error_msg:
            print("\n" + "="*70)
            print("ACCESS DENIED - You need to accept terms on HuggingFace website")
            print("="*70)
            print("\nPlease follow these steps:")
            print("1. Go to: https://huggingface.co/kyutai/pocket-tts")
            print("2. Log in with your HuggingFace account")
            print("3. Click 'Agree and access repository'")
            print("4. Wait 2-3 minutes for access to propagate")
            print("5. Run this script again")
            print("="*70)
        
        return False


def show_manual_instructions():
    """Show instructions for manual browser download"""
    models_dir = Path(__file__).resolve().parent.parent / "models"
    
    print("""
================================================================================
MANUAL DOWNLOAD INSTRUCTIONS (Browser Method)
================================================================================

Since automatic download is failing, you can download manually from the website:

STEP 1: Accept Terms on HuggingFace
-----------------------------------
   1. Open: https://huggingface.co/kyutai/pocket-tts
   2. Log in with your HuggingFace account
   3. You should see an "Agree and access repository" button
   4. Click it and wait for the page to reload
   5. You should now see the file list

STEP 2: Download the Weight File
---------------------------------
   1. Click on "Files and versions" tab
   2. Find: tts_b6369a24.safetensors (~236 MB)
   3. Click the download button (down arrow icon)
   4. Save to: {models_dir}/

STEP 3: Verify Download
------------------------
   After downloading, run:
   
   ls -la {models_dir}/
   
   You should see:
   - tts_b6369a24.safetensors (~236 MB)

STEP 4: Use with Voice Cloning
-------------------------------
   Once downloaded, use this command:
   
   python src/pocket_tts_demo.py \\
       --audio-file input/rajni_audio.wav \\
       --text "Hello world" \\
       --output output/result.wav

================================================================================
""".format(models_dir=models_dir.absolute()))


def verify_download():
    """Check if weights are already downloaded"""
    models_dir = Path(__file__).resolve().parent.parent / "models"
    weights_file = models_dir / "tts_b6369a24.safetensors"
    
    if weights_file.exists():
        size_mb = weights_file.stat().st_size / (1024 * 1024)
        print(f"\n✓ Voice cloning weights found: {weights_file}")
        print(f"  Size: {size_mb:.1f} MB")
        
        if size_mb < 200:
            print(f"  ⚠️  Warning: File seems too small. Expected ~236 MB.")
            return False
        
        print(f"\n✓ You can now use voice cloning with:")
        return True
    else:
        print(f"\n✗ Voice cloning weights NOT found at: {weights_file}")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Pocket TTS voice cloning weights")
    parser.add_argument("--token", type=str, help="HuggingFace token")
    parser.add_argument("--manual", action="store_true", help="Show manual download instructions")
    parser.add_argument("--verify", action="store_true", help="Only verify if weights exist")
    args = parser.parse_args()
    
    token = args.token or os.environ.get("HUGGINGFACE_HUB_TOKEN") or os.environ.get("HF_TOKEN")
    
    if args.verify:
        verify_download()
        return
    
    if args.manual:
        show_manual_instructions()
        return
    
    # Check if already downloaded
    if verify_download():
        print("\nWeights already downloaded! No action needed.")
        return
    
    print("\nAttempting automatic download...")
    print("(This requires you to have already accepted terms at https://huggingface.co/kyutai/pocket-tts)\n")
    
    # Try CLI first (often works better with gated repos)
    if check_huggingface_cli():
        success = download_with_cli(token)
    else:
        print("huggingface-cli not found, trying Python API...")
        success = download_with_python(token)
    
    if success:
        verify_download()
    else:
        print("\n" + "="*70)
        print("Automatic download failed. Showing manual instructions...")
        print("="*70)
        show_manual_instructions()


if __name__ == "__main__":
    main()
