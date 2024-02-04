import os
import sys
import unittest

current_dir = os.getcwd()
module_path = '/backend/indexer'
parent_dir = os.path.abspath(current_dir + module_path)
sys.path.append(parent_dir)

from PostingLinkedList import PostingLinkedList
from PostingNode import PostingNode

class PostingLinkedListTest(unittest.TestCase):
    def test_initialization(self):
        pll = PostingLinkedList()
        self.assertIsNone(pll.head)
        self.assertEqual(len(pll), 0)
    
    def test_insert_and_length(self):
        pll = PostingLinkedList([1, 3, 2])
        self.assertEqual(len(pll), 3)
        self.assertEqual(pll.toList(), [1, 2, 3])

    def test_str_and_repr(self):
        pll = PostingLinkedList([1, 2, 3])
        self.assertEqual(str(pll), "1 --> 2 --> 3")
        self.assertEqual(repr(pll), "[1, 2, 3]")
    
    def test_decrement_postings(self):
        pll = PostingLinkedList([2, 3, 4])
        decremented = pll.decrement_postings(1)
        self.assertEqual(decremented.toList(), [1, 2, 3])
    
    def test_intersect(self):
        pll1 = PostingLinkedList([1, 2, 3])
        pll2 = PostingLinkedList([2, 3, 4])
        intersected = pll1.intersect(pll2)
        self.assertEqual(intersected.toList(), [2, 3])
    
    def test_union(self):
        pll1 = PostingLinkedList([1, 2])
        pll2 = PostingLinkedList([2, 3])
        united = pll1.union(pll2)
        self.assertEqual(united.toList(), [1, 2, 3])
    
    def test_toList(self):
        pll = PostingLinkedList([1, 3, 2])
        self.assertEqual(pll.toList(), [1, 2, 3])

if __name__ == '__main__':
    unittest.main()