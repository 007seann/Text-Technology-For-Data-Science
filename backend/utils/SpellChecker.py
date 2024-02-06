from re import S
import spacy
# Too many dependencies. Took too much space. Slow too. 
#import contextualSpellCheck
from autocorrect import Speller

class SpellChecker:
    def __init__(self, language_model='en_core_web_sm', use_secondary=True):
        self.use_secondary = use_secondary
        if not self.use_secondary:
            self.nlp = spacy.load(language_model, disable=["tagger", "ner"])
            #contextualSpellCheck.add_to_pipe(self.nlp)
        else:
            self.secondary = Speller()

    def suggest_corrections_fst(self, token):
        # This is just a placeholder. Probably edit distance. May be faster.
        return ["suggestion1", "suggestion2"]

    def check_and_correct(self, text):
        if not self.use_secondary:
            return self.check_and_correct_spacy(text)
        else:
            return self.secondary(text)

    def check_and_correct_spacy(self, text):
        doc = self.nlp(text)
        corrections_dict = doc._.suggestions_spellCheck
        corrections = list(corrections_dict.items())
        corrected_text = doc._.outcome_spellCheck
        correction_made = len(corrections) > 0
        return corrected_text, corrections, correction_made
    
    
if __name__ == '__main__':
    spell_checker = SpellChecker()
    text = "In an atempt to write a longer paragraf, multiple speling mistaks are intentionally added to this text to see how the spel checker behaves."
    corrected_text, corrections, correction_made = spell_checker.check_and_correct(text)
    print(corrected_text)
    print(corrections)
    print(correction_made)