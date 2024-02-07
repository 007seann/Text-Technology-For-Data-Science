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
    def __init__(self):
        """
        Initialises the Query Expander.
        """
        self.nlp = spacy.load("en_core_web_sm")

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
        return case[mode](query)
        
    def _syn_expand(self, query_tokens, words_to_replace=1):
        """
        Expands a query with synonyms.
        :param query: The query to be expanded.
        :param words_to_replace: The number of words to replace. (Default: 1)
        :return: The expanded query.
        """
        token_pos = [(token, token.pos_) for token in self.nlp(" ".join(query_tokens))]
        tokens_to_replace = random.sample(token_pos, words_to_replace)
        print("Old query: {}".format(query_tokens))
        for token, pos in tokens_to_replace:
            if pos == "NOUN":
                synsets = wn.synsets(token.text, pos=wn.NOUN)
            elif pos == "VERB":
                synsets = wn.synsets(token.text, pos=wn.VERB)
            elif pos == "ADJ":
                synsets = wn.synsets(token.text, pos=wn.ADJ)
            elif pos == "ADV":
                synsets = wn.synsets(token.text, pos=wn.ADV)
            else:
                synsets = []
            if synsets:
                different_words = [synset for synset in synsets if synset.lemmas()[0].name() != token.text]
                synset = random.choice(different_words)
                query_tokens.append(synset.lemmas()[0].name())
        print("New query: {}".format(query_tokens))
        return query_tokens

    def _get_centroid(self, doc_vectors):
        """
        Calculates the centroid of a list of document vectors.
        :param doc_vectors: The list of document vectors.
        :return: The centroid of the document vectors.
        """
        centroid = [0 for _ in range(len(doc_vectors[0]))]
        for doc_vector in doc_vectors:
            top_k_terms = self._get_top_k_terms_in_vector(doc_vector)
            for i, score in top_k_terms:
                centroid[i] += score
        centroid /= len(doc_vectors)
        return centroid
    
    def _get_top_k_terms_in_vector(self, vector, k=5):
        """
        Returns the top k terms in a vector.
        :param vector: The vector.
        :param k: The number of terms to return. (Default: 5)
        :return: The top k terms in the vector.
        """
        enumerated_vector = list(enumerate(vector))
        sorted_vector = sorted(enumerated_vector, key=lambda x: x[1], reverse=True)
        return sorted_vector[:k]

    def _prf_expand(self, query_vector, returned_vectors, top_k=5, top_n=10, bottom_k=5, alpha=1, beta=1, gamma=0):
        """
        Expands a query with pseudo relevance feedback.
        :param query_vector: The query to be expanded.
        :param returned_vectors: The list of document vectors returned from the search.

        :param top_k: The number of relevant documents to be used. (Default: 5)
        :param bottom_k: The number of irrelevant documents to be used. (Default: 5)
        :param alpha: The weight of the original query. (Default: 1)
        :param beta: The weight of the relevant documents. (Default: 1)
        :param gamma: The weight of the irrelevant documents. (Default: 0)

        :return: The expanded query.
        """
        relevant_doc_vectors = returned_vectors[:top_k]
        if gamma == 0:
            irrelevant_doc_vectors = []
        else:
            irrelevant_doc_vectors = returned_vectors[-bottom_k:]
        augmented_query_vector = alpha * query_vector + beta * self._get_centroid(relevant_doc_vectors) - gamma * self._get_centroid(irrelevant_doc_vectors)
        return augmented_query_vector


if __name__ == "__main__":
    documents = ["I want to buy a car", "I want to buy a bike", "I want to buy a truck"]
    query = ["I", "want", "to", "buy", "a", "vehicle"]
    query_expander = QueryExpander()
    vsm = VectorSpaceModel(documents, use_stopping=False, mode='bm25')
    # query_vector = vsm.get_query_vector(query)
    query_expander.expand(query, mode="syn")