"""Inspect basic metadata from an uncompressed PCM WAV file."""

import argparse
import json
import wave
from pathlib import Path


def inspect_wav(path: str | Path) -> dict[str, int | float]:
    """Read WAV metadata without loading the audio samples into memory."""
    audio_path = Path(path)
    with wave.open(str(audio_path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        frame_count = wav_file.getnframes()
        sample_width_bytes = wav_file.getsampwidth()

    if sample_rate <= 0:
        raise ValueError("Invalid sample rate in WAV file")

    return {
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "frames": frame_count,
        "sample_width_bytes": sample_width_bytes,
        "duration_seconds": frame_count / sample_rate,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect uncompressed PCM WAV metadata")
    parser.add_argument("file", type=Path, help="Path to a WAV file")
    arguments = parser.parse_args()
    try:
        info = inspect_wav(arguments.file)
    except (OSError, EOFError, ValueError, wave.Error) as error:
        parser.exit(1, f"Unable to inspect WAV file: {error}\n")

    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
