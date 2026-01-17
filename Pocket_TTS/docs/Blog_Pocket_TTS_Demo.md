<!-- cspell:disable -->
# Pocket TTS Demo: I cloned Rajnikanth's voice on my machine, kinda!

![Pocket TTS Blog Banner](./pocket_tts_blog_banner.png)


I tried [`pocket-tts` from kyutai labs](https://github.com/kyutai-labs/pocket-tts) and, with a short audio clip, ended up with a voice that sounded oddly familiar. No GPU setup, no cloud stack, just with my mac. 

Pocket TTS is a lightweight, CPU-friendly TTS demo. It can speak with a built-in voice or clone a voice from a short audio clip. 

**🔗 Demo Repository:** [Check out the full demo on GitHub](https://github.com/saru2020/AI_POCs/blob/main/Pocket_TTS)

The repo stays lean: one entry script (`src/pocket_tts_demo.py`), a Docker runner (`run.sh`), and helpers that keep the flow smooth. 
Both paths lead to the same moment: your text turns into a WAV file under `output/`.

## The quick path

If you like containers, the flow is:

```bash
./run.sh build
./run.sh run --voice alba --text "Hello, this is a test" --output /app/output/test.wav
```

If you prefer Python:

```bash
pip install pocket-tts --no-deps
pip install -r requirements.txt
python src/pocket_tts_demo.py --voice alba --text "Hello world" --output output/test.wav
```

You can play the audio afterward (macOS example):

```bash
afplay output/test.wav
```

## Voice cloning in three small steps

Voice cloning is optional and gated by the model access rules. The repo already includes a demo input file (`input/rajni_audio.wav`) so you can try it quickly.

1. **Accept the model terms**
   - Visit https://huggingface.co/kyutai/pocket-tts and click "Agree and access repository".

2. **Get a Hugging Face token**
   - Create a token at https://huggingface.co/settings/tokens.

3. **Run the demo with your audio**
   - With Docker:
     ```bash
     HUGGINGFACE_HUB_TOKEN=your_token ./run.sh run \
       --audio-file /app/input/rajni_audio.wav \
       --text "You know what: Anger! Anger is the cause of all miseries, one should know how to control it; otherwise life becomes miserable; and hey, last but not least" \
       --output /app/output/test.wav
     ```
   - With Python:
     ```bash
     python src/pocket_tts_demo.py \
       --audio-file input/rajni_audio.wav \
       --text "You know what: Anger! Anger is the cause of all miseries, one should know how to control it; otherwise life becomes miserable; and hey, last but not least" \
       --output output/test.wav
     ```

That is it. The script loads the model, extracts a voice state from your audio file, and generates speech from your text. The output is a WAV you can play or share.

## A small ending

The best part of this demo is how compact it feels. A short audio clip in `input/`, a line of text, and a single command later you have a voice that sounds familiar reading something new. If you want to skim the mechanics, start with `Pocket_TTS/README.md`. If you want to hear it, just play/run the audio/demo.
