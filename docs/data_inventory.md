# Data inventory: candidate speech datasets

This document lists public speech datasets that CallSense AI may use for the research problem in [problem.md](problem.md): transcription of spoken monetary amounts in natural two-speaker Hindi-English conversations.

**Status.** This is a desk review of official web pages, dataset cards, and papers, last checked on 2026-11-19. No audio was downloaded, no dataset was loaded, and no evaluation examples were opened. Nothing here has been confirmed by listening to or reading the data.

**Marking.** "Needs verification" means the point could not be confirmed from an official source during this review, or official sources disagree. Statements under "Suitability" are this project's assessment, not claims made by the dataset authors.

## Roles in this project

| Dataset | Role | Rule |
| --- | --- | --- |
| MUCS 2021 / OpenSLR 104, Hindi-English | May be considered for development | No decision to use it has been made yet. |
| CoSHE-Eval | Reserved for final evaluation only | Do not download, listen to, read, or tune on it before the evaluation protocol is fixed. |
| Vaani Benchmark V1.0 | Reserved for final evaluation only | Same rule as CoSHE-Eval. |
| Vaani main corpus (non-benchmark) | Not assigned | Stays unassigned, and unused, until possible speaker and recording overlap with the Vaani Benchmark is independently clarified. See section 3b. |
| IndicVoices | Reserved; not used for development | Same rule as CoSHE-Eval. |

MUCS is the only dataset in this inventory that may be used for development. IndicVoices was reserved by project decision on 2026-11-19; whether it takes part in the final evaluation is not decided.

Reserved means the data is not used for model selection, prompt or decoding choices, normalization rules, error analysis, or examples in documents. Third-party subsets or repackagings of a reserved dataset are reserved too.

## Summary

| | MUCS / OpenSLR 104 (Hi-En) | CoSHE-Eval | Vaani | IndicVoices |
| --- | --- | --- | --- | --- |
| Publisher | MUCS 2021 organisers, hosted by OpenSLR | Soket AI (soketlabs) | IISc Bangalore and ARTPARK | AI4Bharat, IIT Madras |
| Speech style | Narrated technical tutorials | Mixed: conversations, interviews, lectures, podcasts | Spontaneous speech prompted by images | Read, extempore, and conversational |
| Hindi-English code-switching | Yes, mostly technical terms | Yes, by design | Not the focus; Needs verification | Not the focus; Needs verification |
| Size | 89.86 h train, 5.18 h test, 6.24 h blind test | 1,985 clips, about 30 h | About 31,278 h audio, 2,122 h transcribed, all languages | 23.7K h audio, 11.2K h transcribed, all languages |
| License | CC BY-SA 4.0 | CC BY-NC 4.0 on the card; stricter wording in the blog | CC BY 4.0 | CC BY 4.0 |
| Access | Direct download | Public on Hugging Face, not gated | Gated on Hugging Face | Gated on Hugging Face |
| Monetary amounts documented | No | No | No | No |

None of the sources reviewed documents how often monetary amounts occur, and none provides amount-level annotations. Reference amounts for the metric in [problem.md](problem.md) would have to be produced and verified by this project.

## 1. MUCS 2021 / OpenSLR 104

**Official source**

- OpenSLR resource page: <https://www.openslr.org/104/> (identifier SLR104, sub-task 2).
- Challenge site and data page: <https://navana-tech.github.io/MUCS2021/> and <https://navana-tech.github.io/MUCS2021/data.html>.
- Paper: Diwan et al., "Multilingual and code-switching ASR challenges for low resource Indian languages", Interspeech 2021, <https://arxiv.org/abs/2104.00235>.

SLR104 holds two language pairs, Hindi-English and Bengali-English. Only Hindi-English is relevant here. The companion resource SLR103 (sub-task 1) is monolingual Hindi, Marathi, and Odia under a different license, and is out of scope.

**Language and speech characteristics**

- Hindi-English code-switched speech taken from spoken tutorials on computer science topics. The code-switching "predominantly arises from the technical content of the lectures" (OpenSLR page).
- Sizes for Hindi-English: 89.86 h train, 5.18 h test, 6.24 h blind test. Archives on OpenSLR: train 7.3 GB, test 443 MB, and a 1.0 GB blind test archive covering both language pairs.
- 16 kHz sampling rate, 16-bit encoding.
- Speaker identity was not available to the organisers. The paper assumes one speaker per tutorial, giving 520 (train), 30 (test), and 35 (blind test) for Hindi-English.
- The transcriptions were scripts written for video narrators, not transcripts made for ASR. The paper lists known problems in the train and test sets: misaligned segment timestamps, the same English word appearing in both Latin and Devanagari script, punctuation spoken aloud or written as words, incomplete audio at segment edges, and merged English words.
- The blind test transcriptions were manually corrected. The paper reports 33.9% overlap between the Hindi-English test and train sets.
- Whether the audio contains two-speaker conversation: the sources describe narrated tutorials only. Needs verification that there is no dialogue.

**Access requirements**

- Direct download links on the OpenSLR page, with mirrors. No registration or agreement form is shown on the page.
- The MUCS data page lists a "Main" link and a password-free "Mirror1" link. Whether the "Main" link needs a password: Needs verification.

**License or usage restrictions**

- CC BY-SA 4.0, stated on both the OpenSLR page and the MUCS data page. This requires attribution, and adaptations that are shared must carry the same license.
- Whether this project's own annotations of the audio (for example amount labels) count as adapted material under the license: Needs verification before any annotation is published.
- Terms of the underlying spoken-tutorial source material: Needs verification.

**Suitability for the Hinglish monetary-amount task**

- Useful for building and checking the pipeline: loading audio, running a pretrained model, handling mixed-script transcripts, and scoring. The format (16 kHz, 16-bit) matches what `scripts/inspect_audio.py` supports.
- Weak match for the research problem itself. The speech is scripted narration by one speaker about computing, not natural two-speaker conversation, and monetary amounts are probably rare. That last point is an expectation from the domain, not a measurement: Needs verification.
- The label noise in the train and test sets means a mismatch between a model amount and the reference may be a reference error. Any amount reference taken from MUCS would need human verification first.
- The corpus has been public since 2021, so a pretrained model may already have been trained on it. Whether a given model was: Needs verification per model.
- All MUCS partitions, including the blind test, would be development data for this project. None is a final evaluation set.

## 2. CoSHE-Eval

**Official source**

- Dataset card: <https://huggingface.co/datasets/soketlabs/CoSHE-Eval> (publisher account `soketlabs`).
- Publisher's description: "Building CoSHE-Eval: A Code-Switching ASR Benchmark for Hindi-English Speech", dated 12 November 2025, <https://soket.ai/blogs/coshe_eval>.
- No peer-reviewed paper was found. Needs verification.

**Language and speech characteristics**

- An evaluation dataset for ASR on Hindi-English code-mixed speech, with Hindi written in Devanagari and English in Latin script inside the same utterance.
- 1,985 samples, about 30 hours, in one split named `eval`. Segment length runs from 0.60 s to 59.8 s, with a median of 56.9 s. Audio is provided as WAV.
- The blog says the audio was curated from "publicly available sources" covering casual conversations, interviews, educational lectures, and podcasts. It says multi-speaker dialogues are kept intact and that heavily degraded or telephony-quality recordings are not included.
- How many clips are two-speaker conversations, as opposed to lectures or single-speaker podcasts: Needs verification.
- Reference transcriptions were first generated with Gemini 2.5 Pro and then reviewed by human annotators, according to the blog.
- The blog describes inline emotion and tone tags in square brackets. Whether the published `transcription` column contains these tags: Needs verification.
- Sampling rate, and how numbers are written in the references (digits, Hindi words, or English words): Needs verification.

**Access requirements**

- Public on Hugging Face and not gated at the time of review. No access form.

**License or usage restrictions**

- The dataset card declares CC BY-NC 4.0: attribution required, non-commercial use only.
- The blog's legal disclaimer is worded more strictly: a "Research-Only, Non-Commercial License", for academic research and evaluation only, with redistribution and commercially intended derivative datasets not permitted without written consent. Which text governs: Needs verification with the publisher.
- The blog states the dataset is intended solely for ASR evaluation and research.
- The audio comes from public sources. Rights and consent for the underlying recordings are not documented on the card or in the blog: Needs verification. This matters for the project rule that evaluation clips must be authorized.
- Practical consequence under either reading: no CoSHE audio or transcripts in this repository, and no use if the project becomes commercial.

**Suitability for the Hinglish monetary-amount task**

- The closest match in speech style of the datasets reviewed: natural, conversational Hindi-English with mixed-script references.
- Not limited to two-speaker conversations, and not telephony audio, so it does not represent call recordings.
- Whether it contains enough spoken monetary amounts to report a meaningful exact amount match rate is unknown, and must stay unknown until final evaluation because the set is reserved. This is a real risk for the evaluation plan.
- The references were produced by a model and then checked by humans. Amounts used as reference values would need this project's own human verification, done as part of the final evaluation procedure and not before.
- A third-party subset, `Trelis/CoSHE-500` on Hugging Face (500 clips of about 30 s), is derived from CoSHE-Eval. It is not an official source and is reserved under the same rule.

## 3. Vaani and IndicVoices

These are two separate projects from different institutions. They are grouped here because both are large, general-purpose Indian speech corpora and neither was built for code-switching. The Vaani main corpus (3a) and the Vaani Benchmark (3b) are separate releases with different roles.

### 3a. Vaani main corpus

**Official source**

- Project site: <https://vaani.iisc.ac.in/>, by IISc Bangalore and ARTPARK, funded by Google.
- Corpus on Hugging Face: <https://huggingface.co/datasets/ARTPARK-IISc/Vaani>.
- Paper: "VAANI: Capturing the language landscape for an inclusive digital India", <https://arxiv.org/abs/2603.28714>.

**Language and speech characteristics**

- Spontaneous speech in which speakers respond to image prompts. The dataset card reports about 31,278 hours of audio from 156K speakers in 165 districts across 105 languages, with 2,122 hours transcribed. Hindi has the most hours in the per-state figures on the project site.
- The project site says roughly 10% of the data is transcribed.
- Whether any recordings are two-speaker conversations: the sources describe single-speaker responses to images. Needs verification.
- Extent of Hindi-English code-switching, sampling rate, and audio format: Needs verification.

**Access requirements**

- Gated on Hugging Face with automatic approval. A Hugging Face account and access token are required.
- The access form asks for first name, last name, country, company, and intended use (Research, Academic, Commercial, or Education).
- The exact conditions text is shown only after login: Needs verification.

**License or usage restrictions**

- CC BY 4.0, as stated on the project site and in the dataset card metadata. Attribution is required; commercial use is permitted by the license.
- The dataset card asks users to cite the Vaani paper.

**Suitability for the Hinglish monetary-amount task**

- Low for the specific problem. Describing an image is single-speaker and unlikely to be Hindi-English conversation about money. That is an expectation from the collection method, not a measurement: Needs verification.
- Role: not assigned. The corpus is not used for development or evaluation until its possible overlap with the Vaani Benchmark is independently clarified. See "Relationship to the Vaani main corpus" in section 3b.

### 3b. Vaani Benchmark V1.0

**Official source**

- Dataset card: <https://huggingface.co/datasets/ARTPARK-IISc/Vaani-Benchmark-V1.0>, read on 2026-11-19. Hugging Face reports the repository as last modified on 2026-10-30.
- Benchmark paper: "Vaani Benchmark V1.0: An Inclusive Multimodal Benchmark Dataset for Hindi", <https://arxiv.org/abs/2606.21408>. The current version is v2, dated 18 September 2026.

**Published metadata**

Hindi configuration, the one relevant to this project. Each value is shown as stated by the dataset card and by the paper (v2):

| Item | Dataset card | Paper v2 |
| --- | --- | --- |
| Audio segments | 5,050 | 5,050 utterances |
| Duration | Approximately 10.9 hours | 10.91 hours |
| Speakers | 1,062 | 1,062 unique speakers |
| Districts | 102 | 102 |
| States | 22 Indian states | 20 states and 2 Union Territories |
| Transcriptions per segment | Three, by independent human annotators | Three independent transcriptions |
| Split | `test` only | Evaluated as a single test set |
| Speaker IDs | 100000 to 101102 | Not stated |

- The card and the paper agree on segments, duration, speakers, and districts. The card's "22 Indian states" corresponds to the paper's 20 states plus 2 Union Territories.
- The Hindi speaker ID block spans 1,103 possible IDs, which is more than the 1,062 speakers reported. The ID range should not be read as a speaker count. Whether some IDs in the block are unused: Needs verification.
- Earlier version of the paper: v1, dated 19 June 2026, described a larger release of 104 districts in 22 states and Union Territories, 3,252 speakers, and 20.64 hours. Those figures were replaced in v2 and do not describe the published dataset.
- This section covers the Hindi configuration only. Totals for the whole multilingual benchmark are left out because the dataset card is their only source.

**Language and speech characteristics**

- The paper describes spontaneous speech elicited with image prompts and recorded in real-world acoustic conditions.
- Audio is WAV. The card says Hindi has a variable sample rate, while the other languages are 16 kHz.
- The card's scoring method is multi-reference: a hypothesis is aligned against all three references, and a word counts as an error only if it is wrong against all of them. The card links an evaluation toolkit that includes Latin-script normalization for code-switched predictions.
- The repository is tagged "code-switching". How much Hindi-English switching the Hindi portion contains: Needs verification.
- Whether any recordings are two-speaker conversations: the sources describe single-speaker responses to images. Needs verification.

**Access requirements**

- Gated on Hugging Face with automatic approval. Users must log in, agree to share their Hugging Face account information, and accept conditions.
- The exact conditions text is shown only after login: Needs verification.

**License or usage restrictions**

- CC BY 4.0, as stated on the dataset card. Attribution is required; commercial use is permitted by the license.

**Relationship to the Vaani main corpus**

- The card describes the benchmark as a separate, held-out collection, distinct from the publicly released Vaani dataset and built for benchmarking.
- This is the publisher's statement. It does not say explicitly whether people who recorded for the benchmark also appear as speakers in the main corpus, and it has not been confirmed by any source other than the publisher. Speaker and recording overlap: Needs verification.
- Until this is clarified independently, without inspecting benchmark examples, the Vaani main corpus stays unassigned.

**Suitability for the Hinglish monetary-amount task**

- Reserved for final evaluation only.
- Low match for the specific problem, for the same reason as the main corpus: single-speaker image description, not conversation about money. Whether it contains spoken monetary amounts is unknown and must stay unknown until final evaluation.
- Useful as a general check that a model handles spontaneous Hindi from many regions, alongside the task-specific result.
- Three references per segment could help when the same amount can be written in more than one valid way.
- The variable sample rate in the Hindi configuration means audio would need resampling before use with most models.

### 3c. IndicVoices

**Official source**

- Dataset card: <https://huggingface.co/datasets/ai4bharat/IndicVoices>.
- Repository: <https://github.com/AI4Bharat/IndicVoices>.
- Project page: <https://ai4bharat.iitm.ac.in/datasets/indicvoices>. The page content could not be read during this review: Needs verification.
- Paper: Javed et al., "IndicVoices: Towards building an Inclusive Multilingual Speech Dataset for Indian Languages", Findings of ACL 2024, <https://arxiv.org/abs/2403.01926>.

**Language and speech characteristics**

- Natural and spontaneous speech in 22 Indian languages, including Hindi. The dataset card reports 23.7K hours from 51K speakers in more than 400 districts: read (8%), extempore (76%), and conversational (15%). It reports 11.2K hours transcribed as of 23 December 2025.
- These totals have grown across releases. The 2024 paper reports 7,348 hours, and the GitHub README reports 12,000 hours.
- The Hugging Face repository has one configuration per language. The ones checked, including Hindi, have `train` and `valid` splits and no `test` split. Where an official test set is published, if at all: Needs verification.
- Hours of Hindi, the share of Hindi that is conversational, and the number of speakers per conversational recording: Needs verification.
- Extent of Hindi-English code-switching and how English words are written in the transcripts: Needs verification.
- Sampling rate: the repository's preparation steps downsample to 16 kHz, which suggests the released audio uses a different rate. Needs verification.

**Access requirements**

- Gated on Hugging Face with automatic approval. Users must log in, agree to share their Hugging Face account information, and accept conditions. The exact conditions text is shown only after login: Needs verification.
- The dataset card also lists direct archive links for full-length audio. Whether those links apply any access control: Needs verification.

**License or usage restrictions**

- CC BY 4.0, stated on the dataset card. Attribution is required, and the card asks users to cite the paper.

**Suitability for the Hinglish monetary-amount task**

- The conversational portion is the nearest thing among the large corpora to natural multi-party speech.
- It is a monolingual-first collection, so Hindi-English switching and spoken monetary amounts may be uncommon. Needs verification.
- It is reserved and is not used for development. This covers every split, including `train` and `valid`, and any separately published test set.

## Open items

1. CoSHE-Eval: confirm with the publisher which license text governs, and whether rights to the underlying public-source audio are cleared.
2. CoSHE-Eval: confirm whether references contain inline tags and how numbers are written. This must be done from documentation or by asking the publisher, not by reading the data.
3. Vaani: independently clarify whether benchmark speakers or recordings also appear in the main corpus. The dataset card calls the benchmark a separate held-out collection, which is the publisher's statement only. The main corpus stays unassigned until then.
4. Vaani and IndicVoices: read the full gated access conditions after login, and decide whether to accept them and share the requested account details.
5. IndicVoices: confirm Hindi hours, the conversational share, the test set location, and the sampling rate.
6. MUCS: confirm whether published annotations of the audio must be released under CC BY-SA 4.0.
7. All datasets: none documents the presence of monetary amounts. MUCS is the only development candidate and is a weak match for the task, so decide how development data with spoken amounts will be obtained if MUCS contains too few.
8. Decide whether IndicVoices takes part in the final evaluation or stays unused.

## Sources reviewed

All accessed on 2026-11-19.

- <https://www.openslr.org/104/> and <https://www.openslr.org/103/>
- <https://navana-tech.github.io/MUCS2021/data.html>
- <https://arxiv.org/abs/2104.00235> (full text)
- <https://huggingface.co/datasets/soketlabs/CoSHE-Eval> (card text and repository metadata only)
- <https://soket.ai/blogs/coshe_eval>
- <https://huggingface.co/datasets/Trelis/CoSHE-500> (card text only; third party)
- <https://vaani.iisc.ac.in/>, <https://vaani.iisc.ac.in/dataset>, and <https://vaani.iisc.ac.in/dataset/Version1>
- <https://huggingface.co/datasets/ARTPARK-IISc/Vaani> (card text and repository metadata)
- <https://huggingface.co/datasets/ARTPARK-IISc/Vaani-Benchmark-V1.0> (card text and repository metadata)
- <https://arxiv.org/abs/2603.28714> and <https://arxiv.org/abs/2606.21408> (abstracts)
- <https://huggingface.co/datasets/ai4bharat/IndicVoices> (card text and repository metadata)
- <https://github.com/AI4Bharat/IndicVoices>
- <https://arxiv.org/abs/2403.01926> (abstract)

## Review notes

- Reserved datasets were researched through card text, repository metadata, and publisher pages only. Dataset viewers and files were not opened.
- The Vaani Benchmark card was read as extracted text around its statistics and descriptions, with non-Latin script removed, so no transcript examples were viewed.
- One search-engine result for the CoSHE-Eval page displayed a single line of transcript text in its preview. It was not recorded or used.
- The CoSHE-Eval card contains one short illustrative sentence in a code example. Whether it comes from the dataset is not stated.
