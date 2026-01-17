# HuggingFace Authentication Guide for Voice Cloning

## Required Steps

### 1. Accept the Terms (MANDATORY)

**This is the most important step!**

1. Go to: https://huggingface.co/kyutai/pocket-tts
2. Click the **"Agree and access repository"** button
3. You must be logged into HuggingFace to do this

**Without accepting the terms, voice cloning will NOT work, even with a valid token.**

### 2. Create/Get Your Token

1. Go to: https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Give it a name (e.g., "pocket-tts-voice-cloning")
4. Select **"Read"** as the token type (this is sufficient)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again)

### 3. Token Permissions

Your token needs:
- **Type**: `Read` (this is the default and sufficient)
- **No special permissions required** - just read access

The token should:
- Start with `hf_`
- Be active (not revoked)
- Not be expired

### 4. Use the Token

#### Option A: Environment Variable (Recommended)
```bash
export HUGGINGFACE_HUB_TOKEN=your_token_here
./run.sh run --audio-file /app/input/your_audio.wav --text "Hello" --output /app/output/result.wav
```

#### Option B: Inline with Command
```bash
HUGGINGFACE_HUB_TOKEN=your_token_here ./run.sh run --audio-file /app/input/your_audio.wav --text "Hello" --output /app/output/result.wav
```

#### Option C: Using --token Flag
```bash
./run.sh run --token your_token_here --audio-file /app/input/your_audio.wav --text "Hello" --output /app/output/result.wav
```

## Troubleshooting

### Error: "Voice Cloning Model Not Available"

**Most common cause**: You haven't accepted the terms!

1. ✅ Go to https://huggingface.co/kyutai/pocket-tts
2. ✅ Click "Agree and access repository"
3. ✅ Make sure you're logged in
4. ✅ Try again

### Error: "Token is required but no token found"

1. ✅ Make sure the token is set: `echo $HUGGINGFACE_HUB_TOKEN`
2. ✅ Check the token starts with `hf_`
3. ✅ Verify the token is active at https://huggingface.co/settings/tokens
4. ✅ Generate a new token if needed

### Error: "Authentication check failed"

This is often okay! The token might still work for model downloads even if `whoami()` fails. The script will continue and try to download the model.

If voice cloning still fails:
1. ✅ Accept the terms (most important!)
2. ✅ Verify token is correct
3. ✅ Try generating a new token
4. ✅ Make sure you're logged into HuggingFace in your browser

## Verification

To verify your setup:

1. **Check terms acceptance**: Visit https://huggingface.co/kyutai/pocket-tts - you should see the repository content, not a "Accept terms" button

2. **Test token**: 
   ```bash
   python -c "from huggingface_hub import whoami; print(whoami())"
   ```

3. **Test voice cloning**: Try with a predefined voice first:
   ```bash
   ./run.sh run --voice alba --text "Test" --output /app/output/test.wav
   ```

## Summary Checklist

- [ ] Accepted terms at https://huggingface.co/kyutai/pocket-tts
- [ ] Created a token with "Read" permissions
- [ ] Token is set in environment or passed as argument
- [ ] Token starts with `hf_` and is active
- [ ] Audio file is in `input/` directory
- [ ] Running the command with proper paths
