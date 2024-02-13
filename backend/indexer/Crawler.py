import os
import time
import pickle
import hashlib
import logging
from bs4 import BeautifulSoup

CRAWL_CACHE_PATH = os.path.join(os.path.dirname(__file__), '../utils/url_cache.pkl')
SOURCE_FILE_EXTENSION = '.html'

class Crawler:
    def __init__(self, base_directories, cache_file=CRAWL_CACHE_PATH):
        self.base_directories = base_directories if isinstance(base_directories, list) else [base_directories]
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.cache_file = cache_file
        self.updated_stack = []  # Stack to track updated files
        self.cache = {}

    def crawl(self):
            """
            Crawls through the base directories and updates the cache with new or modified files.

            Args:
                rebuild (bool, optional): If True, rebuilds the cache from scratch. Defaults to False.

            Raises:
                Exception: If no files are found in the base directories.

            """
            index_changed = False
            for base_directory in self.base_directories:
                for root, _, files in os.walk(base_directory):
                    for file in files:
                        if not file.endswith(SOURCE_FILE_EXTENSION):
                            continue
                        file_path = os.path.join(root, file)  # Treat file_path as URL
                        checksum = self.get_check_sum(file_path)
                        # Check if the file is new or has been modified
                        if file_path not in self.cache or self.cache[file_path] != checksum:
                            index_changed = True
                            self.updated_stack.append(file_path)
                            self.cache[file_path] = checksum  # Update cache with new checksum
            if not self.cache:
                self.logger.info("No files found in the base directories.")
                raise Exception("No files found in the base directories.")
            if index_changed:
                
                self.logger.info("Index changed, updating cache...")
                self.logger.info(f"Current cache size: {len(self.cache)}")
                self.logger.info(f"Updated files size: {len(self.updated_stack)}")
                
                self.save_cache()
        
        
    def get_check_sum(self, file_path, algorithm='sha256'):
            """
            Calculate the checksum of a file using the sha256 algorithm.

            Parameters:
            - file_path (str): The path to the file.
            - algorithm (str): The hashing algorithm to use (default is 'sha256').

            Returns:
            - str: The checksum of the file.
            """
            hash_func = getattr(hashlib, algorithm)()
            with open(file_path, 'rb') as file:
                while chunk := file.read(4096):
                    hash_func.update(chunk)
            return hash_func.hexdigest()

    def load_cache(self):
        try:
            with open(self.cache_file, 'rb') as file:
                self.logger.info(f"Loading cache from {self.cache_file}")
                self.cache = pickle.load(file)
                self.crawl()  # Update the cache with new or modified files
                new_files = self.get_new_files()
                self.logger.info(f"New files: {new_files}")
                self.logger.info(f"Found {len(new_files)} new or modified files.")
                
                
        except (FileNotFoundError, EOFError) as e:
            self.logger.info(f"Cache file not found or is empty, creating new cache. Error: {e}")
            self.cache = {}
            self.crawl()  # Populate self.cache with fresh data


    def save_cache(self):
        # Back up the old cache file
        if os.path.exists(self.cache_file):
            backup_path = "{}.{}".format(self.cache_file, time.strftime("%Y%m%d-%H%M%S"))
            os.rename(self.cache_file, backup_path)
            self.logger.info(f"Backed up old cache to {backup_path}")
        
        with open(self.cache_file, 'wb') as file:
            self.logger.info(f"Saving cache to {self.cache_file}")
            pickle.dump(self.cache, file)


    def get_new_files(self, clear_queue=False):
        """
        Returns a list of updated files and optionally clears the stack.

        Parameters:
        - clear_queue (bool): If True, clears the stack of updated files.

        Returns:
        - list: A list of updated files.

        """
        updated_files = list(self.updated_stack)  # Copy the stack
        clear_queue and self.updated_stack.clear()  # Clear the stack if clear_queue is True
        return updated_files
        
    def html_to_dict(self, html_path, doc_id):
        with open(html_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        
        # Initialize the dictionary with DOCNO
        doc_dict = {"DOCNO": str(doc_id)}
        
        # Define mappings for HTML tags to dict keys. Can similarly add any future additions
        mappings = [('h1', 'HEADLINE'), ('p', 'TEXT')]
        
        for html_tag, dict_key in mappings:
            content = ' '.join([elem.get_text(strip=True) for elem in soup.find_all(html_tag)])
            if content:
                doc_dict[dict_key] = content
        return doc_dict