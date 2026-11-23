"""Read numbers out of a transcript and score spoken monetary amounts.

The scoring follows docs/problem.md: every reference amount mention counts, and a
mention is matched only when the transcript contains exactly the same numeric value.

Numbers are recognised when written as digits, as Hindi number words in Devanagari,
or as English number words. Romanised Hindi ("dhai hazaar") and English words written
in Devanagari are not recognised yet.

Two readings are available. The strict reading accepts only correctly spelled number
words. The lenient reading also accepts common misspellings of Hindi number words.
"""

import re
import unicodedata
from fractions import Fraction

Number = int | float

_HINDI_UNITS = {
    0: "शून्य", 1: "एक", 2: "दो", 3: "तीन", 4: "चार", 5: "पाँच", 6: "छह छः छे छ", 7: "सात", 8: "आठ", 9: "नौ",
    10: "दस", 11: "ग्यारह", 12: "बारह", 13: "तेरह", 14: "चौदह", 15: "पंद्रह पन्द्रह", 16: "सोलह", 17: "सत्रह",
    18: "अठारह अट्ठारह", 19: "उन्नीस", 20: "बीस", 21: "इक्कीस", 22: "बाईस बाइस", 23: "तेईस तेइस", 24: "चौबीस",
    25: "पच्चीस पचीस", 26: "छब्बीस", 27: "सत्ताईस सत्ताइस", 28: "अट्ठाईस अट्ठाइस अठाईस", 29: "उनतीस उन्तीस",
    30: "तीस", 31: "इकतीस इकत्तीस", 32: "बत्तीस", 33: "तैंतीस तैतीस", 34: "चौंतीस चौतीस", 35: "पैंतीस पैतीस",
    36: "छत्तीस", 37: "सैंतीस सैतीस", 38: "अड़तीस", 39: "उनतालीस उन्तालीस", 40: "चालीस", 41: "इकतालीस",
    42: "बयालीस बयालिस", 43: "तैंतालीस तैतालीस", 44: "चवालीस चौवालीस", 45: "पैंतालीस पैतालीस",
    46: "छियालीस छयालीस", 47: "सैंतालीस सैतालीस", 48: "अड़तालीस", 49: "उनचास उन्चास", 50: "पचास",
    51: "इक्यावन", 52: "बावन", 53: "तिरपन तिरेपन", 54: "चौवन चौअन", 55: "पचपन", 56: "छप्पन", 57: "सत्तावन",
    58: "अट्ठावन अठावन", 59: "उनसठ", 60: "साठ", 61: "इकसठ", 62: "बासठ", 63: "तिरसठ तिरेसठ", 64: "चौंसठ चौसठ",
    65: "पैंसठ पैसठ", 66: "छियासठ छयासठ", 67: "सड़सठ सरसठ", 68: "अड़सठ", 69: "उनहत्तर", 70: "सत्तर",
    71: "इकहत्तर", 72: "बहत्तर", 73: "तिहत्तर", 74: "चौहत्तर", 75: "पचहत्तर", 76: "छिहत्तर", 77: "सतहत्तर",
    78: "अठहत्तर", 79: "उनासी उन्यासी", 80: "अस्सी", 81: "इक्यासी", 82: "बयासी", 83: "तिरासी", 84: "चौरासी",
    85: "पचासी", 86: "छियासी", 87: "सत्तासी", 88: "अट्ठासी अठासी", 89: "नवासी", 90: "नब्बे",
    91: "इक्यानवे इक्यानबे", 92: "बानवे बानबे", 93: "तिरानवे तिरानबे", 94: "चौरानवे चौरानबे",
    95: "पंचानवे पचानवे पंचानबे", 96: "छियानवे छियानबे", 97: "सत्तानवे सत्तानबे",
    98: "अट्ठानवे अठानवे अट्ठानबे", 99: "निन्यानवे निन्यानबे",
}
_ENGLISH_ONES = "zero one two three four five six seven eight nine".split()
_ENGLISH_TEENS = "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_ENGLISH_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
_MULTIPLIERS = {
    "सौ": 100, "हज़ार": 1_000, "लाख": 100_000, "करोड़": 10_000_000, "अरब": 1_000_000_000,
    "hundred": 100, "thousand": 1_000, "lakh": 100_000, "lakhs": 100_000, "lac": 100_000, "lacs": 100_000,
    "crore": 10_000_000, "crores": 10_000_000, "million": 1_000_000, "billion": 1_000_000_000,
}
# Words that stand for a number by themselves: डेढ़ सौ is 150, ढाई हज़ार is 2,500.
_FRACTION_NUMBERS = {"डेढ़": Fraction(3, 2), "ढाई": Fraction(5, 2), "अढ़ाई": Fraction(5, 2)}
# Words that adjust the number that follows: साढ़े तीन is 3.5, सवा दो is 2.25, पौने दो is 1.75.
_FRACTION_PREFIXES = {"साढ़े": Fraction(1, 2), "सवा": Fraction(1, 4), "पौने": Fraction(-1, 4)}

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
_TOKEN = re.compile(r"\d+(?:,\d+)*(?:\.\d+)?|[a-z]+|[ऀ-ॣ॰-ॿ]+|[,;:.!?।॥()]")


def _normalize(text: str) -> str:
    """Lowercase and remove spelling differences that do not change the word."""
    text = unicodedata.normalize("NFC", text).lower().translate(_DEVANAGARI_DIGITS)
    return text.replace("़", "").replace("ँ", "ं")  # drop nukta; chandrabindu to anusvara


def _build_lexicon() -> dict[str, tuple[str, Fraction]]:
    lexicon: dict[str, tuple[str, Fraction]] = {}
    for value, spellings in _HINDI_UNITS.items():
        for spelling in spellings.split():
            lexicon[_normalize(spelling)] = ("number", Fraction(value))
    for value, word in enumerate(_ENGLISH_ONES):
        lexicon[word] = ("english_one", Fraction(value))
    for value, word in enumerate(_ENGLISH_TEENS, start=10):
        lexicon[word] = ("number", Fraction(value))
    for index, word in enumerate(_ENGLISH_TENS, start=2):
        lexicon[word] = ("english_ten", Fraction(index * 10))
    for word, value in _MULTIPLIERS.items():
        lexicon[_normalize(word)] = ("multiplier", Fraction(value))
    for word, value in _FRACTION_NUMBERS.items():
        lexicon[_normalize(word)] = ("number", value)
    for word, value in _FRACTION_PREFIXES.items():
        lexicon[_normalize(word)] = ("prefix", value)
    lexicon["point"] = ("point", Fraction(0))
    lexicon["and"] = ("and", Fraction(0))
    return lexicon


_LEXICON = _build_lexicon()


# Spelling-tolerant reading. A Devanagari word is reduced to a rough sound key, so that
# common misspellings of a number word still find it: सो for सौ, लाक for लाख, देर for डेढ़.
_FOLD_LETTERS = str.maketrans("खघछझठढथधफभशषणऔऐईऊौैीू", "कगचजटडतदपबससनओएइउोेिु")
_FOLD_DROP = str.maketrans("", "", "ंः्‌‍")  # anusvara, visarga, virama, joiners
_OTHER = ("other", Fraction(0))


def _fold(word: str) -> str:
    word = word.translate(_FOLD_DROP).translate(_FOLD_LETTERS)
    if word.startswith("ड"):
        word = "द" + word[1:]
    word = word.replace("ड", "र")  # the flap in साढ़े and डेढ़ is usually written र
    return re.sub(r"(.)\1+", r"\1", word)  # doubled letters count once


_FOLDED = {
    _fold(word): entry
    for word, entry in _LEXICON.items()
    if not word.isascii() and entry[0] in ("number", "multiplier", "prefix")
}
_CURRENCY_ENDINGS = {_fold(_normalize(word)) for word in "रुपये रुपए रुपया रुपे रुपै रूपे".split()}


def _split_run_together(folded: str, parts_left: int = 4) -> list[tuple[str, Fraction]] | None:
    """Split a run-together word such as चारसो (चार सौ) into known number words."""
    if not folded or folded in _CURRENCY_ENDINGS:
        return []
    if parts_left == 0:
        return None
    for end in range(len(folded), 1, -1):
        entry = _FOLDED.get(folded[:end])
        if entry is not None:
            rest = _split_run_together(folded[end:], parts_left - 1)
            if rest is not None:
                return [entry, *rest]
    return None


def _read_tolerantly(word: str) -> list[tuple[str, Fraction]]:
    folded = _fold(word)
    if folded in _FOLDED:
        return [_FOLDED[folded]]
    return _split_run_together(folded) or []


def _is_devanagari_word(raw: str) -> bool:
    return "ऀ" <= raw[0] <= "ॿ" and raw[0] not in "।॥"


def _tokenize(text: str, lenient: bool = False) -> list[tuple[str, Fraction]]:
    raws = _TOKEN.findall(_normalize(text))
    tokens = []
    index = 0
    while index < len(raws):
        raw = raws[index]
        index += 1
        if raw[0].isdigit():
            tokens.append(("literal", Fraction(raw.replace(",", ""))))
            continue
        entry = _LEXICON.get(raw)
        if entry is None and lenient and _is_devanagari_word(raw):
            parts = _read_tolerantly(raw)
            following = raws[index] if index < len(raws) else ""
            if not parts and following and _is_devanagari_word(following) and following not in _LEXICON:
                parts = _read_tolerantly(raw + following)  # a number word written as two: उन तालीस
                if parts:
                    index += 1
            if parts:
                tokens.extend(parts)
                continue
        tokens.append(entry or _OTHER)
    return tokens


def _as_number(value: Fraction) -> Number:
    return int(value) if value.denominator == 1 else float(value)


def extract_numbers(text: str, lenient: bool = False) -> list[Number]:
    """Return every number written or spelled out in the text, in order.

    All numbers are returned, including ones that are not money, such as dates.

    With lenient=True, Hindi number words are also recognised when misspelled in ways
    that keep roughly the same sound, when run together, or when split in two. This
    reads more real amounts but also turns some ordinary words into numbers, for
    example साथ ("with") into 7. It never changes how correctly spelled text is read.
    """
    tokens = _tokenize(text, lenient)
    results: list[Number] = []
    total = Fraction(0)  # value of completed thousand, lakh, and crore groups
    current: Fraction | None = None  # the group being read
    largest_group: Fraction | None = None
    prefix: Fraction | None = None
    after_hundred = after_english_ten = after_word_number = used_shorthand = False

    def flush() -> None:
        nonlocal total, current, largest_group, prefix
        nonlocal after_hundred, after_english_ten, after_word_number, used_shorthand
        if current is not None or total:
            results.append(_as_number(total + (current or 0)))
        total, current, largest_group, prefix = Fraction(0), None, None, None
        after_hundred = after_english_ten = after_word_number = used_shorthand = False

    index = 0
    while index < len(tokens):
        kind, value = tokens[index]
        next_kind = tokens[index + 1][0] if index + 1 < len(tokens) else "other"
        index += 1

        if kind in ("literal", "number", "english_one", "english_ten"):
            is_word = kind != "literal"
            if prefix is not None:
                current, prefix = value + prefix, None
            elif current is None:
                current = value
            elif kind == "english_one" and after_english_ten:
                current += value  # "thirty" then "six"
            elif after_hundred and value < 100:
                current += value  # "पाँच सौ" then "पचास"
                after_hundred = False
            elif (
                is_word and after_word_number and not used_shorthand and not total
                and 10 <= value <= 99 and current.denominator == 1 and 1 <= current <= 99
            ):
                current = current * 100 + value  # "thirty six fifty" means 3,650
                used_shorthand = True
            else:
                flush()
                current = value
            after_english_ten = kind == "english_ten"
            after_word_number = is_word
        elif kind == "prefix":
            flush()
            prefix = value
        elif kind == "multiplier":
            if current is None:
                current = 1 + prefix if prefix is not None else Fraction(1)  # "सवा लाख", or a bare "हज़ार"
                prefix = None
            if value == 100:
                current *= 100
                after_hundred = True
            else:
                if largest_group is not None and value >= largest_group:
                    results.append(_as_number(total))  # a new number starts: "दो हज़ार, तीन हज़ार"
                    total = Fraction(0)
                total += current * value
                current, largest_group, after_hundred = None, value, False
            after_english_ten = after_word_number = False
        elif kind == "point" and current is not None:
            scale = Fraction(1, 10)
            while index < len(tokens) and tokens[index][0] in ("english_one", "number", "literal") and 0 <= tokens[index][1] <= 9:
                current += tokens[index][1] * scale
                scale /= 10
                index += 1
            after_english_ten = after_word_number = False
        elif kind == "and" and (current is not None or total) and next_kind in ("number", "english_one", "english_ten"):
            continue  # "five hundred and fifty"
        else:
            flush()
    flush()
    return results


def parse_amount_list(field: str) -> list[Number]:
    """Read a manifest field such as "2500|2550|2450" into numbers."""
    return [_as_number(Fraction(part)) for part in field.split("|") if part.strip()]


def match_amounts(reference: list[Number], found: list[Number]) -> list[bool]:
    """Say which reference mentions are matched by the numbers found, keeping order.

    Uses the longest common subsequence, so a transcript cannot match a mention twice
    and extra numbers in the transcript are ignored.
    """
    rows, columns = len(reference), len(found)
    table = [[0] * (columns + 1) for _ in range(rows + 1)]
    for i in range(rows - 1, -1, -1):
        for j in range(columns - 1, -1, -1):
            if reference[i] == found[j]:
                table[i][j] = table[i + 1][j + 1] + 1
            else:
                table[i][j] = max(table[i + 1][j], table[i][j + 1])
    matched = [False] * rows
    i = j = 0
    while i < rows and j < columns:
        if reference[i] == found[j]:
            matched[i] = True
            i, j = i + 1, j + 1
        elif table[i + 1][j] >= table[i][j + 1]:
            i += 1
        else:
            j += 1
    return matched


def score_transcript(reference: list[Number], transcript: str, lenient: bool = False) -> dict:
    """Score one transcript against the reference amounts of its clip.

    The strict score (lenient=False) is the primary one. The lenient score is reported
    beside it to show how much of the difference is spelling.
    """
    found = extract_numbers(transcript, lenient)
    matched = match_amounts(reference, found)
    return {
        "reference": reference,
        "found": found,
        "matched": matched,
        "matched_count": sum(matched),
        "reference_count": len(reference),
        "extra_numbers": len(found) - sum(matched),
    }


def exact_amount_match_rate(scores: list[dict]) -> float | None:
    """Matched amount mentions divided by all reference amount mentions."""
    total = sum(score["reference_count"] for score in scores)
    if total == 0:
        return None
    return sum(score["matched_count"] for score in scores) / total
