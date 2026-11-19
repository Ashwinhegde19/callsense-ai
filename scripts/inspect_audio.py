"""Inspect basic metadata and peak amplitude of a 16-bit PCM WAV file."""

import argparse
import array
import json
import sys
import wave
from pathlib import Path


SUPPORTED_SAMPLE_WIDTH_BYTES = 2
FULL_SCALE = 32768  # Magnitude of the most negative 16-bit sample.
CHUNK_FRAMES = 65536


def _peak_amplitude(wav_file: wave.Wave_read) -> float:
    """Return the largest absolute sample value, scaled to 0.0-1.0.

    Frames are read in fixed-size chunks, so memory use does not grow with
    the length of the recording. Channels are interleaved in the frame data,
    so the peak is taken across every channel.
    """
    peak = 0
    while True:
        chunk = wav_file.readframes(CHUNK_FRAMES)
        if not chunk:
            break
        samples = array.array("h")
        samples.frombytes(chunk)
        if sys.byteorder == "big":
            samples.byteswap()  # WAV samples are little-endian.
        peak = max(peak, max(samples), -min(samples))
    return peak / FULL_SCALE


def inspect_wav(path: str | Path) -> dict[str, int | float]:
    """Read WAV metadata and peak amplitude without loading the whole file."""
    audio_path = Path(path)
    with wave.open(str(audio_path), "rb") as wav_file:
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        frame_count = wav_file.getnframes()
        sample_width_bytes = wav_file.getsampwidth()

        if sample_rate <= 0:
            raise ValueError("Invalid sample rate in WAV file")
        if sample_width_bytes != SUPPORTED_SAMPLE_WIDTH_BYTES:
            raise ValueError(
                f"Unsupported sample format: {sample_width_bytes * 8}-bit PCM "
                "(only 16-bit PCM is supported)"
            )

        peak_amplitude = _peak_amplitude(wav_file)

    return {
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "frames": frame_count,
        "sample_width_bytes": sample_width_bytes,
        "duration_seconds": frame_count / sample_rate,
        "peak_amplitude": peak_amplitude,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect 16-bit PCM WAV metadata")
    parser.add_argument("file", type=Path, help="Path to a WAV file")
    arguments = parser.parse_args()
    try:
        info = inspect_wav(arguments.file)
    except (OSError, EOFError, ValueError, wave.Error) as error:
        parser.exit(1, f"Unable to inspect WAV file: {error}\n")

    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
