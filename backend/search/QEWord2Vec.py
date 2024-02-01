import nltk
import gensim.models.word2vec as w2v

class QWWord2Vec:


    def __init__(self, documents):
        tokenised_documents = [nltk.tokenize.word_tokenize(document) for document in documents]
        self.w2v = w2v.Word2Vec(tokenised_documents, vector_size=100, window=5, min_count=1, workers=4)

if __name__ == '__main__':
    documents = ["This is a sentence", "This is another sentence"]
    model = QWWord2Vec(documents)
    print(model.w2v.wv.key_to_index)
