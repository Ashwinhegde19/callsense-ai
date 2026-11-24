"""Read numbers out of a transcript and score spoken monetary amounts.

The scoring follows docs/problem.md: every reference amount mention counts, and a
mention is matched only when the transcript contains exactly the same numeric value.

Numbers are recognised when written as digits, as Hindi number words in Devanagari or
in Latin letters ("dhai hazaar"), or as English number words in Latin or Devanagari.

Two readings are available. The strict reading accepts only correctly spelled number
words; for Hindi in Latin letters, which has no standard spelling, it accepts a fixed
list of usual spellings. The lenient reading also accepts common misspellings of Hindi
number words.
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

# English number words as they are written in Devanagari: टू थाउजेंड फाइव हंड्रेड.
_DEVANAGARI_ENGLISH_ONES = {0: "ज़ीरो", 3: "थ्री", 5: "फाइव", 6: "सिक्स", 7: "सेवन", 9: "नाइन"}
_DEVANAGARI_ENGLISH_TEENS = {
    11: "इलेवन", 12: "ट्वेल्व", 13: "थर्टीन", 14: "फोर्टीन", 15: "फिफ्टीन", 16: "सिक्सटीन",
    17: "सेवनटीन सेवेंटीन", 18: "एटीन", 19: "नाइनटीन नाइंटीन",
}
_DEVANAGARI_ENGLISH_TENS = {
    20: "ट्वेंटी ट्वेन्टी", 30: "थर्टी", 40: "फोर्टी", 50: "फिफ्टी", 60: "सिक्सटी",
    70: "सेवंटी सेवेंटी सेवन्टी", 80: "एटी", 90: "नाइंटी नाइन्टी",
}
_DEVANAGARI_ENGLISH_MULTIPLIERS = {
    100: "हंड्रेड हन्ड्रेड", 1_000: "थाउजेंड थाउजंड थाउसेंड थाउसंड", 1_000_000: "मिलियन", 1_000_000_000: "बिलियन",
}
_DEVANAGARI_ENGLISH_POINT = "पॉइंट पॉइन्ट पाइंट प्वाइंट"
# These are also ordinary words (वन is "forest", टू is "to", एट is "at"), so they are
# read as numbers only when the word next to them is a number.
_DEVANAGARI_ENGLISH_AMBIGUOUS = {1: "वन", 2: "टू", 4: "फोर", 8: "एट", 10: "टेन"}

# Hindi number words written in Latin letters: "bara hazar panch so" is 12,500.
# Romanised Hindi has no standard spelling, so each number lists its usual spellings.
# Words are compared through _roman_key, which ignores routine differences: "aa" for
# "a", "ee" for "i", doubled consonants, "w" for "v", and a dropped final "h".
_ROMAN_HINDI_UNITS = {
    0: "shunya", 1: "ek", 2: "do", 3: "teen", 4: "char", 5: "panch", 6: "chhah chhe", 7: "saat", 8: "aath",
    9: "nau", 10: "das dus", 11: "gyarah", 12: "barah", 13: "terah", 14: "chaudah", 15: "pandrah pandhrah",
    16: "solah", 17: "satrah", 18: "atharah", 19: "unnis", 20: "bees", 21: "ikkis ekkis", 22: "bais",
    23: "teis tais", 24: "chaubis", 25: "pachis pachchis", 26: "chhabbis", 27: "sattais", 28: "atthais",
    29: "untis unatis", 30: "tees", 31: "ikattis iktis", 32: "battis", 33: "taintis tentis taitis",
    34: "chauntis chautis", 35: "paintis pentis paitis", 36: "chhattis", 37: "saintis sentis saitis",
    38: "adtis artis adatis aratis", 39: "untalis unatalis unchalis", 40: "chalis",
    41: "iktalis ikatalis ektalis", 42: "bayalis byalis", 43: "taintalis tentalis taitalis",
    44: "chavalis chauvalis", 45: "paintalis pentalis paitalis", 46: "chhiyalis chhyalis",
    47: "saintalis sentalis saitalis", 48: "adtalis artalis adatalis aratalis", 49: "unchas unanchas",
    50: "pachas", 51: "ikyavan ekyavan", 52: "bavan", 53: "tirpan tirepan tirapan", 54: "chauvan chauan",
    55: "pachpan pachapan", 56: "chhappan", 57: "sattavan", 58: "atthavan", 59: "unsath unasath",
    60: "saath", 61: "iksath ikasath eksath", 62: "basath", 63: "tirsath tiresath tirasath",
    64: "chaunsath chausath", 65: "painsath pensath paisath", 66: "chhiyasath chhyasath",
    67: "sadsath sarsath sadasath sarasath", 68: "adsath arsath adasath arasath", 69: "unhattar unahattar",
    70: "sattar", 71: "ikhattar ikahattar ekhattar", 72: "bahattar", 73: "tihattar", 74: "chauhattar",
    75: "pachhattar pachahattar", 76: "chhihattar", 77: "satahattar sathattar", 78: "athahattar athhattar",
    79: "unasi unyasi", 80: "assi", 81: "ikyasi ekyasi", 82: "bayasi byasi", 83: "tirasi", 84: "chaurasi",
    85: "pachasi", 86: "chhiyasi chhyasi", 87: "sattasi", 88: "atthasi", 89: "navasi", 90: "nabbe nabbey",
    91: "ikyanve ikyanave ikyanbe", 92: "banve banave banbe", 93: "tiranve tiranave tiranbe",
    94: "chauranve chauranave chauranbe", 95: "pachanve pachanave pachanbe panchanve panchanave panchanbe",
    96: "chhiyanve chhiyanave chhiyanbe", 97: "sattanve sattanave sattanbe",
    98: "atthanve atthanave atthanbe", 99: "ninyanve ninyanave ninyanbe",
}
_ROMAN_HINDI_MULTIPLIERS = {100: "sau so", 1_000: "hazar hajar", 100_000: "lakh", 10_000_000: "karod karor"}
_ROMAN_HINDI_FRACTION_NUMBERS = {Fraction(3, 2): "dedh derh", Fraction(5, 2): "dhai adhai"}
_ROMAN_HINDI_FRACTION_PREFIXES = {Fraction(1, 2): "sadhe sarhe", Fraction(1, 4): "sava", Fraction(-1, 4): "paune pauney"}
# These are also ordinary English or Hindi words ("do", "so", "teen", "bees"; "bara" is
# "big", "tera" is "your", "saath" is "with"). They are read as numbers only when the
# same run of number words holds an unambiguous Hindi number word, or lakh or crore, or
# when a rupee word follows the run. "so" must also come straight after a number.
_ROMAN_HINDI_AMBIGUOUS = "do teen char chhah chhe saat bees tees barah terah chaudah saath so"
# "do" is also "give". At the end of a run it is 2 only when a rupee word follows.
_ROMAN_HINDI_GIVE = "do"
# Never read as a number, even leniently: "no" would otherwise sound like nau (9).
_ROMAN_HINDI_NEVER = "no"
_ROMAN_CURRENCY_WORDS = "rupee rupees rupaye rupay rupe rupaya rupiya rupiye rupaiye rupye rs"
_ROMAN_ANCHOR_WORDS = {"lakh", "lakhs", "lac", "lacs", "crore", "crores"}

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
    for kind, table in (
        ("english_one", _DEVANAGARI_ENGLISH_ONES),
        ("number", _DEVANAGARI_ENGLISH_TEENS),
        ("english_ten", _DEVANAGARI_ENGLISH_TENS),
        ("multiplier", _DEVANAGARI_ENGLISH_MULTIPLIERS),
        ("maybe_english_one", _DEVANAGARI_ENGLISH_AMBIGUOUS),
    ):
        for value, spellings in table.items():
            for spelling in spellings.split():
                lexicon[_normalize(spelling)] = (kind, Fraction(value))
    for spelling in _DEVANAGARI_ENGLISH_POINT.split():
        lexicon[_normalize(spelling)] = ("point", Fraction(0))
    return lexicon


_LEXICON = _build_lexicon()
_HINDI_NUMBER_WORDS = {
    _normalize(spelling)
    for spellings in (*_HINDI_UNITS.values(), " ".join(_FRACTION_NUMBERS), " ".join(_FRACTION_PREFIXES), "सौ हज़ार लाख करोड़ अरब")
    for spelling in spellings.split()
}
_NUMBER_KINDS = ("literal", "number", "english_one", "english_ten", "multiplier", "point", "maybe_english_one")


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


_FOLDED = {_fold(word): _LEXICON[word] for word in _HINDI_NUMBER_WORDS}
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


# Romanised Hindi. A token carries a mark: "anchor" for an unambiguous Hindi number
# word, "maybe" for one that needs support from its neighbours, "give" for "do", and
# "currency" for a rupee word.
Token = tuple[str, Fraction, str]
_PLAIN: Token = ("other", Fraction(0), "")
_CURRENCY: Token = ("other", Fraction(0), "currency")


def _roman_key(word: str) -> str:
    """Remove spelling differences that are only transliteration habits."""
    word = word.replace("w", "v").replace("ee", "i").replace("oo", "u")
    word = re.sub(r"(.)\1+", r"\1", word).replace("chch", "ch")
    if len(word) > 2 and word[-1] == "h" and word[-2] in "aeiou":
        word = word[:-1]
    return word


def _roman_fold(key: str) -> str:
    """Reduce a key to a rough sound, for the lenient reading: "saade" for "sadhe"."""
    for written, sound in (("kh", "k"), ("gh", "g"), ("jh", "j"), ("dh", "d"), ("bh", "b"), ("ph", "p"), ("sh", "s"), ("au", "o"), ("ou", "o"), ("z", "j")):
        key = key.replace(written, sound)
    return re.sub(r"(.)\1+", r"\1", key)  # "th" is kept: it separates saat (7) from saath (60)


def _roman_spellings() -> list[tuple[str, str, Fraction]]:
    spellings = []
    for kind, table in (
        ("number", {Fraction(value): words for value, words in _ROMAN_HINDI_UNITS.items()}),
        ("multiplier", {Fraction(value): words for value, words in _ROMAN_HINDI_MULTIPLIERS.items()}),
        ("number", _ROMAN_HINDI_FRACTION_NUMBERS),
        ("prefix", _ROMAN_HINDI_FRACTION_PREFIXES),
    ):
        for value, words in table.items():
            spellings.extend((word, kind, value) for word in words.split())
    return spellings


def _build_roman() -> tuple[dict[str, Token], dict[str, tuple[str, Fraction]]]:
    ambiguous = {_roman_key(word) for word in _ROMAN_HINDI_AMBIGUOUS.split()}
    exact: dict[str, Token] = {}
    folded: dict[str, tuple[str, Fraction]] = {}
    for word, kind, value in _roman_spellings():
        key = _roman_key(word)
        mark = "give" if key == _ROMAN_HINDI_GIVE else "maybe" if key in ambiguous else "anchor"
        exact[key] = (kind, value, mark)
        folded[_roman_fold(key)] = (kind, value)
    folded.pop(_ROMAN_HINDI_NEVER, None)
    return exact, folded


_ROMAN, _ROMAN_FOLDED = _build_roman()
_ROMAN_CURRENCY = {_roman_key(word) for word in _ROMAN_CURRENCY_WORDS.split()}
_ROMAN_CURRENCY_FOLDED = {_roman_fold(key) for key in _ROMAN_CURRENCY}


def _split_roman(folded: str, first: bool = True, parts_left: int = 4) -> list[Token] | None:
    """Read a loosely spelled or run-together word such as "charso" (char so).

    Inside a run-together word a part needs three letters, apart from "so" after a
    number. This keeps "dobara" (again) from being read as "do bara".
    """
    if not folded:
        return []
    if folded in _ROMAN_CURRENCY_FOLDED:
        return [_CURRENCY]
    if parts_left == 0:
        return None
    for end in range(len(folded), 1, -1):
        part = folded[:end]
        entry = _ROMAN_FOLDED.get(part)
        if entry is None:
            continue
        whole_word = first and end == len(folded)
        if len(part) < 3 and not whole_word and (first or part != "so"):
            continue
        rest = _split_roman(folded[end:], False, parts_left - 1)
        if rest is not None:
            return [(*entry, "maybe"), *rest]
    return None


def _read_roman(word: str, lenient: bool) -> list[Token]:
    key = _roman_key(word)
    if key in _ROMAN_CURRENCY:
        return [_CURRENCY]
    if key in _ROMAN:
        return [_ROMAN[key]]
    if not lenient:
        return []
    return _split_roman(_roman_fold(key)) or []


_RUN_KINDS = ("literal", "number", "english_one", "english_ten", "multiplier", "prefix", "maybe_english_one")
_PLAIN_NUMBER_KINDS = ("literal", "number", "english_one", "english_ten")


def _resolve_roman(tokens: list[Token]) -> list[tuple[str, Fraction]]:
    """Decide which ambiguous romanised words are numbers, one run of number words at a time."""
    resolved = [(kind, value) for kind, value, _ in tokens]
    start = 0
    while start < len(tokens):
        if tokens[start][0] not in _RUN_KINDS:
            start += 1
            continue
        end = start
        while end < len(tokens) and tokens[end][0] in _RUN_KINDS:
            end += 1
        rupee_word_follows = end < len(tokens) and tokens[end][2] == "currency"
        supported = rupee_word_follows or any(mark == "anchor" for _, _, mark in tokens[start:end])
        for position in range(start, end):
            kind, _, mark = tokens[position]
            if mark not in ("maybe", "give"):
                continue
            keep = supported
            if keep and kind == "multiplier":  # "so" is 100 only straight after a number
                keep = position > start and resolved[position - 1][0] in _PLAIN_NUMBER_KINDS
            if keep and mark == "give":  # a final "do" is usually "give"
                keep = position + 1 < end or rupee_word_follows
            if not keep:
                resolved[position] = _OTHER
        start = end
    return resolved


def _tokenize(text: str, lenient: bool = False) -> list[tuple[str, Fraction]]:
    raws = _TOKEN.findall(_normalize(text))
    marked: list[Token] = []
    index = 0
    while index < len(raws):
        raw = raws[index]
        index += 1
        if raw[0].isdigit():
            marked.append(("literal", Fraction(raw.replace(",", "")), ""))
            continue
        entry = _LEXICON.get(raw)
        following = raws[index] if index < len(raws) else ""
        if entry is not None:
            marked.append((*entry, "anchor" if raw in _ROMAN_ANCHOR_WORDS else ""))
        elif raw[0].isascii() and raw[0].isalpha():
            parts = _read_roman(raw, lenient)
            if not parts and lenient and following.isascii() and following.isalpha() and following not in _LEXICON and not _read_roman(following, lenient):
                joined = _split_roman(_roman_fold(_roman_key(raw + following)))  # a number word written as two: un talis
                if joined:
                    parts = [(kind, value, mark or "maybe") for kind, value, mark in joined]
                    index += 1
            marked.extend(parts or [_PLAIN])
        elif lenient and _is_devanagari_word(raw):
            parts = _read_tolerantly(raw)
            if not parts and following and _is_devanagari_word(following) and following not in _LEXICON:
                parts = _read_tolerantly(raw + following)  # a number word written as two: उन तालीस
                if parts:
                    index += 1
            marked.extend((kind, value, "") for kind, value in (parts or [_OTHER]))
        else:
            marked.append(_PLAIN)
    tokens = _resolve_roman(marked)
    # A word such as टू counts as a number only beside another number: टू थाउजेंड.
    resolved = []
    for position, (kind, value) in enumerate(tokens):
        if kind == "maybe_english_one":
            before = tokens[position - 1][0] if position else "other"
            after = tokens[position + 1][0] if position + 1 < len(tokens) else "other"
            is_number = before in _NUMBER_KINDS or after in _NUMBER_KINDS
            kind = ("number" if value >= 10 else "english_one") if is_number else "other"
        resolved.append((kind, value))
    return resolved


def _apply_prefix_to_digits(value: Fraction, prefix: Fraction) -> Fraction:
    """Read "पौने 200" as 175: the fraction belongs to the leading unit of a round number."""
    if value.denominator == 1 and value >= 100:
        for unit in (10_000_000, 100_000, 1_000, 100):
            if value % unit == 0:
                return (value / unit + prefix) * unit
    return value + prefix


def _as_number(value: Fraction) -> Number:
    return int(value) if value.denominator == 1 else float(value)


def extract_numbers(text: str, lenient: bool = False) -> list[Number]:
    """Return every number written or spelled out in the text, in order.

    All numbers are returned, including ones that are not money, such as dates.

    With lenient=True, Hindi number words are also recognised when misspelled in ways
    that keep roughly the same sound, when run together, or when split in two. This
    reads more real amounts but also turns some ordinary words into numbers, for
    example साथ ("with") into 7. It never changes how correctly spelled text is read.

    Hindi in Latin letters is read in both modes from a fixed list of usual spellings.
    Words that are also ordinary words, such as "do" and "so", count only when the
    words around them show a number is being said.
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
                current = value + prefix if is_word else _apply_prefix_to_digits(value, prefix)
                prefix = None
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
