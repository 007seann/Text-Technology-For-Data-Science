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
    
    def calculate_tf(self, token, term_freq, mode):
        term_freqs = self.count_matrix[token].values()
        if term_freq == 0:
            return 0
        case = {
            'n': lambda x: x,
            'l': lambda x: 1 + math.log10(x),
            'a': lambda x: 0.5 + (0.5 * (x / max(term_freqs)))
        }
        return case[mode](term_freq)

    def calculate_idf(self, doc_freq, mode):
        case = {
            'n': lambda x: 1,
            't': lambda x: math.log10(self.N / x),
            'p': lambda x: max(0, math.log10((self.N - x) / x))
        }
        return case[mode](doc_freq)
    
    def calculate_tf_idf(self, token, doc_id, tf_mode='l', idf_mode = 't', normalisation_mode='n'):
        term_freq = self.count_matrix[token][doc_id]
        doc_freq = sum([1 for doc_id in self.count_matrix[token] if self.count_matrix[token][doc_id] > 0])
        tf = self.calculate_tf(token, term_freq, mode=tf_mode)
        idf = self.calculate_idf(doc_freq, mode=idf_mode)
        # TODO Add more normalisations
        case = {
            'n': lambda x: x,
        }
        return case[normalisation_mode](tf * idf)


    def calculate_bm25(self, term_freq, doc_freq, L_d, L_bar, k=1.5):
        tf_component = (term_freq) / (k * (L_d / L_bar) + term_freq + 0.5)
        idf_component = math.log10((self.N - doc_freq + 0.5) / (doc_freq + 0.5))
        return tf_component * idf_component

    def make_tfidf_matrix(self):
        tf_idf_matrix = {}
        for token in self.count_matrix:
            tf_idf_matrix[token] = {}
            for doc_id in self.count_matrix[token]:
                tf_idf_matrix[token][doc_id] = self.calculate_tf_idf(token, doc_id)
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
                bm25_matrix[token][doc_id] = -1 * self.calculate_bm25(tf, df, L_d, L_bar)
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
        cosine_similarity = np.zeros((len(self.tokenised_documents), 1))
        for token in self.count_matrix:
            for doc_id in self.count_matrix[token]:
                cosine_similarity[doc_id] += query_vector[self.vocab.index(token)] * self.score_matrix[token][doc_id]
        return cosine_similarity
    
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
        "This is the first document and second document.",
        "This document is the second document and fourth document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
    query = "This document might be the second document."
    vsm = VectorSpaceModel(documents, mode='bm25')
    print(vsm.score_matrix)

