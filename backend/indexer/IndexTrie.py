from pprint import pprint as pp
from collections import defaultdict
from PostingLinkedList import PostingLinkedList
import matplotlib.pyplot as plt
import networkx as nx

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
    
    def visualize_word_index(self, letter_font_size=12, 
                            posting_font_size=10,
                            node_color='lightblue',
                            edge_color='gray',
                            posting_offset=50):
        G = nx.DiGraph()
        node_id = 0
        node_positions = {}

        def add_node(parent_id, char, node, postings):
            nonlocal node_id
            current_id = node_id
            G.add_node(current_id)
            if parent_id is not None:
                G.add_edge(parent_id, current_id)
            node_id += 1
            return current_id

        def traverse(node, parent_id=None, word=''):
            postings = [str(post) for post in node.doc_postings.values()]
            current_id = add_node(parent_id, word[-1] if word else 'root', node, postings)
            label = str(word[-1]).upper() if word else 'root'
            node_positions[current_id] = {'label': label, 'postings': postings}
            for char, child in node.children.items():
                traverse(child, current_id, word + char)

        traverse(self.root)
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        nx.draw(G, pos, with_labels=False, arrows=False, node_color=node_color, edge_color=edge_color, node_size=2000)

        for node_id, position in pos.items():
            label = node_positions[node_id]['label']
            postings = node_positions[node_id]['postings']
            plt.text(position[0], position[1], label, fontsize=letter_font_size, fontweight='bold', ha='center', va='center')
            plt.text(position[0], position[1] - posting_offset, '\n'.join(postings), fontsize=posting_font_size, ha='center', va='center')

        plt.show()
    
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