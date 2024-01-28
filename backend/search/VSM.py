from sklearn.feature_extraction.text import TfidfVectorizer

class VSM:
    """
    This class is responsible for Vector Space Model.
    It is able to calculate the cosine similarity between a query and a document.
    """

    def __init__(self, docs, tokenizer):
        """
        Initialises the Vector Space Model.
        :param docs: A list of documents. (Current assumption is that it is a String)
        :param tokenizer: The tokenizer to be used.
        """
        self.vectorizer = TfidfVectorizer()
        self.index = self.vectorizer.fit_transform([doc for doc in docs])
        self.tokenizer = tokenizer

    def _cosine_similarity(self, query_vector, doc_vector):
        """
        Calculates the cosine similarity between a query and a document.
        :param query_vector: The query vector.
        :param doc_vector: The document vector.
        :return: The cosine similarity between the query and the document.
        """
        return ((query_vector * doc_vector.T).A)[0][0]

    def search(self, query):
        """
        Searches the index for documents that match the query.
        :param query: The query to be searched.
        :return: A list of documents that match the query.
        """
        query_vector = self.vectorizer.fit_transform([query])
        results = []
        for doc in self.index.documents:
            doc_vector = self.vectorizer.transform([doc.text])
            similarity = self._cosine_similarity(query_vector, doc_vector)
            results.append((doc, similarity))
        results.sort(key=lambda x: x[1], reverse=True)
        return results