# First results: synthetic batch 1 (preliminary)

**Status: preliminary, synthetic speech only, not human-verified.**

This document records the first measurements made for the research problem in [problem.md](problem.md). They were produced on 2026-11-23 and 2026-11-24.

**Read this first.** These results are preliminary. Every clip is synthetic speech from one text-to-speech voice. No person has listened to any clip. The results say how some models handle clear, generated speech containing rupee amounts. They do not test the project's hypothesis, which is about natural two-speaker conversations.

## What was tested

**Sentences.** The 42 sentences in `synthetic/amount_cases.csv`, containing 52 intended amounts across eight categories: standard amounts, look-alike amounts, Hindi compound forms, English forms, large amounts, corrections, several amounts in one sentence, and amounts next to other numbers.

**Speech.** Each sentence was spoken once by the Indus-Labs `indus-pocket-tts` model (compressed weights, voice "Inaya") with a fixed random seed. Each clip exists in two audio conditions:

- `clean`: 16 kHz mono.
- `phone_noise`: the same clip limited to 300 to 3,400 Hz, resampled through 8 kHz, with pink noise added.

**Models.** No model was given the reference text, a prompt containing the answer, or a language hint.

| Model | How it was run | Settings |
| --- | --- | --- |
| Sarvam Saaras v4 | Sarvam API | Language detection on. Two output modes: "transcribe", which writes numbers as digits, and "verbatim", which writes them as spoken. |
| Whisper large-v3 | Groq API | Temperature 0. |
| Whisper small | Locally with faster-whisper 1.2.1, CPU, 8-bit weights | Default decoding with temperature fallback. |
| NVIDIA Nemotron 3 Nano Omni 30B | NVIDIA API | Prompt "Transcribe this audio.", reasoning off. NVIDIA documents this model as English only. |

**Scoring.** `scripts/amount_scoring.py`, with the strict and lenient scores defined in [evaluation_protocol.md](evaluation_protocol.md). All 52 intended amounts are read correctly by the scorer from the exact words given to the speech model.

## Results

Every number in this section is preliminary: synthetic speech, scored against the amounts each sentence was written to contain, with no clip checked by a person.

Exact amount match, out of 52 intended amounts per condition.

| Model | Clean, strict | Clean, lenient | Phone and noise, strict | Phone and noise, lenient |
| --- | --- | --- | --- | --- |
| Sarvam Saaras v4, digits mode | 51 (98%) | 51 (98%) | 50 (96%) | 50 (96%) |
| Sarvam Saaras v4, as-spoken mode | 50 (96%) | 50 (96%) | 50 (96%) | 50 (96%) |
| Whisper large-v3 | 44 (85%) | 50 (96%) | 40 (77%) | 49 (94%) |
| Whisper small | 16 (31%) | 25 (48%) | 17 (33%) | 23 (44%) |
| Nemotron 3 Nano Omni | 9 (17%) | 9 (17%) | Not run | Not run |

Clean audio by category, shown as strict / lenient matches out of the category total:

| Category | Amounts | Saaras v4, digits | Saaras v4, as spoken | Whisper large-v3 | Whisper small |
| --- | --- | --- | --- | --- | --- |
| Standard amounts | 5 | 5 / 5 | 5 / 5 | 4 / 5 | 2 / 3 |
| Look-alike amounts | 8 | 8 / 8 | 8 / 8 | 7 / 8 | 2 / 4 |
| Hindi compound forms | 6 | 5 / 5 | 5 / 5 | 4 / 5 | 1 / 2 |
| English forms | 5 | 5 / 5 | 4 / 4 | 4 / 4 | 2 / 2 |
| Large amounts | 5 | 5 / 5 | 5 / 5 | 5 / 5 | 0 / 2 |
| Corrections | 8 | 8 / 8 | 8 / 8 | 8 / 8 | 5 / 6 |
| Several amounts in one sentence | 10 | 10 / 10 | 10 / 10 | 7 / 10 | 2 / 4 |
| Amount next to other numbers | 5 | 5 / 5 | 5 / 5 | 5 / 5 | 2 / 2 |

## What the misses were

- **Clip C03 ("साढ़े तीन हज़ार", 3,500).** Every model wrote a form of "टाडे तीन हज़ार" and so read 3,000. Four models agreeing on the same wrong sound suggests the synthetic voice mis-spoke the sentence. This clip should be listened to by a person. It is a miss for every model in the tables above; without it each total is out of 51.
- **Clip D04 ("ninety nine").** Both Whisper models wrote "Menti 9". Sarvam and Nemotron wrote it correctly, so the recording appears sound and this is a recognition error.
- **Clip D02 ("thirty six fifty").** Sarvam's as-spoken mode wrote "टर्डी सिक्स फिफ्टी" on clean audio. Its digits mode wrote 3,650.
- **Whisper large-v3 spelling.** Six of its strict misses on clean audio are number words spelled non-standardly, such as "सो" for "सौ" and "साथ" for "सात". The lenient score accepts them.
- **Whisper small.** Most number words are misspelled, run together, or partly dropped. The lenient score recovers 9 of its 36 strict misses on clean audio. Many of the rest have a word missing, for example "एक हजार सो पतास" for 1,450.
- **Nemotron 3 Nano Omni.** It wrote Hindi in Latin letters for all 42 clips, for example "bara hazar panch so rupe" for 12,500. The scorer does not read Latin-script Hindi, so its score counts only amounts it wrote in English words or digits. Its score here is not a measure of what it heard. An informal reading of its transcripts suggests most amounts are present.

## Machine check

Following the rule in [evaluation_protocol.md](evaluation_protocol.md), a clean clip was marked `machine_checked` when both Whisper large-v3 and Sarvam Saaras v4 (digits mode) recovered every intended amount under the lenient reading.

- 40 of the 42 clean clips passed.
- C03 failed for both models and D04 failed for Whisper large-v3. Both stay `unverified`.
- The `phone_noise` clips were not marked.

`machine_checked` is not human verification. No row is `verified` or `double_checked`, so under the protocol none of these results is official.

## What can and cannot be concluded

**Supported by these results, for this synthetic batch only**

- On clear synthetic speech, the two large models transcribed almost every amount, including look-alike amounts, corrections, and sentences with several amounts.
- The small Whisper model did not: fewer than half of the amounts were readable even leniently.
- How a model writes numbers matters. Writing digits or correctly spelled words scores well; near-miss spellings cost Whisper large-v3 eleven points between its lenient and strict scores on clean audio.
- The telephone-band and noise treatment used here made little difference to the large models.

**Not supported**

- Nothing here says how any model performs on real two-speaker conversations. The hypothesis in [problem.md](problem.md) remains untested.
- The speech model's authors used Whisper large-v3 to check its output, so this audio is likely to suit that model.
- There is one take per sentence and 52 amounts in total. Categories hold five to ten amounts, so one clip changes a category by 10 to 20 points.
- The machine check favours the two models that performed it, because clips they misheard are the ones left unmarked.
- The noise treatment was mild and was not calibrated to a measured signal-to-noise ratio.

## Known gaps in the scorer

- Hindi written in Latin letters ("dhai hazaar") is not read.
- Digit shorthand such as "36-50" for 3,650 or "12-100" for 1,200 is read as two numbers.
- The lenient reading sometimes turns ordinary words into numbers. These never count as matches but add noise.

## Reproducing

Tracked in this repository: the sentences (`synthetic/amount_cases.csv`), the scorer and its tests, and the protocol.

Not tracked: the generated audio, the raw transcripts, the per-clip scores, and the scripts that generated speech and called each model. They exist only in the local `data/` and `outputs/` folders. Reproducing these numbers from a fresh clone would need those scripts to be added to the repository, and the speech model, API accounts, and seeds described above.
