import numpy as np
import math
import sys
sys.path.append('../')
sys.path.append('../backend')
from indexer.Tokeniser import Tokeniser
import scipy.sparse as sp

class VectorSpaceModel:
    """
    This class performs vector space model calculations.
    We provide these options:
        Use stopping (i.e., remove English stop words such as 'and', 'or', and 'but')
        Use different modes of calculation (i.e., tf-idf, bm25)
    """
    def __init__(self, documents, use_stopping=True, mode='tfidf'):
        """
        Initialise the VectorSpaceModel class
        documents: list[str]    List of documents to perform vector space model calculations on
        use_stopping: Boolean   If true, remove stop words.
        mode: str               Mode of calculation (i.e., tf-idf, bm25)
        """
        self.mode = mode
        self.tokeniser = Tokeniser(use_stopping=use_stopping)
        self.tokenised_documents = [self.tokeniser.tokenise(document) for document in documents]
        self.N = len(self.tokenised_documents)
        self.L_bar = sum([len(document) for document in self.tokenised_documents]) / self.N
        self.vocab = self.make_vocab()

        # Inverted Index of the form {token: {doc_id: count}} (Sparse Matrix)
        self.count_matrix = self.make_count_matrix()

        # Score Matrix of the form {doc_id: {token: score}} (Sparse Matrix)
        self.score_matrix = self.make_score_matrix()

    def make_vocab(self):
        """
        Returns the vocabulary of the documents.
        :param documents: The documents.
        :return: The vocabulary of the documents.
        """
        vocab = list()
        for tokenised_document in self.tokenised_documents:
            for token in tokenised_document:
                if token not in vocab:
                    vocab.append(token)
        # Do we need this?
        return vocab
    
    def make_count_matrix(self):
        """
        Returns the count matrix of the documents.
        :param documents: The documents.
        :return: The count matrix of the documents.
        Count Matrix = {token: {doc_id: count}}
        """
        count_matrix = sp.dok_matrix((len(self.vocab), self.N))
        for token_index, token in enumerate(self.vocab):
            for doc_id, tokenised_document in enumerate(self.tokenised_documents):
                count_matrix[token_index, doc_id] = tokenised_document.count(token)
        return count_matrix
    
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
        score_matrix = sp.dok_matrix((self.N, len(self.vocab)))
        for doc_id, _ in enumerate(self.tokenised_documents):
            for token_id, token in enumerate(self.vocab):
                score_matrix[doc_id, token_id] = score_function[self.mode](token, doc_id)
        return score_matrix
    
    def calculate_tf(self, token, doc_id, mode, is_query=False, query_term_freq=None):
        """
        Returns the term frequency of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param mode: The mode of calculation.
        :return: The term frequency of a token in a document.
        """
        term_freqs = self.count_matrix.getcol(doc_id).toarray()
        if is_query:
            term_freq = query_term_freq
        else:
            token_id = self.vocab.index(token)
            term_freq = self.count_matrix[token_id, doc_id]
        if term_freq == 0:
            return 0
        case = {
            'n': lambda x: x,
            'l': lambda x: 1 + math.log10(x),
            # Only works with calculating tf for a matrix not a query.
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
    
    def calculate_tf_idf(self, token, doc_id, tf_mode='l', idf_mode = 't', normalisation_mode='n', is_query=False, query_term_freq=None):
        """
        Returns the tf-idf score of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param tf_mode: The mode of calculation of term frequency.
        :param idf_mode: The mode of calculation of inverse document frequency.
        :param normalisation_mode: The mode of normalisation.
        :param is_query: Whether the token is in a query.
        :param query_term_freq: The term frequency of the token in the query.
        :return: The tf-idf score of a token in a document.
        """
        token_id = self.vocab.index(token)
        doc_freq = self.count_matrix.getrow(token_id).count_nonzero()
        tf = self.calculate_tf(token, doc_id, mode=tf_mode, is_query=is_query, query_term_freq=query_term_freq)
        idf = self.calculate_idf(doc_freq, mode=idf_mode)
        # TODO Add more normalisations
        case = {
            'n': lambda x: x,
        }
        return case[normalisation_mode](tf * idf)

    def calculate_bm25(self, token, doc_id, is_query=False, query_term_freq=None, k=1.5):
        """
        Returns the bm25 score of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param k: The k value.
        :return: The bm25 score of a token in a document.
        """
        token_id = self.vocab.index(token)
        if is_query:
            term_freq = query_term_freq
        else:
            term_freq = self.count_matrix[token_id, doc_id]
        doc_freq = self.count_matrix.getrow(token_id).count_nonzero()
        L_d = len(self.tokenised_documents[doc_id])
        tf_component = (term_freq) / (k * (L_d / self.L_bar) + term_freq + 0.5)
        idf_component = math.log10((self.N - doc_freq + 0.5) / (doc_freq + 0.5))
        return tf_component * idf_component

    def get_query_vector(self, query):
        """
        Returns the vector representation of the query.
        :param query: The query.
        :return: The vector representation of the query.
        """
        score_function = {
            'tfidf': self.calculate_tf_idf,
            'bm25': self.calculate_bm25
        }
        query_vector = sp.dok_array((len(self.vocab), 1))
        tokenised_query = self.tokeniser.tokenise(query)
        for token in tokenised_query:
            if token in self.vocab:
                token_id = self.vocab.index(token)
                token_count = tokenised_query.count(token)
                query_vector[token_id, 0] = score_function[self.mode](token, 0, is_query=True, query_term_freq=token_count)
        return query_vector
    
    def calculate_vector_similarity(self, query_vector):
        """
        Returns the similarity of the query vector with the document vectors.
        :param query_vector: The query vector.
        :return: The similarity of the query vector with the document vectors.
        """
        similarity = {}
        for doc_id in range(self.N):
            similarity[doc_id] = np.dot(self.score_matrix[doc_id].toarray(), query_vector.toarray())[0][0]
        return sorted(similarity.items(), key=lambda x: x[1], reverse=True)

if __name__ == '__main__':
    documents = [
        "This is the first document and second document.",
        "This document is the second document and fourth document.",
        "And this is the third one.",
        "Is this the first document?",
    ]
    query = "Is this the second document?"
    vsm = VectorSpaceModel(documents, use_stopping=False, mode='bm25')
    query_vector = vsm.get_query_vector(query)
    similarity = vsm.calculate_vector_similarity(query_vector)
    print(similarity)