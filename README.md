# CallSense AI

CallSense AI is an experimental speech recognition and inference engineering project focused on Hindi-English conversations.

The repository will grow through reproducible work on audio processing, ASR evaluation, streaming inference, and performance measurements. Results will be published with methods and limitations.

## Requirements

- Python 3.10 or newer

## Inspect a WAV file

Run:

```bash
python scripts/inspect_audio.py path/to/recording.wav
```

The inspector reports the sample rate, number of channels, frame count, and duration of an uncompressed PCM WAV recording.

## Run tests

```bash
python -m unittest discover -s tests -v
```

Tests generate audio in temporary directories. No example recordings or external datasets are needed.

## Data handling

Keep local recordings, dataset manifests, model weights, credentials, and generated artifacts outside version control. Only publish audio or annotations when licensing and consent allow it.

## Status

Initial audio inspection utilities are available. ASR model evaluation and streaming functionality are not implemented yet.
