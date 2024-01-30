

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.doc_ids = set()


class IndexTrie:
    def __init__(self):
        self.root = None

    def insert(self, word, doc_id, position):
        pass
            