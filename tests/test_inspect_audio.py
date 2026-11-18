"""Tests for the WAV metadata inspector using generated audio."""

import importlib.util
import tempfile
import unittest
import wave
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_audio.py"
SPEC = importlib.util.spec_from_file_location("inspect_audio", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
inspector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inspector)


class InspectAudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def make_wav(self, name: str, sample_rate: int, channels: int, frames: int) -> Path:
        path = self.root / name
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(channels)
            audio.setsampwidth(2)
            audio.setframerate(sample_rate)
            audio.writeframes(b"\x00\x00" * channels * frames)
        return path

    def test_one_second_mono(self) -> None:
        path = self.make_wav("mono.wav", sample_rate=16_000, channels=1, frames=16_000)
        info = inspector.inspect_wav(path)
        self.assertEqual(info["sample_rate_hz"], 16_000)
        self.assertEqual(info["channels"], 1)
        self.assertEqual(info["frames"], 16_000)
        self.assertAlmostEqual(info["duration_seconds"], 1.0)

    def test_two_second_stereo(self) -> None:
        path = self.make_wav("stereo.wav", sample_rate=8_000, channels=2, frames=16_000)
        info = inspector.inspect_wav(path)
        self.assertEqual(info["channels"], 2)
        self.assertAlmostEqual(info["duration_seconds"], 2.0)

    def test_invalid_wav(self) -> None:
        path = self.root / "invalid.wav"
        path.write_text("not an audio file", encoding="utf-8")
        with self.assertRaises((wave.Error, EOFError)):
            inspector.inspect_wav(path)


if __name__ == "__main__":
    unittest.main()
