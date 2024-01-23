from PostingLinkedList import PostingLinkedList
from Tokeniser import Tokeniser
from nltk.stem import PorterStemmer
from xml.etree import ElementTree as ET
import json
import os
import sys

string_path = "../../"
ROOT_DIR = os.path.abspath(string_path)
sys.path.append(ROOT_DIR)

with open("config.json", 'r') as file:
    config = json.load(file)

INDEX_SAVE_PATH = config["index_root_dir"]
COLLCETION_PATH = config["collection_root_dir"]


class PositionalIndex:
    def __init__(self):            
        # Stemming and Tokenisation utils
        self.stemmer = PorterStemmer() # TODO
        self.tokeniser = Tokeniser() #TODO
        
        # In memory data
        self.index = {}
        self.document_ids = set()
        self.vocabulary = set()
        self.vocabulary_size = 0
    
    # Will take an XML parsed doc. 
    def insert_document(self, document, include_subsections=False):
        doc_id = document.get("DOCNO")
    
        # Document has already been added. 
        if doc_id in self.document_ids:
            return
        
        # We collapse document into two sections
        merged_text = document.get("HEADLINE", "") + " " + document.get("TEXT", "")
        
        # Used if we need do to read any other subsections
        if include_subsections:
            for tag in ["PROFILE", "DATE", "BYLINE", "DATELINE", "PUB", "PAGE"]:
                merged_text += document.get(tag, "")
        
        # Mapping between token {term : PostingLinkedList}
        term_posting_mapping = {}
        token_index = 0
        token_stream = self.tokeniser.tokenise(merged_text)
        
        for token in token_stream:
            if self.enable_stopping and (token in self.stopwords):
                continue
            
            stemmed_token = self.stemmer.stem(token)
            
            # Caching the term and current posting
            if stemmed_token in term_posting_mapping:
                term_posting_mapping[stemmed_token].insert(token_index)
            else:
                term_posting = PostingLinkedList()
                term_posting.insert(token_index)
                term_posting_mapping[stemmed_token] = term_posting
            token_index += 1
        
        # Adding the term and posting to our index.
        for (term, new_postings) in term_posting_mapping.items():
            if term in self.index:
                doc_freq, doc_dict = self.index[term]
        
                if doc_id in doc_dict:
                    updated_postings_list = doc_dict[doc_id].union(new_postings)
                    doc_dict.update({ doc_id : updated_postings_list})
                    
                    self.index[term] = (doc_freq, doc_dict)
                else:
                    doc_freq = doc_freq + 1
                    doc_dict.update({ doc_id : new_postings})
                    
                    self.index[term] = (doc_freq, doc_dict)
            else:
                self.vocabulary.add(term)
                self.vocabulary_size += 1
                
                doc_freq = 1
                self.index[term] = (doc_freq, {doc_id : new_postings})
        
        # Add document to set.
        self.document_ids.add(doc_id)
    
    def reset_index(self):
        self.index = {}
        self.document_ids = set()
        self.vocabulary = set()
        self.vocabulary_size = 0
        
    def save_index(self, save_path=INDEX_SAVE_PATH):
        sorted_vocabulary = sorted(self.vocabulary)
        with open(save_path, 'w') as file:
            for term in sorted_vocabulary:
                (doc_freq, doc_dict) = self.index[term]
                file.write(term + ":" + str(doc_freq) + "\n")
                doc_list = sorted(doc_dict.keys())
                for doc_id in doc_list:
                    posting_string = ",".join(map(str, doc_dict[doc_id].toList()))
                    file.write("\t" + doc_id + ":" + posting_string + "\n")
                
    def load_index(self, load_path=INDEX_SAVE_PATH):
        self.vocabulary_size = 0
        self.vocabulary = set()
        self.index = {}
        
        with open(load_path, 'r') as file:
            lines = file.readlines()
            current_word = None
            doc_freq = None
            doc_posting_pairs = {}
            for line in lines:
                if not line.startswith('\t'):
                    if current_word:
                        self.index[current_word] = (int(doc_freq), doc_posting_pairs)
                        self.vocabulary.add(current_word)
                        self.vocabulary_size += 1
                        
                    word, doc_freq = line.split(":")
                    current_word = word
                    doc_posting_pairs = {}
                else:
                    doc_id, positions = line.strip().split(':')
                    doc_posting_pairs[doc_id] = PostingLinkedList(list(map(int, positions.split(','))))
                    self.document_ids.add(doc_id)
                    
            self.index[current_word] = (int(doc_freq), doc_posting_pairs)
            self.vocabulary.add(current_word)
            self.vocabulary_size += 1
            
class XMLDocParser:
    def __init__(self, filename):
        self.filename = filename

    def stream_docs(self):
        if not os.path.exists(self.filename):
            raise Exception("File does not exist: ", self.filename)
        
        # Use iterparse for efficient streaming
        context = ET.iterparse(self.filename, events=("start", "end"))
        current_doc = {}
        
        for event, elem in context:
            tag = elem.tag

            if event == "start" and tag == "DOC":
                current_doc = {}

            elif event == "end":
                if tag == "DOC":
                    yield current_doc
                    elem.clear()  # Free up memory
                elif tag in ["DOCNO", "PROFILE", "DATE", "HEADLINE", "BYLINE", "DATELINE", "TEXT", "PUB", "PAGE"]:
                    current_doc[tag] = elem.text.strip() if elem.text else ""
                elem.clear()
                
                
    
if __name__ == "__main__":
    pass