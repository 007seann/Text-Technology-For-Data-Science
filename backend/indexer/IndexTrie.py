from pprint import pprint as pp
from collections import defaultdict
from PostingLinkedList import PostingLinkedList
class WordIndexNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.index_id = 0
        self.word_frequency = 0
        self.doc_postings = defaultdict(list)

class WordIndex:
    def __init__(self):
        self.root = WordIndexNode()
        self.index_size = 0

    def insert(self, word, document_id, postings):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = WordIndexNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.index_id = self.index_size
        node.word_frequency += 1
        node.doc_postings[document_id] = postings
        self.index_size += 1
        
    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return (word, node.index_id, node.word_frequency) if node.is_end_of_word else None
    
    def traverse_words(self):
        word_list = []
        def traverse(node, word):
            if node.is_end_of_word:
                word_list.append((word, node.index_id, node.word_frequency))
            for char, child_node in node.children.items():
                traverse(child_node, word + char)
        traverse(self.root, "")
        return word_list
    
    def __len__(self):
        return self.index_size
    
    def __contains__(self, word):
        return self.search(word) is not None
    
    def __getitem__(self, word):
        return self.search(word)
    
    def __str__(self):
        return str(self.traverse_words())
    
    def __repr__(self):
        return str(self)
    
if __name__ == "__main__":
    
    #test
    test_ll = PostingLinkedList([1,2,3,5])
    wordindex = WordIndex()
    wordindex.insert("hello", 1, test_ll)
    wordindex.insert("help", 2, test_ll)
    wordindex.insert("this", 3, test_ll)
    wordindex.insert("that", 4, test_ll)

    for word in wordindex.traverse_words():
        print(word)