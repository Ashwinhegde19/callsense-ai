"""Tests for reading numbers from transcripts and scoring spoken amounts."""

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "amount_scoring.py"
SPEC = importlib.util.spec_from_file_location("amount_scoring", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
scoring = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scoring)


class ExtractNumbersTests(unittest.TestCase):
    def assert_numbers(self, text: str, expected: list) -> None:
        self.assertEqual(scoring.extract_numbers(text), expected, text)

    def test_digits(self) -> None:
        self.assert_numbers("आपकी किश्त 2,800 रुपये है", [2800])
        self.assert_numbers("refund 2800 rupees", [2800])
        self.assert_numbers("कीमत 1,25,000 रुपये है", [125000])
        self.assert_numbers("बिल २,८०० रुपये", [2800])
        self.assert_numbers("fee 99.50 rupees", [99.5])

    def test_digits_with_unit_words(self) -> None:
        self.assert_numbers("2.5 lakh rupees", [250000])
        self.assert_numbers("25 हज़ार रुपये", [25000])
        self.assert_numbers("2 हज़ार 5 सौ रुपये", [2500])

    def test_hindi_words(self) -> None:
        self.assert_numbers("दो हज़ार आठ सौ रुपये", [2800])
        self.assert_numbers("एक हज़ार चार सौ पचास रुपये", [1450])
        self.assert_numbers("एक लाख पच्चीस हज़ार रुपये", [125000])
        self.assert_numbers("पाँच लाख पचास हज़ार", [550000])
        self.assert_numbers("तीन करोड़ रुपये", [30000000])
        self.assert_numbers("निन्यानवे रुपये", [99])
        self.assert_numbers("सौ रुपये", [100])

    def test_hindi_spelling_variants(self) -> None:
        self.assert_numbers("दो हजार पांच सौ", [2500])
        self.assert_numbers("तीन हज़ार छः सौ पचास", [3650])
        self.assert_numbers("अट्ठारह", [18])

    def test_hindi_fraction_forms(self) -> None:
        self.assert_numbers("डेढ़ सौ रुपये", [150])
        self.assert_numbers("ढाई हज़ार रुपये", [2500])
        self.assert_numbers("ढाई लाख", [250000])
        self.assert_numbers("साढ़े तीन हज़ार", [3500])
        self.assert_numbers("साढ़े सात सौ", [750])
        self.assert_numbers("सवा लाख", [125000])
        self.assert_numbers("सवा दो लाख", [225000])
        self.assert_numbers("पौने दो सौ", [175])

    def test_hindi_hundreds_above_one_thousand(self) -> None:
        self.assert_numbers("चौबीस सौ पचास", [2450])
        self.assert_numbers("बारह सौ पचास", [1250])

    def test_english_words(self) -> None:
        self.assert_numbers("two thousand five hundred fifty rupees", [2550])
        self.assert_numbers("two thousand four hundred fifty", [2450])
        self.assert_numbers("five hundred and fifty", [550])
        self.assert_numbers("twelve hundred rupees", [1200])
        self.assert_numbers("ninety nine rupees", [99])
        self.assert_numbers("ninety-nine", [99])
        self.assert_numbers("two point five lakh rupees", [250000])
        self.assert_numbers("Fifteen rupees", [15])

    def test_english_shorthand(self) -> None:
        self.assert_numbers("thirty-six fifty", [3650])
        self.assert_numbers("thirty seven fifty", [3750])
        self.assert_numbers("छत्तीस पचास", [3650])

    def test_english_words_written_in_devanagari(self) -> None:
        self.assert_numbers("आपका बिल टू थाउजेंड फाइव हंड्रेड फिफ्टी रुपीस है", [2550])
        self.assert_numbers("मैंने ट्वेल्व हंड्रेड रुपीस ट्रांसफर किए", [1200])
        self.assert_numbers("कैशबैक नाइन्टी नाइन रुपीस मिलेगा", [99])
        self.assert_numbers("बिल थर्टी सिक्स फिफ्टी रुपीस हुआ था", [3650])
        self.assert_numbers("सैलरी टू पॉइंट फाइव लाख रुपीज़ है", [250000])
        self.assert_numbers("अमाउंट फिफ्टीन हंड्रेड नहीं सिक्सटीन हंड्रेड रुपीज़ है", [1500, 1600])
        self.assert_numbers("चार्ज फिफ्टीन रुपीज़ है", [15])
        self.assert_numbers("चार्ज फिफ्टी रुपीज़ है", [50])

    def test_ambiguous_devanagari_words_need_a_number_beside_them(self) -> None:
        self.assert_numbers("वन विभाग का दफ़्तर", [])
        self.assert_numbers("मुझे टू बी ऑनेस्ट नहीं पता", [])
        self.assert_numbers("टू हंड्रेड रुपीज़", [200])
        self.assert_numbers("फोर थाउजेंड", [4000])

    def test_fraction_word_before_digits(self) -> None:
        self.assert_numbers("पौने 200 रुपये बचे हैं", [175])
        self.assert_numbers("साढ़े 3000 रुपये", [3500])
        self.assert_numbers("सवा 200", [225])
        self.assert_numbers("साढ़े 3 हज़ार", [3500])

    def test_romanized_hindi(self) -> None:
        self.assert_numbers("bara hazar panch so", [12500])
        self.assert_numbers("dhai hazaar", [2500])
        self.assert_numbers("Aapka bill ek hazar chaar so pachaas rupaye aaya hai", [1450])
        self.assert_numbers("refund do hazar paanch so pachaas rupaye hai, sorry, do hazar chaar so pachaas rupaye hai", [2550, 2450])
        self.assert_numbers("gadi ki keemat ek lakh pachis hazaar rupe hai", [125000])
        self.assert_numbers("turnover teen karor rupe hai", [30000000])
        self.assert_numbers("account mein das lakh rupaye hain", [1000000])
        self.assert_numbers("ninyanve rupaye", [99])
        self.assert_numbers("sau rupaye", [100])

    def test_romanized_hindi_spelling_variants(self) -> None:
        self.assert_numbers("baarah hazaar paanch sau", [12500])
        self.assert_numbers("barah hajar", [12000])
        self.assert_numbers("BARA HAZAR", [12000])
        for spelling in ("pachis", "pachees", "pachchis", "pacchis", "pachhis"):
            self.assert_numbers(f"{spelling} hazar", [25000])
        self.assert_numbers("bawan hazar", [52000])
        self.assert_numbers("chhattees hazar", [36000])

    def test_romanized_hindi_fraction_forms(self) -> None:
        self.assert_numbers("dedh sau rupaye", [150])
        self.assert_numbers("dhaai lakh", [250000])
        self.assert_numbers("sadhe teen hazar", [3500])
        self.assert_numbers("sawa do lakh", [225000])
        self.assert_numbers("paune do sau", [175])
        self.assert_numbers("sadhe 3 hazar", [3500])

    def test_romanized_hindi_shorthand(self) -> None:
        self.assert_numbers("chaar pachis rupe kata", [425])

    def test_romanized_look_alike_amounts_stay_distinct(self) -> None:
        for text, expected in [
            ("saat rupaye", [7]), ("saath rupaye", [60]), ("satrah rupaye", [17]), ("sattar rupaye", [70]),
            ("pachis rupaye", [25]), ("pachas rupaye", [50]), ("untalis rupaye", [39]), ("unchas rupaye", [49]),
            ("tees rupaye", [30]), ("teis rupaye", [23]), ("bees rupaye", [20]), ("bais rupaye", [22]),
        ]:
            self.assert_numbers(text, expected)
            self.assertEqual(scoring.extract_numbers(text, lenient=True), expected, text)

    def test_ordinary_english_words_are_not_numbers(self) -> None:
        for text in [
            "please do so",
            "so do I",
            "I do not know what to do",
            "so what should we do now",
            "a teen sat at the bar",
            "the bees char the tin",
            "he sat down and had tees printed",
            "no, that is not right",
        ]:
            self.assert_numbers(text, [])
            self.assertEqual(scoring.extract_numbers(text, lenient=True), [], text)

    def test_english_words_beside_real_numbers_are_left_out(self) -> None:
        self.assert_numbers("I do not have 2000 rupees", [2000])
        self.assert_numbers("do 20 pushups", [20])
        self.assert_numbers("we sat for 3 hours", [3])
        self.assert_numbers("so 500 rupees it is", [500])
        self.assert_numbers("so ek hazar rupaye lagenge", [1000])
        self.assert_numbers("ek hazar, so I left", [1000])

    def test_ordinary_hindi_words_are_not_numbers(self) -> None:
        self.assert_numbers("bara ghar hai", [])
        self.assert_numbers("tera bill 500 rupaye hai", [500])
        self.assert_numbers("GST ke saath total ek hazar ek so assi rupaye", [1180])
        self.assert_numbers("do teen din mein aayega", [])

    def test_ambiguous_romanized_words_count_with_support(self) -> None:
        self.assert_numbers("do hazar", [2000])
        self.assert_numbers("do lakh", [200000])
        self.assert_numbers("do rupaye", [2])
        self.assert_numbers("teen so bees rupe", [320])
        self.assert_numbers("bara rupaye", [12])

    def test_romanized_do_meaning_give(self) -> None:
        self.assert_numbers("mujhe paanch so do", [500])
        self.assert_numbers("paanch so rupaye de do", [500])
        self.assert_numbers("ek hazar do rupaye", [1002])

    def test_several_numbers(self) -> None:
        self.assert_numbers("refund 2,550 रुपये है, sorry, 2,450 रुपये है", [2550, 2450])
        self.assert_numbers("पचास रुपये, पच्चीस नहीं", [50, 25])
        self.assert_numbers("fifteen hundred नहीं, sixteen hundred rupees", [1500, 1600])
        self.assert_numbers("ten, twenty", [10, 20])
        self.assert_numbers("10 20", [10, 20])

    def test_numbers_that_are_not_money_are_also_returned(self) -> None:
        self.assert_numbers("किश्त 2,800 रुपये है, जो हर महीने 10 तारीख को कटेगी", [2800, 10])

    def test_text_without_numbers(self) -> None:
        self.assert_numbers("get mail आइकन पर क्लिक करें", [])
        self.assert_numbers("", [])


class LenientReadingTests(unittest.TestCase):
    def assert_readings(self, text: str, strict: list, lenient: list) -> None:
        self.assertEqual(scoring.extract_numbers(text), strict, f"strict: {text}")
        self.assertEqual(scoring.extract_numbers(text, lenient=True), lenient, f"lenient: {text}")

    def test_misspelled_number_words(self) -> None:
        self.assert_readings("देर सो रुपै", [], [150])
        self.assert_readings("10 लाक रूपे", [10], [1000000])
        self.assert_readings("तीन करोर रुपे", [3], [30000000])

    def test_run_together_words(self) -> None:
        self.assert_readings("चारसो रुपे", [], [400])
        self.assert_readings("सारे साथसो रुपे", [], [750])
        self.assert_readings("दाईलाक रुपे", [], [250000])
        self.assert_readings("एक्हजार नोसो निन्यान्वे रुपे", [], [1999])
        self.assert_readings("पचास्रुपे, पचीस नहीं", [25], [50, 25])

    def test_number_word_written_as_two_words(self) -> None:
        self.assert_readings("उन तालीस रुपे", [], [39])
        self.assert_readings("उन्चा स्रुपे", [], [49])

    def test_loosely_spelled_romanized_hindi(self) -> None:
        self.assert_readings("saade saat so rupaye", [700], [750])
        self.assert_readings("pone do so rupee", [200], [175])
        self.assert_readings("charso rupe", [], [400])
        self.assert_readings("do hazar charso pachas", [2000, 50], [2450])
        self.assert_readings("un talis rupe", [], [39])
        self.assert_readings("pachasrupe", [], [50])

    def test_lenient_romanized_reading_leaves_ordinary_words_alone(self) -> None:
        # "no" sounds like nau (9) and "dobara" (again) looks like "do bara".
        self.assert_readings("ek hazar no do hazar", [1000, 2000], [1000, 2000])
        self.assert_readings("ek hazar dobara bhejo", [1000], [1000])
        self.assert_readings("dobara ek hazar rupaye bhejo", [1000], [1000])

    def test_romanized_dropped_words_are_not_repaired(self) -> None:
        # "patas" is not "pachas", so neither reading may report 1,450.
        self.assertNotIn(1450, scoring.extract_numbers("ek hazar chaar so patas rupaye", lenient=True))

    def test_no_two_romanized_numbers_share_a_key(self) -> None:
        for key_of in (scoring._roman_key, lambda word: scoring._roman_fold(scoring._roman_key(word))):
            values_by_key: dict[str, set] = {}
            for word, kind, value in scoring._roman_spellings():
                values_by_key.setdefault(key_of(word), set()).add((kind, value))
            self.assertGreater(len(values_by_key), 150)
            clashes = {key: values for key, values in values_by_key.items() if len(values) > 1}
            self.assertEqual(clashes, {})

    def test_correct_spelling_reads_the_same_in_both(self) -> None:
        for text, expected in [
            ("bara hazar panch so", [12500]),
            ("dhai hazaar", [2500]),
            ("दो हज़ार आठ सौ रुपये", [2800]),
            ("साढ़े तीन हज़ार", [3500]),
            ("refund 2,550 रुपये है, sorry, 2,450 रुपये है", [2550, 2450]),
            ("thirty-six fifty", [3650]),
        ]:
            self.assert_readings(text, expected, expected)

    def test_dropped_words_are_not_repaired(self) -> None:
        # "four hundred" is missing, so neither reading may report 1,450.
        self.assertNotIn(1450, scoring.extract_numbers("एक हजार सो पतास रुपे", lenient=True))
        # A different consonant is a different word: पाथ is not accepted as पाँच.
        self.assertNotIn(2550, scoring.extract_numbers("दो हजार पाथ सो पचास", lenient=True))

    def test_look_alike_amounts_stay_distinct(self) -> None:
        for text, expected in [("पच्चीस", [25]), ("पचीस", [25]), ("पचास", [50]), ("उनतालीस", [39]), ("उनचास", [49]), ("सात", [7]), ("साठ", [60]), ("सत्रह", [17]), ("सत्तर", [70])]:
            self.assertEqual(scoring.extract_numbers(text, lenient=True), expected, text)

    def test_no_two_numbers_share_a_sound_key(self) -> None:
        values_by_key: dict[str, set] = {}
        for word in scoring._HINDI_NUMBER_WORDS:
            values_by_key.setdefault(scoring._fold(word), set()).add(scoring._LEXICON[word])
        self.assertGreater(len(values_by_key), 100)
        clashes = {key: values for key, values in values_by_key.items() if len(values) > 1}
        self.assertEqual(clashes, {})

    def test_lenient_reading_can_add_spurious_numbers(self) -> None:
        # Documented cost: ordinary words that sound like number words are read as numbers.
        self.assert_readings("GST के साथ total 1,180 रुपये", [1180], [7, 1180])


class MatchAmountsTests(unittest.TestCase):
    def test_refund_example_from_problem_statement(self) -> None:
        reference = [2500, 2550, 2450, 2450, 2450]
        found = [2500, 2450, 2450, 2450, 2450]
        matched = scoring.match_amounts(reference, found)
        self.assertEqual(matched, [True, False, True, True, True])
        self.assertEqual(sum(matched) / len(reference), 0.8)

    def test_extra_numbers_are_ignored(self) -> None:
        self.assertEqual(scoring.match_amounts([2800], [2800, 10]), [True])

    def test_missing_amount_is_a_mismatch(self) -> None:
        self.assertEqual(scoring.match_amounts([850, 320, 100], [850, 100]), [True, False, True])

    def test_order_matters(self) -> None:
        self.assertEqual(sum(scoring.match_amounts([50, 25], [25, 50])), 1)

    def test_one_found_number_cannot_match_two_mentions(self) -> None:
        self.assertEqual(sum(scoring.match_amounts([2450, 2450], [2450])), 1)

    def test_no_numbers_found(self) -> None:
        self.assertEqual(scoring.match_amounts([2500], []), [False])


class ScoreTests(unittest.TestCase):
    def test_parse_amount_list(self) -> None:
        self.assertEqual(scoring.parse_amount_list("2500|2550|2450"), [2500, 2550, 2450])
        self.assertEqual(scoring.parse_amount_list("99.5"), [99.5])
        self.assertEqual(scoring.parse_amount_list(""), [])

    def test_score_transcript(self) -> None:
        score = scoring.score_transcript([2550, 2450], "आपका refund 2,450 रुपये है, sorry, 2,450 रुपये है")
        self.assertEqual(score["found"], [2450, 2450])
        self.assertEqual(score["matched"], [False, True])
        self.assertEqual(score["extra_numbers"], 1)

    def test_strict_and_lenient_scores(self) -> None:
        transcript = "आपके खाते में सारे साथसो रुपे जमा होगे है"
        self.assertEqual(scoring.score_transcript([750], transcript)["matched_count"], 0)
        self.assertEqual(scoring.score_transcript([750], transcript, lenient=True)["matched_count"], 1)

    def test_exact_amount_match_rate(self) -> None:
        scores = [
            scoring.score_transcript([2800], "किश्त 2800 रुपये है"),
            scoring.score_transcript([50, 25], "पचास रुपये, पचास नहीं"),
        ]
        self.assertAlmostEqual(scoring.exact_amount_match_rate(scores), 2 / 3)

    def test_rate_is_none_without_reference_amounts(self) -> None:
        self.assertIsNone(scoring.exact_amount_match_rate([scoring.score_transcript([], "कोई रकम नहीं")]))


if __name__ == "__main__":
    unittest.main()
