import numpy as np
import math
import sys
sys.path.append('./backend')
from Tokeniser import Tokeniser
from Crawler import Crawler
from QueryExpander import QueryExpander
import scipy.sparse as sp
import time
import pickle
import os
import logging
from sklearn.metrics.pairwise import cosine_similarity

INDEX_BASE_DIR = os.path.join(os.path.dirname(__file__), '../database/collection')
CRAWL_CACHE_PATH = os.path.join(os.path.dirname(__file__), '../utils/url_cache.pkl')
VSM_CACHE_PATH = os.path.join(os.path.dirname(__file__), '../utils/vsm_cache.pkl')

class VectorSpaceModel:
    """
    This class performs vector space model calculations.
    We provide these options:
        Use stopping (i.e., remove English stop words such as 'and', 'or', and 'but')
        Use different modes of calculation (i.e., tf-idf, bm25)
    """
    def __init__(self, mode='tfidf'):
        """
        Initialise the VectorSpaceModel class
        documents: list[str]    List of documents to perform vector space model calculations on
        use_stopping: Boolean   If true, remove stop words.
        mode: str               Mode of calculation (i.e., tf-idf, bm25)
        """
        # Initialise data structures
        self.mode = mode
        self.crawler = Crawler(INDEX_BASE_DIR, CRAWL_CACHE_PATH)
        self.documents = []
        self.url_to_docid = {}
        self.docid_to_url = {}
        self.documents = []
        self.logger = logging.getLogger(self.__class__.__name__) 
        
        # Initialise VSM
        cache_exists = os.path.exists(VSM_CACHE_PATH)
        if cache_exists:
            self.logger.info("Loading VSM from cache.")
            self.load_from_file()
        else:
            self.logger.info("Building VSM from scratch.")
            self.build_vsm()

    def save_to_file(self, filename=VSM_CACHE_PATH):
        """
        Save the VectorSpaceModel to a file.
        """
        data = {
            'url_to_docid': self.url_to_docid,
            'docid_to_url': self.docid_to_url,
            'documents': self.documents,
            'tokenised_documents': self.tokenised_documents,
            'vocab': self.vocab,
            'count_matrix': self.count_matrix,
            'idf': self.idf,
            'score_matrix': self.score_matrix
        }
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        self.logger.info(f"Saved VectorSpaceModel to {filename}")

    def load_from_file(self, filename=VSM_CACHE_PATH):
        """
        Load the VectorSpaceModel from a file.
        """
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            self.tokeniser = Tokeniser()
            self.url_to_docid = data['url_to_docid']
            self.docid_to_url = data['docid_to_url']
            self.documents = data['documents']
            self.tokenised_documents = data['tokenised_documents']
            self.vocab = data['vocab']
            self.count_matrix = data['count_matrix']
            self.idf = data['idf']
            self.score_matrix = data['score_matrix']
            self.logger.info(f"Loaded VectorSpaceModel from {filename}")
        except FileNotFoundError:
            self.logger.error(f"File {filename} not found. Building VectorSpaceModel from scratch.")
            self.__init__()

    def build_vsm(self):
        self.retrieve_and_tokenise_documents()

        self.precompute_constants()
        
        # Make Vocabulary
        # Vocabulary of the form {token: token_id}
        self.vocab = self.make_vocab()

        # Count Matrix
        # Inverted Index of the form {token: {doc_id: count}} (Sparse Matrix)
        start = time.time()
        self.count_matrix = self.make_count_matrix()
        end = time.time()
        self.logger.info(f"Count Matrix time: {end - start}")

        # Pre-compute the inverse document frequency for each token
        start = time.time()
        self.precompute_idf()
        end = time.time()
        self.logger.info(f"IDF time: {end - start}")

        # Score Matrix of the form {doc_id: {token: score}} (Sparse Matrix)
        start = time.time()
        self.score_matrix = self.make_score_matrix()
        end = time.time()
        self.logger.info(f"Score Matrix time: {end - start}")

        self.save_to_file()

    def get_documents(self, include_subsections=False):
        """
        Get the documents from the crawler and store them in the documents list.
        """
        self.crawler.load_cache()
        crawler_url_cache = self.crawler.cache # {url: checksum}
        if not crawler_url_cache:
            self.logger.info("No files found in the base directories.")
            raise Exception("No files found in the base directories.")
        for file_path, _ in crawler_url_cache.items():
            if file_path not in self.url_to_docid:
                self.logger.info(f"Processing file: {file_path}")
                self.url_to_docid[file_path] = len(self.url_to_docid)
                self.docid_to_url[len(self.url_to_docid)-1] = file_path
                doc_dict = self.crawler.html_to_dict(file_path, self.url_to_docid[file_path])
                raw_text = doc_dict.get('HEADLINE', "") + " " + doc_dict.get('TEXT', "")
                if include_subsections:
                    for tag in ["PROFILE", "DATE", "BYLINE", "DATELINE", "PUB", "PAGE"]:
                        raw_text += doc_dict.get(tag, "")
                self.documents.append(raw_text)

    def retrieve_and_tokenise_documents(self, include_subsections=False, use_stopping=False, use_stemming=False, punctuations_to_keep=[]):
        # Retrieve and tokenise the documents
        self.get_documents(include_subsections=include_subsections)
        self.tokeniser = Tokeniser(use_stopping=use_stopping, use_stemming=use_stemming, punctuations_to_keep=punctuations_to_keep)
        start = time.time()
        self.tokenised_documents = [self.tokeniser.tokenise(document) for document in self.documents]
        end = time.time()
        self.logger.info(f"Tokenisation time: {end - start}")

    def precompute_constants(self):
        # Pre-compute constants
        self.N = len(self.tokenised_documents)
        self.L_bar = sum([len(document) for document in self.tokenised_documents]) / self.N

    def make_vocab(self):
        """
        Returns the vocabulary of the documents.
        """
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
        """
        Pre-compute the inverse document frequency for each token.
        """
        # len(self.count_matrix[token_id]) returns the document frequency of the token 
        # TODO Can this be optimised further?
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

        tokenised_query = self.tokeniser.tokenise(query)
        query_vector_data = []
        query_vector_row = []
        query_vector_col = []

        for token in set(tokenised_query):  # Use set to avoid redundant computations
            if token in self.vocab:
                token_id = self.vocab[token]
                token_count = tokenised_query.count(token)
                score = score_function[self.mode](token, 0, is_query=True, query_term_freq=token_count)
                query_vector_data.append(score)
                query_vector_row.append(token_id)
                query_vector_col.append(0)

        query_vector = sp.csr_matrix((query_vector_data, (query_vector_row, query_vector_col)), shape=(len(self.vocab), 1))
        return query_vector

    def calculate_vector_similarity(self, query_vector):
        """
        Returns the cosine similarity of the query vector with the document vectors.
        :param query_vector: The query vector.
        :return: The similarity of the query vector with the document vectors.
        """
        similarity = cosine_similarity(self.score_matrix, query_vector.T)
        return sorted(enumerate(similarity), key=lambda x: x[1], reverse=True)

    def process_query(self, query, top=10, is_expanded=False):
        """
        Returns the documents that contain the query.
        :param query: The query.
        :return: The documents that contain the query.
        """
        start = time.time()
        if is_expanded:
            query_vector = sp.csr_matrix(query, shape=(1, len(self.vocab))).T
        else:
            query_vector = self.get_query_vector(query)
        end = time.time()
        self.logger.info(f"Query Vectorisation time: {end-start}")

        start = time.time()
        similarity = self.calculate_vector_similarity(query_vector)[:top]
        end = time.time()
        self.logger.info(f"Query time: {end-start}")
        doc_id_positions = [(doc_id, []) for doc_id, _ in similarity]
        return doc_id_positions
