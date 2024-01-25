import nltk
import regex as re
import string

class Tokeniser:
    """
    This class performs tokenisations of sentences.
    We provide options to keep apostrophes
    """

    def __init__(self, use_stopping=True, punctuations_to_keep=[]):
        """
        Initialise the Tokeniser class

        use_stopping: Boolean           If true, remove stop words.
        punctuations_to_keep: list[str]    List of punctuations to keep (i.e., do not split on these punctuations)
        """
        self.use_stopping = use_stopping
        self.punctuations_to_keep = punctuations_to_keep
        if self.use_stopping:
            self.stop_words = self._read_stop_words()
        self.stemmer = nltk.PorterStemmer()

    def _read_stop_words(self):
        with open('ttds_2023_english_stop_words.txt.txt', 'r') as f:
            stop_words = set(f.read().split("\n"))
        return stop_words

    def tokenize(self, sentence):
        altered_punctuation = string.punctuation
        # Keep apostrophes in tokens:
        if self.punctuations_to_keep != []:
            for punct in self.punctuations_to_keep:
                altered_punctuation = string.punctuation.replace(punct, '')
        
        # Split on punctuations and blank space (\s)
        tokens = re.split("[\s" + altered_punctuation + "]", sentence)

        # Lowercase tokens
        tokens = [token.lower() for token in tokens]
        
        # Remove any leftover punctuations
        tokens = [token.translate(str.maketrans('', '', string.punctuation)) for token in tokens]
        
        # Remove stop words
        if self.use_stopping:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        # Stem split tokens
        tokens = [self.stemmer.stem(token) for token in tokens]

        # Remove any blank spaces
        tokens = [token for token in tokens if token != '']
        return tokens