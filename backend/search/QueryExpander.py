from nltk.corpus import wordnet as wn
import random
import spacy
import sys
sys.path.append('../')
from utils.VectorSpaceModel import VectorSpaceModel


class QueryExpander:
    """
    This class is responsible for Query Expansion.
    It is able to expand a query based on a mode.
    Modes:
        syn - Expands the query with synonyms.
        prf - Expands the query with PRF (Pseudo Relevance Feedback)
        bert - Expands the query with BERT. TODO
    """
    def __init__(self, vsm):
        """
        Initialises the Query Expander.
        """
        self.nlp = spacy.load("en_core_web_sm")
        self.vsm = vsm

    def expand(self, query, mode="prf"):
        """
        Expands a query based on the mode.
        :param query: The query to be expanded.
        :return: The expanded query.
        """
        case = {
            "syn": self._syn_expand,
            "prf": self._prf_expand
        }
        if mode == "prf":
            query_vector = self.vsm.get_query_vector(query)
            print("Old query: ", [x for y in query_vector.toarray().tolist() for x in y])
            returned_vectors = self.vsm.calculate_vector_similarity(query_vector)
            return case[mode](query_vector, returned_vectors)
        return case[mode](query)
        
    def _syn_expand(self, query, words_to_replace=3):
        """
        Expands a query with synonyms.
        :param query: The query to be expanded.
        :param words_to_replace: The number of words to replace. (Default: 1)
        :return: The expanded query.
        """
        token_pos = [(token, token.pos_) for token in self.nlp(query)]
        tokens_to_replace = random.sample(token_pos, words_to_replace)
        query_tokens = [token.text for token, _ in token_pos]
        print("Old query: {}".format(query))
        for token, pos in tokens_to_replace:
            synsets = []
            if pos == "NOUN":
                synsets = wn.synsets(token.text, pos=wn.NOUN)
            elif pos == "VERB":
                synsets = wn.synsets(token.text, pos=wn.VERB)
            elif pos == "ADJ":
                synsets = wn.synsets(token.text, pos=wn.ADJ)
            elif pos == "ADV":
                synsets = wn.synsets(token.text, pos=wn.ADV)
            if synsets:
                different_words = [synset for synset in synsets if synset.lemmas()[0].name() != token.text]
                synset = random.choice(different_words)
                query_tokens.append(synset.lemmas()[0].name())
        print("New query: {}".format(" ".join(query_tokens)))
        new_query = " ".join(query_tokens)
        return new_query

    def _get_centroid(self, doc_vectors_tuple, top_t):
        """
        Calculates the centroid of a list of document vectors.
        :param doc_vectors: The list of document vectors.
        :param top_t: The number of terms to be used. (Default: 5)
        :return: The centroid of the document vectors.
        """
        centroid = [0 for _ in range(len(doc_vectors_tuple))]
        for doc_vector in doc_vectors_tuple:
            doc_id, _ = doc_vector
            doc_vector = self.vsm.score_matrix[doc_id]
            # top_k_terms = self._get_top_t_terms_in_vector(doc_vector, t=top_t)
            dense_vector = [x for y in doc_vector.toarray().tolist() for x in y]
            centroid = [centroid[i] + dense_vector[i] for i in range(len(doc_vectors_tuple))]
        centroid = [score / len(doc_vectors_tuple) for score in centroid]
        return centroid
    
    def _get_top_t_terms_in_vector(self, vector, t):
        """
        Returns the top k terms in a vector.
        :param vector: The vector.
        :param k: The number of terms to return. (Default: 5)
        :return: The top k terms in the vector.
        """
        doc_id, _ = vector
        doc_vector = self.vsm.score_matrix[doc_id]
        sorted_vector = sorted(doc_vector, key=lambda x: x, reverse=True)
        return sorted_vector[:t]

    def _prf_expand(self, query_vector, returned_vectors, top_d=1, top_t=5, bottom_d=1, bottom_t=-5, alpha=1, beta=1, gamma=0):
        """
        Expands a query with pseudo relevance feedback.
        :param query_vector: The query to be expanded.
        :param returned_vectors: The list of document vectors returned from the search.

        :param top_d: The number of relevant documents to be used. (Default: 5)
        :param top_t: The number of terms to be used. (Default: 5)
        :param bottom_d: The number of irrelevant documents to be used. (Default: 5)
        :param bottom_t: The number of terms to be used. (Default: 5)
        :param alpha: The weight of the original query. (Default: 1)
        :param beta: The weight of the relevant documents. (Default: 1)
        :param gamma: The weight of the irrelevant documents. (Default: 0)

        :return: The expanded query.
        """
        relevant_doc_vectors = returned_vectors[:top_d]
        dense_query_vector = [x for y in query_vector.toarray().tolist() for x in y]
        augmented_query_vector = alpha * dense_query_vector + beta * self._get_centroid(relevant_doc_vectors, top_d)
        if gamma:
            irrelevant_doc_vectors = returned_vectors[-bottom_d:]
            augmented_query_vector += gamma * self._get_centroid(irrelevant_doc_vectors, bottom_t,)
        return augmented_query_vector


if __name__ == "__main__":
    documents = ["I want to buy a car", "This is a random document", "I crave a truck"]
    query = "I want to buy a vehicle"
    vsm = VectorSpaceModel(documents, use_stopping=False, mode='bm25')
    query_expander = QueryExpander(vsm)
    expanded_query = query_expander.expand(query, mode="syn")