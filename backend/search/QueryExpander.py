from nltk.corpus import wordnet as wn
import nltk
import random
import spacy


class QueryExpander:
    """
    This class is responsible for Query Expansion.
    It is able to expand a query based on a mode.
    Modes:
        Basic - Expands the query with synonyms.
        Intermediate - Expands the query with synonyms and related words.
        Advanced - Expands the query with synonyms, related words and hypernyms.
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
        new_query_tokens = query_tokens.copy()
        token_pos = [(token, token.pos_) for token in self.nlp(" ".join(query_tokens))]
        tokens_to_replace = random.sample(token_pos, words_to_replace)
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
                synset = random.choice(synsets)
                new_query_tokens[new_query_tokens.index(token.text)] = synset.lemmas()[0].name()
        print("Old query: {}".format(query_tokens))
        print("New query: {}".format(new_query_tokens))

    def _get_centroid(self, doc_vectors):
        """
        Calculates the centroid of a list of document vectors.
        :param doc_vectors: The list of document vectors.
        :return: The centroid of the document vectors.
        """
        centroid = [0 for _ in range(len(doc_vectors[0]))]
        for doc_vector in doc_vectors:
            for i in range(len(doc_vector)):
                centroid[i] += doc_vector[i]
        centroid = [x / len(doc_vectors) for x in centroid]
        return centroid

    def _prf_expand(self, query_vector, returned_vectors, top_k=5, bottom_k=5, alpha=1, beta=1, gamma=0):
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
        irrelevant_doc_vectors = returned_vectors[-bottom_k:]
        augmented_query_vector = alpha * query_vector + beta * self._get_centroid(relevant_doc_vectors) - gamma * self._get_centroid(irrelevant_doc_vectors)
        return augmented_query_vector



if __name__ == "__main__":
    query = ["I", "want", "to", "buy", "a", "car"]
    query_expander = QueryExpander()
    query_expander.expand(query, mode="syn")