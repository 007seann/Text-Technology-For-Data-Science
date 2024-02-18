import nltk
import regex as re
import string
import spacy
import os
import sys
from pathlib import Path

util_dir = Path(os.path.join(os.path.dirname(__file__))).parent.joinpath('utils')
sys.path.append(str(util_dir))

from AppConfig import AppConfig
config = AppConfig()

STOPWORDS_PATH = config.get('indexer', 'stop_words', True)
class Tokeniser:
    """
    This class performs tokenisations of sentences.
    We provide these options:
        Keep certain punctuations within the sentence.
        Use stopping (i.e., remove English stop words such as 'and', 'or', and 'but')
    """

    def __init__(self, use_stopping=False, use_stemming=False, punctuations_to_keep=[]):
        """
        Initialise the Tokeniser class

        use_stopping: Boolean               If true, remove stop words.
        punctuations_to_keep: list[str]     List of punctuations to keep (i.e., do not split on these punctuations)
        """
        self.use_stopping = use_stopping
        self.use_stemming = use_stemming
        self.altered_punctuations = self._get_altered_punctuations(punctuations_to_keep)
        self.stop_words = self._get_stop_words()
        self.stemmer = nltk.PorterStemmer()
        self.ner = spacy.load('en_core_web_sm')
        self.pattern = "[\s" + self.altered_punctuations + "]"
        
    def _get_stop_words(self):
        if self.use_stopping:
            return self._read_stop_words()
        return set()

    def _read_stop_words(self):
        with open(STOPWORDS_PATH, 'r') as f:
            stop_words = set(f.read().split("\n"))
        return stop_words
    
    def _get_altered_punctuations(self, punctuations_to_keep):
        altered_punctuation = string.punctuation
        # Keep apostrophes in tokens:
        if punctuations_to_keep != []:
            for punct in punctuations_to_keep:
                altered_punctuation = string.punctuation.replace(punct, '')
        return altered_punctuation

    def tokenise(self, sentence):
        """
        Tokenises the given sentence according to the Tokeniser class' configurations
        
        sentence: str       Sentence to tokenise

        Return: list[str]   List of tokens that have been tokenised
        """
        # Split on punctuations and blank space (\s)
        tokens = re.split(self.pattern, sentence)

        # Lowercase tokens and remove any leftover punctuations
        tokens = [token.lower() for token in tokens if token and token not in self.altered_punctuations]

        # Remove stop words
        if self.use_stopping:
            tokens = [token for token in tokens if token not in self.stop_words]

        # Stem split tokens
        if self.use_stemming:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        return tokens
    
    def get_ner(self, sentence, is_headline=False):
        """
        This method retrieves the Named Entities according to spacy's 

        is_headline: Boolean    If true, treats the sentence as a headline. A headline has the format - "{SOURCE}  {DATE} / {HEADLINE}"

        Return:
            source: str | None                 News Source (E.g. CNBC, CNN, etc). None if sentence is not a headline.
            date: str | None                   News Date (Format - {dd/mm/YYYY}). None if sentence is not a headline.
            entities: list((str, str))         List of entities and their labels in the sentence (Format - [(Word, Label)...]).
        """
        if is_headline:
            split_preprocessed_text = sentence.split(" / ")
            source_date = split_preprocessed_text[0].split("  ")
            source = source_date[0]
            date = source_date[1].replace(" ", "/")
        entities = []
        for word in self.ner(sentence).ents:
            entities.append((word.text, word.label_))
        return source, date, entities