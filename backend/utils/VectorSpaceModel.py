# from sklearn.feature_extraction.text import TfidfVectorizer

import numpy as np
from Tokeniser import Tokeniser
import math

class VectorSpaceModel:

    def __init__(self, documents, mode='tfidf'):
        self.mode = mode
        self.tokeniser = Tokeniser()
        self.tokenised_documents = [self.tokeniser.tokenise(document) for document in documents]
        self.N = len(self.tokenised_documents)
        self.vocab = self.make_vocab()
        self.count_matrix = self.make_count_matrix()
        self.score_matrix = self.make_score_matrix()

    def make_vocab(self):
        vocab = set()
        for tokenised_document in self.tokenised_documents:
            vocab.update(tokenised_document)
        vocab = list(vocab)
        vocab.sort()
        return vocab
    
    def make_count_matrix(self):
        # Count Matrix = {token: {doc_id: count}}
        vocab = self.vocab
        count_matrix = {}
        for token in vocab:
            count_matrix[token] = {}
            for i, tokenised_document in enumerate(self.tokenised_documents):
                count_matrix[token][i] = tokenised_document.count(token)
        return count_matrix
    
    def calculate_tf_idf(self, term_freq, doc_freq, use_smoothing=True):
        k = 0
        if use_smoothing:
            k = 1
        return (1 + math.log10(term_freq + k)) * (math.log10(self.N / doc_freq + k))

    def calculate_bm25(self, term_freq, doc_freq, L_d, L_bar, k=1.5):
        tf_component = (term_freq) / (k * (L_d / L_bar) + term_freq + 0.5)
        idf_component = math.log10((self.N - doc_freq + 0.5) / (doc_freq + 0.5))
        return tf_component * idf_component

    def make_tfidf_matrix(self):
        tf_idf_matrix = {}
        for token in self.count_matrix:
            tf_idf_matrix[token] = {}
            for doc_id in self.count_matrix[token]:
                tf = self.count_matrix[token][doc_id]
                df = len(self.count_matrix[token])
                tf_idf_matrix[token][doc_id] = self.calculate_tf_idf(tf, df)
        return tf_idf_matrix

    def make_bm25_matrix(self):
        bm25_matrix = {}
        L_bar = sum([len(document) for document in self.tokenised_documents]) / len(self.tokenised_documents)
        for token in self.count_matrix:
            bm25_matrix[token] = {}
            for doc_id in self.count_matrix[token]:
                tf = self.count_matrix[token][doc_id]
                df = len(self.count_matrix[token])
                L_d = len(self.tokenised_documents[doc_id])
                bm25_matrix[token][doc_id] = self.calculate_bm25(tf, df, L_d, L_bar)
        return bm25_matrix
    
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
        L_bar = sum([len(document) for document in self.tokenised_documents]) / len(self.tokenised_documents)
        for i in range(len(self.vocab)):
            token = self.vocab[i]
            if token in tokenised_query:
                tf = tokenised_query.count(token)
                df = len(self.count_matrix[token])
                L_d = len(tokenised_query)
                bm25 = self.calculate_bm25(tf, df, L_d, L_bar)
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
        if self.mode == "tfidf":
            return self.make_tfidf_matrix()
        elif self.mode == "bm25":
            return self.make_bm25_matrix()
    
    def cosine_similarity(self, query_vector):
        """
        Calculates the cosine similarity between the query and the documents.
        :param query_vector: The vector representation of the query.
        :return: The cosine similarity between the query and the documents.
        """
        pass
    
    def get_top_n(self, query_vector, n):
        """
        Returns the top n documents based on the cosine similarity.
        :param query_vector: The vector representation of the query.
        :param n: The number of documents to return.
        :return: The top n documents.
        """
        cosine_similarity = self.cosine_similarity(query_vector)
        return np.argsort(cosine_similarity, axis=0)[-n:][::-1]

if __name__ == '__main__':
    documents = [
        "This is the first document.",
        "This document is the second document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
    query = ["This document might be the second document."]
    vsm = VectorSpaceModel(documents, mode='bm25')
    print(vsm.score_matrix)

