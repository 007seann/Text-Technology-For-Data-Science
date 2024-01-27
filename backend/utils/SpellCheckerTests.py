import unittest
from SpellChecker import SpellChecker
import time

# Reqs:
# pip install spacy
# pip install contextualSpellCheck

class TestSpellChecker(unittest.TestCase):
    def setUp(self):
        self.spell_checker = SpellChecker()

    def test_correction_performance(self):
        test_cases = [
            "Speling errrs in sentnce.",
            "This is a test sentense with som spelling erors.",
            "In an atempt to write a longer paragraf, multiple speling mistaks are intentionally added to this text to see how the spel checker behaves."
        ]

        for text in test_cases:
            start_time = time.time()
            corrected_text, corrections, correction_made = self.spell_checker.check_and_correct(text)
            end_time = time.time()
            print("--------------------------------------------------")
            print(f"Test text: \"{text}\"")
            print(f"Test text length: {len(text.split())}")
            print(f"Number of corrections: {len(corrections)}")
            print(f"Time taken for correction: {end_time - start_time} seconds\n")

if __name__ == '__main__':
    unittest.main()
