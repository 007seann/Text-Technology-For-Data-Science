import os
import sys
import math
import logging
import pickle
from pathlib import Path
from Crawler import Crawler
from Tokeniser import Tokeniser
from nltk.stem import PorterStemmer
from PostingLinkedList import PostingLinkedList

util_dir = Path(os.path.join(os.path.dirname(__file__))).parent.joinpath('utils')
sys.path.append(str(util_dir))

from AppConfig import AppConfig
config = AppConfig()

INDEX_SAVE_PATH = config.get('indexer', 'index_save_path', True)
CRAWL_CACHE_PATH = config.get('indexer', 'crawler_cache_path', True)
INDEX_BASE_DIR = config.get('indexer', 'index_base_dir', True)
POSITIONAL_INDEX_LOG_PATH = config.get('indexer', 'positional_index_log', True)
POSITIONAL_INDEX_CACHE_PATH = config.get('indexer', 'positional_index_cache', True)
STOPWORDS = config.get('indexer', 'stop_words', True)

class PositionalIndex:
    logging.basicConfig(filename=POSITIONAL_INDEX_LOG_PATH, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    def __init__(self, load_from_cache=True):   
        self.logger = logging.getLogger(self.__class__.__name__) 
                
        # Stemming and Tokenisation utils
        self.stemmer = PorterStemmer() # TODO
        self.tokeniser = Tokeniser() #TODO
        self.crawler = Crawler(INDEX_BASE_DIR, CRAWL_CACHE_PATH)
        
        self.enable_stemming = False
        # In memory data
        self.url_to_docid = {} # {url: docId}
        self.docid_to_url = {} # {docId: url}
        self.index = {}
        self.document_ids = set()
        self.vocabulary = set()
        self.vocabulary_size = 0
        self.headline_index = {}
        
        # Initialise index
        cache_exists = os.path.exists(POSITIONAL_INDEX_CACHE_PATH)
        if load_from_cache and cache_exists:
            self.logger.info("Loading index from cache.")
            self.load_from_file()
        else:
            self.logger.info("Building index from scratch.")
            self.build_index()
            
    def build_index(self):
        """
        Builds the positional index by crawling the web pages, extracting documents, and inserting them into the index.

        Raises:
            Exception: If no files are found in the base directories.

        """
        self.crawler.load_cache()
        crawler_url_cache = self.crawler.cache # {url: checksum}
        if not crawler_url_cache:
            self.logger.info("No files found in the base directories.")
            raise Exception("No files found in the base directories.")
        for file_path, checksum in crawler_url_cache.items():
            if file_path not in self.url_to_docid:
                self.logger.info(f"Processing file: {file_path}")

                self.url_to_docid[file_path] = len(self.url_to_docid)
                self.docid_to_url[len(self.url_to_docid)-1] = file_path
                doc_dict = self.crawler.html_to_dict(file_path, self.url_to_docid[file_path])
                self.insert_document(doc_dict)
        self.logger.info("Index built successfully.")
        self.save_to_file()
        self.load_from_file()
    
    def reload_index(self):
        """
        Reloads the index by crawling new pages, updating the document ID mapping,
        and inserting the documents into the index.

        This method performs the following steps:
        1. Calls the `crawl` method of the crawler object to crawl new pages.
        2. Retrieves the paths of the new pages using the `get_new_files` method of the crawler object.
        3. Updates the document ID mapping by assigning a unique ID to each new page.
        4. Converts the HTML content of each new page to a dictionary representation using the `html_to_dict` method of the crawler object.
        5. Inserts the document into the index using the `insert_document` method.

        Note: This method assumes that the `crawler` object and the `url_to_docid` dictionary are already initialized.

        Parameters:
        None

        Returns:
        None
        """
        self.crawler.crawl()
        new_pages = self.crawler.get_new_files(clear_queue=True)
        for file_path in new_pages:
            self.url_to_docid[file_path] = len(self.url_to_docid)
            self.docid_to_url[len(self.url_to_docid)] = file_path
            doc_dict = self.crawler.html_to_dict(file_path, self.url_to_docid[file_path])            
            self.insert_document(doc_dict) 
        
    
    def insert_document(self, document_dict, include_subsections=False):
        doc_id = document_dict.get("DOCNO")
        # Document has already been added. 
        if doc_id in self.document_ids:
            return
        
        # We collapse document into two sections
        merged_text = document_dict.get("HEADLINE", "") + " " + document_dict.get("TEXT", "")
        headline = document_dict.get('HEADLINE', "")
        # Used if we need do to read any other subsections
        if include_subsections:
            for tag in ["PROFILE", "DATE", "BYLINE", "DATELINE", "PUB", "PAGE"]:
                merged_text += document_dict.get(tag, "")

        ## Building Extent Index. { (headline) : {docId: spans} }, where a headline of an article is stemmed and does not include stopwords as well as an article.
        headline_token_stream = self.tokeniser.tokenise(headline)
        token_stream = self.tokeniser.tokenise(merged_text)
        
        stopwords = self.tokeniser._get_stop_words()

        token_stream_without_stopwords = [token for token in token_stream if token not in stopwords]
        stemmed_tokens = []
        headline_token_stream_without_stopwords = [token for token in headline_token_stream if token not in stopwords]
        stemmed_headline_tokens = []
        headline = []
        
        for token in token_stream_without_stopwords:
            stemmed_token = self.stemmer.stem(token) if self.enable_stemming else token
            stemmed_tokens.append(stemmed_token)
        
        for token in headline_token_stream_without_stopwords:
            stemmed_headline_token = self.stemmer.stem(token) if self.enable_stemming else token
            stemmed_headline_tokens.append(stemmed_headline_token)
            headline.append(stemmed_headline_token)

        span = [] # This is the span of the article headline position. i.e. span =[0,1,2] means the headline position span is from 0 to 2 of the headline-text-merged article.
        for index, token in enumerate(stemmed_tokens):
            for h_index, h_token in enumerate(stemmed_headline_tokens):
                if token == h_token:
                    span.append(index)
                    del stemmed_headline_tokens[h_index]
                    break
                        
        self.headline_index[tuple(headline)] = {doc_id: span}
    
        ## Mapping between token {term : PostingLinkedList}
        term_posting_mapping = {}
        token_index = 0
        token_stream = self.tokeniser.tokenise(merged_text)
        
        for token in token_stream:
            
            stemmed_token = self.stemmer.stem(token) if self.enable_stemming else token
            
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
    
    def extract_tokens(self, query):
        # modified to address stemming only.
        if self.enable_stemming:
            return [self.stemmer.stem(token) for token in self.tokeniser.tokenise(query)]
        else:
            return [token for token in self.tokeniser.tokenise(query)]
    
    def save_to_file(self, filename=POSITIONAL_INDEX_CACHE_PATH):
        data = {
            'url_to_docid': self.url_to_docid,
            'docid_to_url': self.docid_to_url,
            'index': self.index,
            'document_ids': self.document_ids,
            'vocabulary': self.vocabulary,
            'vocabulary_size': self.vocabulary_size,
            'headline_index': self.headline_index
        }
        with open(filename, 'wb') as file:
            pickle.dump(data, file)
        self.logger.info(f'Index saved to {filename}')

    def load_from_file(self, filename=POSITIONAL_INDEX_CACHE_PATH):
        try:
            with open(filename, 'rb') as file:
                data = pickle.load(file)
            self.url_to_docid = data['url_to_docid']
            self.docid_to_url = data['docid_to_url']
            self.index = data['index']
            self.document_ids = data['document_ids']
            self.vocabulary = data['vocabulary']
            self.vocabulary_size = data['vocabulary_size']
            self.headline_index = data['headline_index']
            self.logger.info(f'Index loaded from {filename}')
        except FileNotFoundError:
            self.logger.error(f'File {filename} not found. Building index from scratch.')
            self.build_index()
        
        # Cache could have been created remotely. Stored document paths may still point to remote files when 
        # working locally. Need to update to make them work locally. 
        if config.get("run_config", "dev") == "True":
            self.logger.info("Setting local development environment")
            self.logger.info("Updating cache paths to local paths.")
            new_url_to_docid = {}
            new_docid_to_url = {}
            for key, value in self.url_to_docid.items():
                new_url_to_docid[config.get('server', 'collection_path') + key.split('collection')[1]] = value
                new_docid_to_url[value] = config.get('server', 'collection_path') + key.split('collection')[1]
            self.url_to_docid = new_url_to_docid
            self.docid_to_url = new_docid_to_url
            
    def search_and(self, search_query, include_positions=False):
        tokenised_terms = self.extract_tokens(search_query)
        if not tokenised_terms:
            return set()  # Return an empty set if there are no terms
    
        # Initialize the result_set with the documents of the first term
        doc_freq, doc_dict = self.index.get(tokenised_terms[0], (0, {}))
        document_set, posting_cache = set(doc_dict.keys()), {}
        posting_cache.update(doc_dict)

        # Intersect the document_set with the documents of the other terms
        for term in tokenised_terms[1:]:
            _, doc_dict = self.index.get(term, (0, {}))
            document_set.intersection_update(doc_dict.keys())

            term_posting_mapping = {doc_id: posting for doc_id, posting in doc_dict.items()}

            docs_to_remove = set()
            for doc in document_set:
                posting_cache[doc] = posting_cache[doc].intersect(term_posting_mapping[doc])
                if not posting_cache[doc]:
                    docs_to_remove.add(doc)

            document_set.difference_update(docs_to_remove)

            if not document_set:
                return set()  # Early exit if no documents match
            
        if not include_positions:
            return document_set
            
        return [(doc, posting_cache[doc].toList()) for doc in document_set]

    def search_not(self, search_query):
        excluded_set = set()
        tokenised_terms = self.extract_tokens(search_query)

        if not tokenised_terms:
            return self.document_ids  # Return all docs if no terms left.
        
        for token in tokenised_terms:
            doc_freq, doc_dict = self.index.get(token, (0, {}))
            excluded_set.update(doc_dict.keys())

        return self.document_ids - excluded_set
    
    def search_phrase(self, search_query, include_positions=False):
        document_set, posting_cache = set(), {}
        search_term_index = 0
        tokenised_terms = self.extract_tokens(search_query)
        if not tokenised_terms:
            return set()  # Return an empty list if there are no terms

        for tokenised_term in tokenised_terms:
            doc_freq, doc_dict = self.index[tokenised_term]

            if search_term_index == 0:
                document_set.update(doc_dict.keys())
                posting_cache.update(doc_dict)
                search_term_index += 1
            else:
                term_document_list = {doc_id for doc_id, posting in doc_dict.items()}
                term_posting_mapping = {doc_id: posting.decrement_postings(search_term_index) for doc_id, posting in doc_dict.items()}
                document_set.intersection_update(term_document_list)
                
                if not document_set:
                    return set()
                
                # Intersect current doc postings with postings in our cache
                docs_to_remove = set()
                for doc in document_set:
                    posting_cache[doc] = posting_cache[doc].intersect(term_posting_mapping[doc])
                    if not posting_cache[doc]:
                        docs_to_remove.add(doc)
                
                document_set.difference_update(docs_to_remove)
                search_term_index += 1
                
        # alternate version for debugging
        if not include_positions:
            return document_set
        
        return [(doc, posting_cache[doc].toList()) for doc in document_set]

    def search_proximity(self, search_query, proximity, include_positions=False):
        tokenised_terms = self.extract_tokens(search_query)
        if not tokenised_terms:
            return set()  # Return an empty set if there are no terms
        
        result = []

        # Get the posting lists for all terms
        posting_dicts = [self.index.get(term, (0, {}))[1] for term in tokenised_terms]

        # Get the set of documents that contain all terms (like an AND search)
        common_doc_ids = set.intersection(*[set(posting_dict.keys()) for posting_dict in posting_dicts])

        for doc_id in common_doc_ids:
            postings = [posting_dict[doc_id] for posting_dict in posting_dicts]
            if self.check_proximity(postings, proximity):
                result.append(doc_id)
        
        if not include_positions:
            return set(result)

        return [(doc, posting_dicts[doc].toList()) for doc in result]
    
    def check_proximity(self, postings, proximity):
        # Initialize pointers to the head of each postings linked list
        pointers = [posting.head for posting in postings]

        while all(pointer for pointer in pointers):
            # Find the minimum and maximum positions in the current window
            min_pos = min(pointer.value for pointer in pointers if pointer)
            max_pos = max(pointer.value for pointer in pointers if pointer)

            # Check if the terms are within the specified proximity
            if max_pos - min_pos <= proximity:
                return True

            # Slide the window: move the pointer of the term with the smallest position
            for i in range(len(pointers)):
                if pointers[i] and pointers[i].value == min_pos:
                    pointers[i] = pointers[i].next
                    break

        return False
    
    def calculate_tf_idf(self, term_freq, doc_freq):
        return (1 + math.log10(term_freq)) * math.log10((len(self.document_ids)) / doc_freq)
    
    def ranked_retrieval(self, search_query):
        document_score_map = {}
        
        # conditional filtering modified to cater for stemming.
        tokenised_terms = self.extract_tokens(search_query)

        if not tokenised_terms:
            return []  # Return an empty list if there are no terms
    
        # Calculate tfidf scores for each.
        for term in tokenised_terms:
            if term in self.index:
                doc_freq, doc_dict = self.index[term]
                
                # Calculate a score for each dic in this result and update our dictionary.
                for doc_id in doc_dict:
                    term_freq = doc_dict[doc_id].length
                    score = self.calculate_tf_idf(term_freq, doc_freq)
                    current_score = document_score_map.get(doc_id, 0)
                    document_score_map[doc_id] = score + current_score
        
        # Directly sort the dictionary items based on the scores.
        sorted_document_scores = sorted(document_score_map.items(), key=lambda x: x[1], reverse=True)
        return [(doc, round(score, 4)) for doc, score in sorted_document_scores][:150]
    
    def _get_docs_and_positions(self, set_a_results, set_b_results, mode):
        set_a_docs = {doc for doc, _ in set_a_results}
        set_b_docs = {doc for doc, _ in set_b_results}
        set_a_postings = {doc: posting for doc, posting in set_a_results if doc in set_a_docs}
        set_b_postings = {doc: posting for doc, posting in set_b_results if doc in set_b_docs}

        result_dict = []

        # Find the intersection of document IDs
        common_doc_ids = {}
        if mode == 'AND':
            common_doc_ids = set_a_docs.intersection(set_b_docs)
        elif mode == 'OR':
            common_doc_ids = set_a_docs.union(set_b_docs)
        
        # Iterate through common document IDs
        for doc_id in common_doc_ids:
            # Concatenate the positions lists
            concatenated_positions = []
            if doc_id in set_a_postings:
                concatenated_positions += set_a_postings[doc_id]
            if doc_id in set_b_postings:
                concatenated_positions += set_b_postings[doc_id]
            # Update the result dictionary
            result_dict.append((doc_id, concatenated_positions))
            
        # [(doc_id, [pos1, pos2, ...]), ...]
        return result_dict

    def process_query(self, query):
        query = query.strip()
        if ' AND NOT ' in query:
            terms = query.split(' AND NOT ')
            positive_results = self.process_query(terms[0])
            negative_results = self.process_query(terms[1])
            
            return positive_results.difference(negative_results)

        elif ' OR NOT ' in query:
            terms = query.split(' OR ', 1)
            positive_results = self.process_query(terms[0])
            not_negative_results = self.process_query(terms[1])

            return positive_results.union(not_negative_results)
        
        elif ' AND ' in query:
            terms = query.split(' AND ', 1)
            set_a_results = self.process_query(terms[0])
            set_b_results = self.process_query(terms[1])
            doc_pos_result = self._get_docs_and_positions(set_a_results, set_b_results, 'AND')
            
            return doc_pos_result

        elif ' OR ' in query:
            terms = query.split(' OR ', 1)
            set_a_results = self.process_query(terms[0])
            set_b_results = self.process_query(terms[1])
            doc_pos_result = self._get_docs_and_positions(set_a_results, set_b_results, 'OR')

            return doc_pos_result
        
        elif query.startswith('NOT '):
            query = query.replace('NOT ', '')
            res = self.search_not(query)

            return res
        
        elif query.startswith('#'):
            try:
                proximity_end_index = query.index('(')
                proximity_value = int(query[1:proximity_end_index])
                terms = query[proximity_end_index + 1: -1]
                terms = ' '.join(terms.split(', '))
                res = self.search_proximity(terms, proximity_value)
                return res
            except ValueError:
                return "Error: Proximity value must be an integer."

        elif '\"' in query:
            phrase = query.replace('"', '')
            return self.search_phrase(phrase, include_positions=True)
        else:
            return self.search_and(query, include_positions=True)

