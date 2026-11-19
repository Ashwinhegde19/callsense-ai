"""Tests for the WAV metadata inspector using generated audio."""

import importlib.util
import struct
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock


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

    def make_wav_from_samples(self, name: str, channels: int, samples: list[int]) -> Path:
        """Write 16-bit samples, interleaved by channel, at 16 kHz."""
        path = self.root / name
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(channels)
            audio.setsampwidth(2)
            audio.setframerate(16_000)
            audio.writeframes(struct.pack(f"<{len(samples)}h", *samples))
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

    def test_silent_wav_has_zero_peak(self) -> None:
        path = self.make_wav("silent.wav", sample_rate=16_000, channels=1, frames=1_600)
        info = inspector.inspect_wav(path)
        self.assertEqual(info["peak_amplitude"], 0.0)

    def test_peak_uses_absolute_magnitude(self) -> None:
        # The largest positive sample is 8192 (0.25); the largest magnitude is -16384 (0.5).
        path = self.make_wav_from_samples("signed.wav", channels=1, samples=[0, 8192, -16384, 4096])
        info = inspector.inspect_wav(path)
        self.assertEqual(info["peak_amplitude"], 0.5)

    def test_full_scale_samples_stay_within_range(self) -> None:
        negative = self.make_wav_from_samples("negative.wav", channels=1, samples=[0, -32768])
        positive = self.make_wav_from_samples("positive.wav", channels=1, samples=[0, 32767])
        self.assertEqual(inspector.inspect_wav(negative)["peak_amplitude"], 1.0)
        self.assertEqual(inspector.inspect_wav(positive)["peak_amplitude"], 32767 / 32768)

    def test_stereo_peak_in_right_channel(self) -> None:
        # Interleaved as left, right. Left peaks at 4000; right peaks at 24576 (0.75).
        samples = [1000, -2000, 3000, 24576, -4000, 500]
        path = self.make_wav_from_samples("stereo_peak.wav", channels=2, samples=samples)
        info = inspector.inspect_wav(path)
        self.assertEqual(info["channels"], 2)
        self.assertEqual(info["frames"], 3)
        self.assertEqual(info["peak_amplitude"], 0.75)

    def test_peak_found_across_chunks(self) -> None:
        samples = [100] * 10 + [-16384]
        path = self.make_wav_from_samples("chunked.wav", channels=1, samples=samples)
        with mock.patch.object(inspector, "CHUNK_FRAMES", 4):
            info = inspector.inspect_wav(path)
        self.assertEqual(info["peak_amplitude"], 0.5)

    def test_unsupported_sample_width_is_rejected(self) -> None:
        path = self.root / "eight_bit.wav"
        with wave.open(str(path), "wb") as audio:
            audio.setnchannels(1)
            audio.setsampwidth(1)
            audio.setframerate(16_000)
            audio.writeframes(b"\x80" * 160)
        with self.assertRaisesRegex(ValueError, "8-bit PCM"):
            inspector.inspect_wav(path)


if __name__ == "__main__":
    unittest.main()
