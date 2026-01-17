# Pocket TTS Docker Setup

This guide explains how to run Pocket TTS using Docker with a single command.

## Quick Start

### 1. Build the Docker Image

```bash
./run.sh build
```

### 2. Run with Predefined Voice

```bash
./run.sh run --voice alba --text "Hello world" --output output/hello.wav
```

### 3. Run with Voice Cloning

First, place your audio file in the `input/` directory:

```bash
cp rajni_audio.wav input/
```

Then run with your HuggingFace token:

```bash
HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run --audio-file /app/input/rajni_audio.wav --text "Hello world" --output /app/output/result.wav
```

## Single Command Examples

### Build and Run (Predefined Voice)
```bash
./run.sh build && ./run.sh run --voice alba --text "Hello world"
```

### Build and Run (Voice Cloning)
```bash
./run.sh build && HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run --audio-file /app/input/rajni_audio.wav --text "Hello world" --output /app/output/result.wav
```

## Directory Structure

```
Pocket_TTS/
├── input/          # Place your audio files here
├── output/         # Generated audio files will be saved here
├── run.sh          # Main script to run everything
├── Dockerfile      # Docker image definition
├── src/            # Application source code
│   └── pocket_tts_demo.py  # Main application
└── docs/           # Documentation
```

## Available Commands

- `./run.sh build` - Build the Docker image
- `./run.sh run [options]` - Run the TTS demo
- `./run.sh shell` - Open a shell in the container
- `./run.sh clean` - Remove containers and images
- `./run.sh help` - Show help message

## Environment Variables

- `HUGGINGFACE_HUB_TOKEN` - Your HuggingFace token for voice cloning

## File Paths in Docker

When running in Docker:
- Input files: `/app/input/filename.ext`
- Output files: `/app/output/filename.wav`
- These map to `./input/` and `./output/` on your host machine

## Troubleshooting

### Image not found
If you get an error about the image not being found, run:
```bash
./run.sh build
```

### Voice cloning not working
Make sure you:
1. Have accepted terms at https://huggingface.co/kyutai/pocket-tts
2. Set your HuggingFace token: `export HUGGINGFACE_HUB_TOKEN=your_token`
3. Place audio files in the `input/` directory

### Permission errors
Make sure the script is executable:
```bash
chmod +x run.sh
```
