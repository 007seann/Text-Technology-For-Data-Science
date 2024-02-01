import numpy as np
from Tokeniser import Tokeniser
import math

class VectorSpaceModel:

    def __init__(self, documents, mode='tfidf'):
        self.mode = mode
        self.tokeniser = Tokeniser()
        self.tokenised_documents = [self.tokeniser.tokenise(document) for document in documents]
        self.N = len(self.tokenised_documents)
        self.L_bar = sum([len(document) for document in self.tokenised_documents]) / self.N
        self.vocab = self.make_vocab()

        # TODO Turn into lists to save space
        # Inverted Index of the form {token: {doc_id: count}}
        self.count_matrix = self.make_count_matrix()

        # Score Matrix of the form {doc_id: {token: score}}
        self.score_matrix = self.make_score_matrix()

    def make_vocab(self):
        """
        Returns the vocabulary of the documents.
        :param documents: The documents.
        :return: The vocabulary of the documents.
        """
        vocab = set()
        for tokenised_document in self.tokenised_documents:
            vocab.update(tokenised_document)
        vocab = list(vocab)
        vocab.sort()
        return vocab
    
    def make_count_matrix(self):
        """
        Returns the count matrix of the documents.
        :param documents: The documents.
        :return: The count matrix of the documents.
        Count Matrix = {token: {doc_id: count}}
        """
        vocab = self.vocab
        count_matrix = {}
        for token in vocab:
            count_matrix[token] = {}
            for i, tokenised_document in enumerate(self.tokenised_documents):
                count_matrix[token][i] = tokenised_document.count(token)
        return count_matrix
    
    def calculate_tf(self, token, doc_id, mode):
        """
        Returns the term frequency of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param mode: The mode of calculation.
        :return: The term frequency of a token in a document.
        """
        term_freqs = self.count_matrix[token].values()
        term_freq = self.count_matrix[token][doc_id]
        if term_freq == 0:
            return 0
        case = {
            'n': lambda x: x,
            'l': lambda x: 1 + math.log10(x),
            'a': lambda x: 0.5 + (0.5 * (x / max(term_freqs)))
        }
        return case[mode](term_freq)

    def calculate_idf(self, doc_freq, mode):
        """
        Returns the inverse document frequency of a token.
        :param doc_freq: The document frequency of a token.
        :param mode: The mode of calculation.
        :return: The inverse document frequency of a token.
        """
        case = {
            'n': lambda x: 1,
            't': lambda x: math.log10(self.N / x),
            'p': lambda x: max(0, math.log10((self.N - x) / x))
        }
        return case[mode](doc_freq)
    
    def calculate_tf_idf(self, token, doc_id, tf_mode='l', idf_mode = 't', normalisation_mode='n'):
        """
        Returns the tf-idf score of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param tf_mode: The mode of calculation of term frequency.
        :param idf_mode: The mode of calculation of inverse document frequency.
        :param normalisation_mode: The mode of normalisation.
        :return: The tf-idf score of a token in a document.
        """
        doc_freq = sum([1 for doc_id in self.count_matrix[token] if self.count_matrix[token][doc_id] > 0])
        tf = self.calculate_tf(token, doc_id, mode=tf_mode)
        idf = self.calculate_idf(doc_freq, mode=idf_mode)
        # TODO Add more normalisations
        case = {
            'n': lambda x: x,
        }
        return case[normalisation_mode](tf * idf)

    def calculate_bm25(self, token, doc_id, k=1.5):
        """
        Returns the bm25 score of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param k: The k value.
        :return: The bm25 score of a token in a document.
        """
        term_freq = self.count_matrix[token][doc_id]
        doc_freq = sum([1 for doc_id in self.count_matrix[token] if self.count_matrix[token][doc_id] > 0])
        L_d = len(self.tokenised_documents[doc_id])
        tf_component = (term_freq) / (k * (L_d / self.L_bar) + term_freq + 0.5)
        idf_component = math.log10((self.N - doc_freq + 0.5) / (doc_freq + 0.5))
        return tf_component * idf_component
    
    def get_tfidf_query_vector(self, query):
        tokenised_query = self.tokeniser.tokenise(query)
        query_vector = np.array([0 for _ in range(len(self.vocab))])
        for i in range(len(self.vocab)):
            token = self.vocab[i]
            if token in tokenised_query:
                tf = tokenised_query.count(token)
                df = len(self.count_matrix[token])
                tfidf = self.calculate_tf_idf(tf, df)
                query_vector[i] = tfidf
        return query_vector
    
    def get_bm25_query_vector(self, query):
        tokenised_query = self.tokeniser.tokenise(query)
        query_vector = np.array([0 for _ in range(len(self.vocab))])
        for i in range(len(self.vocab)):
            token = self.vocab[i]
            if token in tokenised_query:
                tf = tokenised_query.count(token)
                df = len(self.count_matrix[token])
                L_d = len(tokenised_query)
                bm25 = self.calculate_bm25(tf, df, L_d, self.L_bar)
                query_vector[i] = bm25
        return query_vector

    def get_query_vector(self, query):
        """
        Returns the vector representation of the query.
        :param query: The query.
        :return: The vector representation of the query.
        """
        if self.mode == "tfidf":
            return self.get_tfidf_query_vector(query)
        elif self.mode == "bm25":
            return self.get_bm25_query_vector(query)
        
    def make_score_matrix(self):
        """
        Returns the score matrix of the documents.
        :param documents: The documents.
        :return: The score matrix of the documents.
        """
        score_function = {
            'tfidf': self.calculate_tf_idf,
            'bm25': self.calculate_bm25
        }
        score_matrix = {}
        for doc_id, _ in enumerate(self.tokenised_documents):
            score_matrix[doc_id] = {}
            for pos, token in enumerate(self.vocab):
                score_matrix[doc_id][pos] = score_function[self.mode](token, doc_id)
        return score_matrix

if __name__ == '__main__':
    documents = [
        "This is the first document and second document.",
        "This document is the second document and fourth document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
    query = "This document might be the second document."
    vsm = VectorSpaceModel(documents, mode='bm25')
    print(vsm.score_matrix)

