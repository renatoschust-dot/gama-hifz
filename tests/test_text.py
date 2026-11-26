"""The Qur'an text helpers are the part of hifz that must not be wrong.

`norm_ar` decides whether a recitation matches the verse ignoring diacritics, and
`lev_ratio` decides how close it is. Both are pure functions, so they are tested
without a database, a model or a network.
"""
from __future__ import annotations

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app  # noqa: E402


class Normalisation(unittest.TestCase):
    def test_diacritics_are_removed(self):
        with_marks = "بِسْمِ اللَّهِ"
        self.assertEqual(app.norm_ar(with_marks), app.norm_ar("بسم الله"))

    def test_alef_variants_match(self):
        for variant in ("أ", "إ", "آ"):
            self.assertEqual(app.norm_ar(variant), app.norm_ar("ا"), variant)

    def test_ta_marbuta_matches_ha(self):
        self.assertEqual(app.norm_ar("رحمة"), app.norm_ar("رحمه"))

    def test_tatweel_and_punctuation_do_not_count(self):
        self.assertEqual(app.norm_ar("اللـــه،"), app.norm_ar("الله"))

    def test_arabic_punctuation_is_stripped(self):
        for mark in ("،", "؛", "؟", "۝", "۞", "٪"):
            self.assertEqual(app.norm_ar("الله" + mark), "الله", mark)

    def test_empty_is_empty(self):
        self.assertEqual(app.norm_ar(""), "")
        self.assertEqual(app.norm_ar("   "), "")


class Similarity(unittest.TestCase):
    def test_identical_is_one(self):
        self.assertEqual(app.lev_ratio("الله", "الله"), 1.0)

    def test_empty_is_zero(self):
        self.assertEqual(app.lev_ratio("", "الله"), 0.0)

    def test_distance_is_symmetric_and_bounded(self):
        pairs = [("الله", "اللة"), ("بسم", "بسمل"), ("abc", "xyz")]
        for a, b in pairs:
            forward, backward = app.lev_ratio(a, b), app.lev_ratio(b, a)
            self.assertAlmostEqual(forward, backward, places=6)
            self.assertGreaterEqual(forward, 0.0)
            self.assertLessEqual(forward, 1.0)

    def test_one_substitution_is_below_one(self):
        self.assertLess(app.lev_ratio("بسم الله", "بسم اللة"), 1.0)
        self.assertGreater(app.lev_ratio("بسم الله", "بسم اللة"), 0.8)


class Words(unittest.TestCase):
    def test_words_are_split_after_normalisation(self):
        words = app.words_ar("بِسْمِ اللَّهِ الرَّحْمَٰنِ")
        self.assertEqual(len(words), 3)
        self.assertTrue(all(w for w in words))


if __name__ == "__main__":
    unittest.main()
