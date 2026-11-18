# Research problem: monetary amounts in Hindi-English conversations

## Problem statement

In natural two-speaker Hindi-English (Hinglish) conversations, speakers state monetary amounts in ways that mix both languages: English number words, Hindi number words, compound forms such as "dhai hazaar" (2,500) or "saadhe teen hazaar" (3,500), and shorthand such as "thirty-six fifty" (3,650). Speakers also restate, question, and correct amounts mid-conversation.

A transcript that gets an amount wrong is wrong in the way that matters most for many uses of a call transcript, even when the rest of the sentence is recognized well. The initial research problem for CallSense AI is therefore:

> How often do automatic speech recognition (ASR) models transcribe a spoken monetary amount incorrectly in natural two-speaker Hindi-English conversations?

### Scope: transcription, not interpretation

The task is ASR transcription of every monetary amount actually spoken. An amount that a speaker later corrects, retracts, or rejects was still spoken, and a faithful transcript must contain it with the value that was spoken.

In the refund example below:

- Spoken INR 2,550 must be transcribed as INR 2,550.
- Spoken INR 2,450 must be transcribed as INR 2,450.
- Determining that INR 2,450 is the final refund is a separate conversation-understanding task. It is out of scope for this problem.

A transcript that omits the retracted INR 2,550, or replaces it with INR 2,450, is incorrect for this task even though INR 2,450 is the amount the speakers settle on.

## Illustrative examples

Both conversations below are fictional. They were written for this document, are not transcripts of real recordings, and do not describe real people or organizations. They are romanized for readability.

Each table lists every amount mention in the order it is spoken. Every row is a transcription target, whether or not the amount is later corrected or rejected. The last column is context for the reader and is not part of the task.

### Example 1: refund call

> **Speaker A:** Hello, main courier helpdesk se bol rahi hoon. Aapka refund process ho gaya hai.
>
> **Speaker B:** Achha, kitna refund aaya hai? Maine toh dhai hazaar pay kiye the.
>
> **Speaker A:** System mein two thousand five hundred fifty dikh raha hai... ek minute, sorry, galat line dekh li. Correct amount hai two thousand four hundred fifty rupees.
>
> **Speaker B:** Matlab chaubees sau pachaas?
>
> **Speaker A:** Ji haan, chaubees sau pachaas.

| # | Speaker | Spoken form | Reference amount (INR) | Context (not scored) |
| --- | --- | --- | --- | --- |
| 1 | B | dhai hazaar | 2,500 | Amount originally paid |
| 2 | A | two thousand five hundred fifty | 2,550 | Later retracted by the same speaker |
| 3 | A | two thousand four hundred fifty | 2,450 | Stated as the correction |
| 4 | B | chaubees sau pachaas | 2,450 | Asked as confirmation |
| 5 | A | chaubees sau pachaas | 2,450 | Confirmed |

A correct transcript of this clip contains both INR 2,550 (mention 2) and INR 2,450 (mentions 3 to 5). Deciding that INR 2,450 is the final refund is the separate conversation-understanding task.

### Example 2: splitting a dinner bill

> **Speaker A:** Kal ke dinner ka bill kitna hua tha?
>
> **Speaker B:** Total saadhe teen hazaar ke aas-paas tha, I think thirty-six fifty.
>
> **Speaker A:** Thirty-six fifty nahi yaar, tip mila ke thirty-seven fifty hua tha. Maine receipt check kiya.
>
> **Speaker B:** Okay, toh teen log hain, har ek ka barah sau pachaas.
>
> **Speaker A:** Theek hai, main tujhe barah sau pachaas UPI kar deta hoon.

| # | Speaker | Spoken form | Reference amount (INR) | Context (not scored) |
| --- | --- | --- | --- | --- |
| 1 | B | saadhe teen hazaar (ke aas-paas) | 3,500 | Approximate recollection |
| 2 | B | thirty-six fifty | 3,650 | Later rejected by the other speaker |
| 3 | A | thirty-six fifty | 3,650 | Repeated while rejecting it |
| 4 | A | thirty-seven fifty | 3,750 | Stated as the correction |
| 5 | B | barah sau pachaas | 1,250 | Per-person share (3,750 / 3) |
| 6 | A | barah sau pachaas | 1,250 | Repeated when agreeing to pay |

A correct transcript of this clip contains both INR 3,650 (mentions 2 and 3) and INR 3,750 (mention 4).

In both examples an amount that is later corrected or rejected sits next to a similar-sounding amount that replaces it. For this task both are treated the same way: each must appear in the transcript with the value that was spoken. A model that transcribes spoken INR 2,550 as INR 2,450, or spoken INR 3,650 as INR 3,750, has made a transcription error, even though the amount it wrote is the one the speakers finally agree on.

## Hypothesis

Pretrained ASR models, used without fine-tuning, may confuse spoken monetary amounts in natural two-speaker Hindi-English conversations, so that the amount in the model transcript differs from the amount that was spoken.

The hypothesis covers every amount mention, including amounts that are later corrected or rejected. It is a claim about transcription only. It makes no claim about whether a model, or any system built on its transcript, can tell which amount is final.

This is testable: on a set of clips with human-verified reference amounts, the exact amount match rate defined below is either at or near 100% (evidence against the hypothesis) or clearly below it (evidence for it). The threshold that separates the two outcomes must be fixed before any model is run, not after results are seen.

Possible sources of confusion, listed as conjectures and not as findings:

- Switching between English and Hindi number words inside one amount or one turn.
- Hindi compound and fractional forms (dedh, dhai, saadhe, sau-based forms such as "chaubees sau").
- Similar-sounding number words (for example pachees / pachaas, fifteen / fifty).
- Shorthand that omits units ("thirty-six fifty").
- Restated and corrected amounts close together, sometimes across a speaker change, where a model might drop one of two similar amounts or write the same value for both.

## Proposed measurement

The unit of measurement is the amount mention: one spoken occurrence of a monetary amount. Every mention counts, including amounts that are later corrected or rejected and amounts that are repeated. For each amount mention in a clip:

1. **Reference amount.** A human listens to the clip and records the amount that was spoken as a numeric value. The annotator records what was said, not what was meant, and does not mark which amount is final. A second check verifies it.
2. **Predicted amount.** The model transcribes the same clip, and the amount is read from the model transcript and converted to a numeric value using the same normalization rules as the reference.
3. **Comparison.** The mention counts as a match only if the predicted numeric value equals the reference numeric value exactly.

The reported metric is the **exact amount match rate**:

```text
exact amount match rate = matched amount mentions / total reference amount mentions
```

A reference amount with no corresponding amount in the model transcript counts as a mismatch.

Applied to the fictional examples, the refund call has five reference amount mentions (2,500; 2,550; 2,450; 2,450; 2,450) and the dinner bill has six (3,500; 3,650; 3,650; 3,750; 1,250; 1,250). If only the INR 2,550 mention is transcribed as INR 2,450, while the other four mentions are correct, the exact amount match rate is 4/5 (80%).

The metric does not score whether a system identifies the final, corrected, or agreed amount. That belongs to the separate conversation-understanding task and would need its own reference labels and its own metric.

The metric is reported only on **authorized development clips**: recordings that the project has consent and licensing to use for evaluation, in line with the data handling rules in the README. The count of clips and amount mentions is reported alongside the rate.

Still to be defined before any measurement is run:

- Normalization rules for turning spoken forms into numeric values, including approximate amounts ("ke aas-paas") and shorthand.
- How a predicted amount is paired with a reference amount when a clip contains several.
- How amounts are read from the model transcript, so that extraction errors are not counted as recognition errors.
- How amounts that appear in the model transcript but were never spoken are reported, since the rate above only counts reference mentions.

## Limitations

- **No experiments have been run.** No model has been evaluated for this problem.
- **No data has been collected.** There are no development clips, reference annotations, or manifests yet.
- **The hypothesis is unverified.** It is a starting assumption. It may turn out to be false, or true only for some models, amount forms, or recording conditions.
- **The examples are fictional.** They illustrate the kind of speech in scope and are not evidence that models fail on it.
- **Conversation understanding is out of scope.** This problem covers transcription of spoken amounts only. Whether a system can identify the final or corrected amount is not defined or measured here.
- **The metric is narrow.** Exact amount match rate does not measure overall transcription quality, does not say why an amount was wrong, and by itself cannot separate recognition errors from errors in normalization or extraction.
- **Results will not generalize automatically.** Any future result will describe the specific clips, speakers, and models tested.
