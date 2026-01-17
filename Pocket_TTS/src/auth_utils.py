#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication utilities for HuggingFace.
"""

import os
import subprocess
import sys


def setup_huggingface_auth(token=None):
    """Setup HuggingFace authentication"""
    from huggingface_hub import whoami
    
    # Get token from parameter or environment variable
    auth_token = token or os.environ.get('HUGGINGFACE_HUB_TOKEN') or os.environ.get('HF_TOKEN')
    
    # Set token as environment variable and try multiple authentication methods
    if auth_token:
        os.environ['HUGGINGFACE_HUB_TOKEN'] = auth_token
        os.environ['HF_TOKEN'] = auth_token
        
        # Try using huggingface-cli login method (most reliable)
        try:
            # Use huggingface-cli to login (this is what the error message suggests)
            result = subprocess.run(
                [sys.executable, "-m", "huggingface_hub.cli.huggingface_cli", "login", "--token", auth_token],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✓ Token saved via huggingface-cli")
            else:
                # Fallback: try to save token using HfFolder
                try:
                    from huggingface_hub import HfFolder
                    HfFolder.save_token(auth_token)
                    print("✓ Token saved to HuggingFace cache")
                except Exception:
                    print("✓ Token set in environment")
        except Exception:
            # Fallback methods
            try:
                from huggingface_hub import HfFolder
                HfFolder.save_token(auth_token)
                print("✓ Token saved to HuggingFace cache")
            except Exception:
                print("✓ Token set in environment (fallback method)")
    
    # Check if already authenticated
    try:
        # Explicitly pass token to whoami
        user_info = whoami(token=auth_token) if auth_token else whoami()
        username = user_info.get('name', user_info.get('fullname', 'Unknown'))
        print(f"✓ Authenticated as: {username}")
        return True
    except Exception as e:
        if auth_token:
            print(f"⚠️  Authentication check failed: {str(e)[:100]}")
            print("\n" + "="*70)
            print("⚠️  IMPORTANT: Token Authentication Issues")
            print("="*70)
            print("\nThe token is set but authentication verification failed.")
            print("This might be because:")
            print("1. You haven't accepted the terms at: https://huggingface.co/kyutai/pocket-tts")
            print("   → Go to the link and click 'Agree and access repository'")
            print("\n2. The token needs 'read' permissions")
            print("   → Check your token at: https://huggingface.co/settings/tokens")
            print("   → Make sure it has at least 'read' access")
            print("\n3. The token might be expired or invalid")
            print("   → Generate a new token if needed")
            print("\nContinuing anyway - the token is set and may work for model downloads...")
            print("="*70)
            return True  # Continue anyway, token is set
        else:
            print("⚠️  No HuggingFace token provided.")
            print("For voice cloning, you need to:")
            print("1. Accept terms at: https://huggingface.co/kyutai/pocket-tts")
            print("2. Get your token from: https://huggingface.co/settings/tokens")
            print("3. Set it with: --token YOUR_TOKEN or export HUGGINGFACE_HUB_TOKEN=YOUR_TOKEN")
            return False
