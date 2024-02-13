import numpy as np
import math
import sys
sys.path.append('./backend')
from indexer.Tokeniser import Tokeniser
import scipy.sparse as sp
import time

class VectorSpaceModel:
    """
    This class performs vector space model calculations.
    We provide these options:
        Use stopping (i.e., remove English stop words such as 'and', 'or', and 'but')
        Use different modes of calculation (i.e., tf-idf, bm25)
    """
    def __init__(self, documents, use_stopping=False, use_stemming=False, punctuations_to_keep=[], mode='tfidf'):
        """
        Initialise the VectorSpaceModel class
        documents: list[str]    List of documents to perform vector space model calculations on
        use_stopping: Boolean   If true, remove stop words.
        mode: str               Mode of calculation (i.e., tf-idf, bm25)
        """
        self.mode = mode

        self.tokeniser = Tokeniser(use_stopping=use_stopping, use_stemming=use_stemming, punctuations_to_keep=punctuations_to_keep)
        start = time.time()
        self.tokenised_documents = [self.tokeniser.tokenise(document) for document in documents]
        end = time.time()
        print("Tokenisation time: ", end - start)

        self.N = len(self.tokenised_documents)
        self.L_bar = sum([len(document) for document in self.tokenised_documents]) / self.N
        
        # Vocabulary of the form {token: token_id}
        self.vocab = self.make_vocab()

        # Inverted Index of the form {token: {doc_id: count}} (Sparse Matrix)
        start = time.time()
        self.count_matrix = self.make_count_matrix()
        end = time.time()
        print("Count Matrix time: ", end - start)

        # Pre-compute the inverse document frequency for each token
        start = time.time()
        self.precompute_idf()
        end = time.time()
        print("IDF Precomputation time: ", end - start)

        # Score Matrix of the form {doc_id: {token: score}} (Sparse Matrix)
        start = time.time()
        self.score_matrix = self.make_score_matrix()
        end = time.time()
        print("Score Matrix time: ", end - start)

    def make_vocab(self):
        vocab = set()
        for tokenised_document in self.tokenised_documents:
            vocab.update(tokenised_document)
        vocab_dict = {token: token_id for token_id, token in enumerate(vocab)}
        return vocab_dict
    
    def make_count_matrix(self):
        """
        Returns the count matrix of the documents.
        :return: The count matrix of the documents.
        Count Matrix = {token: {doc_id: count}}
        """
        # Initialize the count matrix as a DOK matrix
        count_matrix = sp.dok_matrix((len(self.vocab), self.N), dtype=np.int32)

        # Loop through each document only once and update the count_matrix accordingly
        for doc_id, tokenised_document in enumerate(self.tokenised_documents):
            # Count tokens and update count_matrix
            unique_tokens, counts = np.unique(tokenised_document, return_counts=True)
            token_indices = [self.vocab[token] for token in unique_tokens]
            count_matrix[token_indices, doc_id] = counts

        return count_matrix
    
    def precompute_idf(self):
        # Pre-compute the inverse document frequency for each token (Only for TFIDF)
        # len(self.count_matrix[token_id]) returns the document frequency of the token (TODO Can this be optimised further?)
        if self.mode == 'tfidf':
            self.idf = {token: self.calculate_idf(len(self.count_matrix[token_id]), mode='t') for token, token_id in self.vocab.items()}
        elif self.mode == 'bm25':
            self.idf = {token: self.calculate_idf(len(self.count_matrix[token_id]), mode='bm25') for token, token_id in self.vocab.items()}
    
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
        score_matrix = sp.dok_matrix((self.N, len(self.vocab)), dtype=np.float32)
        for doc_id, tokenised_document in enumerate(self.tokenised_documents):
            for token in tokenised_document:
                token_id = self.vocab[token]
                score_matrix[doc_id, token_id] = score_function[self.mode](token, doc_id)
        return score_matrix
    
    def calculate_tf(self, token_id, doc_id, mode, is_query=False, query_term_freq=None):
        """
        Returns the term frequency of a token in a document.
        :param token: The token.
        :param doc_id: The document id.
        :param mode: The mode of calculation.
        :return: The term frequency of a token in a document.
        """
        if is_query:
            term_freq = query_term_freq
        else:
            term_freq = self.count_matrix[token_id, doc_id]
        if term_freq == 0:
            return 0
        if mode == 'a':
            max_term_freq = max(self.count_matrix[:, doc_id].toarray())
        case = {
            'n': lambda x: x,
            'l': lambda x: 1 + math.log10(x),
            # Only works with calculating tf for a matrix not a query.
            'a': lambda x: 0.5 + (0.5 * (x / max_term_freq))
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
            'n': lambda _: 1,
            't': lambda x: math.log10(self.N / x),
            'p': lambda x: max(0, math.log10((self.N - x) / x)),
            'bm25': lambda x: math.log10((self.N - x + 0.5) / (x + 0.5))
        }
        return case[mode](doc_freq)
    
    def calculate_tf_idf(self, token, doc_id, tf_mode='l', normalisation_mode='n', is_query=False, query_term_freq=None):
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
        token_id = self.vocab[token]
        tf = self.calculate_tf(token_id, doc_id, mode=tf_mode, is_query=is_query, query_term_freq=query_term_freq)
        idf = self.idf[token]
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
        token_id = self.vocab[token]
        if is_query:
            term_freq = query_term_freq
        else:
            term_freq = self.count_matrix[token_id, doc_id]
        L_d = len(self.tokenised_documents[doc_id])
        tf_component = (term_freq) / (k * (L_d / self.L_bar) + term_freq + 0.5)
        idf_component = self.idf[token]
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
                token_id = self.vocab[token]
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
    with open('./backend/utils/test_documents.txt', 'r') as file:
        documents = file.readlines()
    query = "For Adam was first formed, then eve"
    vsm = VectorSpaceModel(documents, use_stopping=False, use_stemming=False, mode='tfidf')
    start = time.time()
    query_vector = vsm.get_query_vector(query)
    similarity = vsm.calculate_vector_similarity(query_vector)
    end = time.time()
    print("Query time: ", end - start)