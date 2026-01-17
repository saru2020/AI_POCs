#!/bin/bash

# Pocket TTS Demo - Single Command Runner
# This script handles building, running, and managing the Docker container

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create necessary directories
mkdir -p input output models

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
${GREEN}Pocket TTS Demo - Docker Runner${NC}

Usage: ./run.sh [command] [options]

Commands:
  build              Build the Docker image
  run                Run the TTS demo (requires --text and --voice or --audio-file)
  shell              Open a shell in the container
  clean              Remove containers and images
  clear-cache        Clear HuggingFace cache (force fresh download)
  download-help      Show instructions for manual model download
  help               Show this help message

Examples:
  # Build the image
  ./run.sh build

  # Use predefined voice (works without authentication)
  ./run.sh run --voice alba --text "Hello world"

  # Use predefined voice WITHOUT voice cloning model (no auth required)
  ./run.sh run --no-voice-cloning --voice alba --text "Hello world"

  # Clone voice from audio file (place file in ./input/ first)
  ./run.sh run --audio-file /app/input/rajni_audio.wav --text "Hello world" --output /app/output/result.wav

  # With HuggingFace token
  HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run --audio-file /app/input/rajni_audio.wav --text "Hello world" --output /app/output/result.wav

  # Clear cache and retry
  ./run.sh clear-cache
  ./run.sh run --audio-file /app/input/rajni_audio.wav --text "Hello" --output /app/output/result.wav

  # Open shell in container
  ./run.sh shell

  # Clean up
  ./run.sh clean

Environment Variables:
  HUGGINGFACE_HUB_TOKEN    Your HuggingFace token for voice cloning

EOF
}

# Function to build Docker image
build_image() {
    print_info "Building Docker image..."
    docker build -t pocket-tts:latest .
    print_success "Docker image built successfully!"
}

# Function to run the demo
run_demo() {
    # Check if image exists
    if ! docker image inspect pocket-tts:latest > /dev/null 2>&1; then
        print_warning "Docker image not found. Building..."
        build_image
    fi

    # Get HuggingFace token from environment or prompt
    if [ -z "$HUGGINGFACE_HUB_TOKEN" ]; then
        print_warning "HUGGINGFACE_HUB_TOKEN not set. Voice cloning may not work."
        print_info "Set it with: export HUGGINGFACE_HUB_TOKEN=your_token"
    fi

    print_info "Running Pocket TTS Demo..."
    print_info "Input files: ./input/"
    print_info "Output files: ./output/"
    echo ""
    
    # Build docker run command with proper argument handling
    docker run --rm -it \
        -v "$SCRIPT_DIR/input:/app/input:ro" \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/models:/app/models:ro" \
        -v pocket-tts-cache:/app/.cache/huggingface \
        ${HUGGINGFACE_HUB_TOKEN:+-e HUGGINGFACE_HUB_TOKEN="$HUGGINGFACE_HUB_TOKEN"} \
        -e PYTHONUNBUFFERED=1 \
        pocket-tts:latest \
        "$@"
}

# Function to open shell
open_shell() {
    if ! docker image inspect pocket-tts:latest > /dev/null 2>&1; then
        print_warning "Docker image not found. Building..."
        build_image
    fi
    
    print_info "Opening shell in container..."
    docker run --rm -it \
        -v "$SCRIPT_DIR/input:/app/input:ro" \
        -v "$SCRIPT_DIR/output:/app/output" \
        -v "$SCRIPT_DIR/models:/app/models:ro" \
        -v pocket-tts-cache:/app/.cache/huggingface \
        -e HUGGINGFACE_HUB_TOKEN="${HUGGINGFACE_HUB_TOKEN:-}" \
        -e PYTHONUNBUFFERED=1 \
        pocket-tts:latest \
        /bin/bash
}

# Function to clear HuggingFace cache
clear_cache() {
    print_info "Clearing HuggingFace cache..."
    
    # Check if image exists
    if ! docker image inspect pocket-tts:latest > /dev/null 2>&1; then
        print_warning "Docker image not found. Building..."
        build_image
    fi
    
    # Run clear cache command in container
    docker run --rm -it \
        -v pocket-tts-cache:/app/.cache/huggingface \
        pocket-tts:latest \
        --clear-cache
    
    # Also offer to remove the Docker volume entirely
    echo ""
    read -p "Also remove Docker cache volume entirely? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume rm pocket-tts-cache 2>/dev/null || true
        print_success "Docker cache volume removed"
    fi
    
    print_success "Cache cleared! Next run will download fresh model weights."
}

# Function to show download help
show_download_help() {
    cat << EOF

${GREEN}================================================================================
VOICE CLONING WEIGHTS DOWNLOAD GUIDE
=================================================================================${NC}

The voice cloning feature requires gated weights from HuggingFace.
You must download them manually from the website.

${YELLOW}STEP 1: Accept Terms on HuggingFace${NC}
   1. Go to: ${BLUE}https://huggingface.co/kyutai/pocket-tts${NC}
   2. Log in with your HuggingFace account
   3. Click "Agree and access repository"
   4. Wait 2-3 minutes for access to propagate

${YELLOW}STEP 2: Download the Weights File${NC}
   1. Click "Files and versions" tab
   2. Find: ${GREEN}tts_b6369a24.safetensors${NC} (~236 MB)
   3. Click the download icon
   4. Save to: ${BLUE}$SCRIPT_DIR/models/${NC}

${YELLOW}STEP 3: Verify and Use${NC}
   ls -la $SCRIPT_DIR/models/
   
   You should see: tts_b6369a24.safetensors (~236 MB)
   
${YELLOW}ALTERNATIVE: Use Predefined Voices (No Download Needed)${NC}
   ${GREEN}./run.sh run --no-voice-cloning --voice alba --text "Hello world" --output /app/output/test.wav${NC}

================================================================================

EOF
}

# Function to clean up
clean_up() {
    print_info "Cleaning up Docker resources..."
    
    # Remove containers
    if docker ps -a | grep -q pocket-tts; then
        docker rm -f $(docker ps -a | grep pocket-tts | awk '{print $1}') 2>/dev/null || true
        print_success "Containers removed"
    fi
    
    # Remove image
    if docker image inspect pocket-tts:latest > /dev/null 2>&1; then
        read -p "Remove Docker image? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker rmi pocket-tts:latest
            print_success "Image removed"
        fi
    fi
    
    # Remove volumes (optional)
    read -p "Remove Docker volumes (cache)? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker volume rm pocket-tts-cache 2>/dev/null || true
        print_success "Volumes removed"
    fi
    
    print_success "Cleanup complete!"
}

# Main script logic
case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        shift  # Remove 'run' from arguments
        run_demo "$@"
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_up
        ;;
    clear-cache)
        clear_cache
        ;;
    download-help)
        show_download_help
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac
