# Pocket TTS Demo

A simple demo showcasing Kyutai Pocket TTS - a lightweight text-to-speech model with voice cloning capabilities that runs on CPU in real-time.

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Build the Docker image:**
   ```bash
   ./run.sh build
   ```

2. **Run with a predefined voice:**
   ```bash
   ./run.sh run --voice alba --text "Hello, this is a test" --output /app/output/test.wav
   ```

3. **Clone voice from audio file:**
   ```bash
   # Place your audio file in ./input/ directory first
   HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run \
     --audio-file /app/input/rajni_audio.wav \
     --text "You know what: Anger! Anger is the cause of all miseries, one should know how to control it; otherwise life becomes miserable; and hey, last but not least" \
     --output /app/output/test.wav
   ```

   **Listen to the generated audio:**
   
   <audio controls>
     <source src="output/test.wav" type="audio/wav">
     Your browser does not support the audio element. <a href="output/test.wav">Download the audio file</a> instead.
   </audio>
   
   > **Note:** If the audio file doesn't play, make sure you've run the command above first to generate `output/test.wav`. You can also download the file directly by clicking the link.

4. **Play the generated audio:**
   ```bash
   # On macOS
   afplay output/test.wav
   
   # On Linux
   aplay output/test.wav
   # or
   mpv output/test.wav
   ```

### Option 2: Using Python Directly

1. **Install dependencies:**
   ```bash
   pip install pocket-tts --no-deps
   pip install -r requirements.txt
   ```

2. **Run with predefined voice:**
   ```bash
   python src/pocket_tts_demo.py --voice alba --text "Hello world" --output output/test.wav
   ```

3. **Clone voice from audio file:**
   ```bash
   python src/pocket_tts_demo.py \
     --audio-file input/rajni_audio.wav \
     --text "This is a test" \
     --output output/test.wav
   ```

## Demo Files

The repository includes demo files for testing:

- **Input:** `input/rajni_audio.wav` - Sample voice file for voice cloning
- **Output:** `output/test.wav` - Sample generated audio file

### Try the Demo

```bash
# Using Docker
./run.sh run --voice alba --text "Welcome to Pocket TTS demo" --output /app/output/test.wav

# Using Python
python src/pocket_tts_demo.py --voice alba --text "Welcome to Pocket TTS demo" --output output/test.wav
```

After running, check the `output/` directory for your generated audio file.

## Available Voices

Predefined voices (no authentication required):
- `alba`
- `marius`
- `javert`
- `jean`
- `fantine`
- `cosette`
- `eponine`
- `azelma`

## Voice Cloning

To clone a voice from an audio file, you need:

1. **HuggingFace Account** - Sign up at https://huggingface.co
2. **Accept Terms** - Visit https://huggingface.co/kyutai/pocket-tts and click "Agree and access repository"
3. **Get Token** - Create a token at https://huggingface.co/settings/tokens
4. **Use Token** - Set `HUGGINGFACE_HUB_TOKEN` environment variable or use `--token` flag

```bash
# With token
HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run \
  --audio-file /app/input/your_voice.wav \
  --text "Hello world" \
  --output /app/output/test.wav
```

## Common Commands

```bash
# Build Docker image
./run.sh build

# Use predefined voice (no auth needed)
./run.sh run --voice alba --text "Hello" --output /app/output/test.wav

# Use without voice cloning (predefined voices only)
./run.sh run --no-voice-cloning --voice alba --text "Hello"

# Clear HuggingFace cache
./run.sh clear-cache

# Show download help
./run.sh download-help

# Open shell in container
./run.sh shell
```

## Project Structure

```
Pocket_TTS/
├── README.md              # Main guide
├── src/                   # Source code
│   ├── pocket_tts_demo.py # Main entry point
│   ├── audio_generator.py  # Audio generation logic
│   ├── audio_utils.py     # Audio conversion utilities
│   ├── auth_utils.py      # HuggingFace authentication
│   ├── cache_utils.py     # Cache management
│   ├── dependencies.py    # Dependency checking
│   ├── logging_utils.py    # Logging setup
│   ├── model_loader.py    # Model loading
│   └── voice_utils.py     # Voice state management
├── docs/                  # Documentation
│   ├── README_DOCKER.md   # Docker guide
│   ├── AUTHENTICATION_GUIDE.md
│   └── Pocket_TTS_Demo.ipynb
├── run.sh                 # Docker runner script
├── Dockerfile             # Docker configuration
├── requirements.txt       # Python dependencies
├── input/                 # Input audio files
│   └── rajni_audio.wav    # Demo input file
└── output/                # Generated audio files
    └── test.wav           # Demo output file
```

## Troubleshooting

**Issue: Authentication failed**
- Make sure you've accepted terms at https://huggingface.co/kyutai/pocket-tts
- Verify your token is valid at https://huggingface.co/settings/tokens
- Try clearing cache: `./run.sh clear-cache`

**Issue: Audio file not found**
- Place audio files in `./input/` directory
- Use full path in Docker: `/app/input/filename.wav`

**Issue: Output file not created**
- Check `output/` directory permissions
- In Docker, use `/app/output/filename.wav` as output path

## Additional Resources

- [Kyutai Pocket TTS Documentation](https://github.com/kyutai/pocket-tts)
- [HuggingFace Model Page](https://huggingface.co/kyutai/pocket-tts)
- [Authentication Guide](docs/AUTHENTICATION_GUIDE.md)
