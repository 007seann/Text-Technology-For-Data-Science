import subprocess
from nltk.stem import PorterStemmer
import xml.etree.ElementTree as ET
from collections import defaultdict
import re
import copy
import math
stemmer = PorterStemmer()


### Open documents and query ###
## Please change directories corresponding to the location of your files stored ##

FILENAME = "trec.5000"
STOPWORD_FILENAME = "englishST"

input_file = f"./test/{FILENAME}.xml"
# input_file = f"./input-file/collections/{FILENAME}.xml"
stopword_file = f"./input-file/{STOPWORD_FILENAME}.txt"
output_directory = "./output-file"
output_file_tokenised = f"{output_directory}/{FILENAME}_tokenised.xml"
output_file_stopping = f"{output_directory}/{FILENAME}_stopping.xml"
output_file_stemmed =  f"{output_directory}/{FILENAME}_stemmed.xml"

# Test
queries_boolean_test = "queries.boolean.txt" 
queries_boolean_test_file = f"/Users/apple/Library/Mobile Documents/com~apple~CloudDocs/Year 3/Final-Project/0 Modules/TTDS/Lab/test/{queries_boolean_test}"
queries_rankedIR_test = "queries.ranked.txt"
# queries_rankedIR_test = "queries.ranked.sample.txt"
queries_rankedIR_test_file = f"/Users/apple/Library/Mobile Documents/com~apple~CloudDocs/Year 3/Final-Project/0 Modules/TTDS/Lab/test/{queries_rankedIR_test}"


with open(file = queries_boolean_test_file, mode = "r") as file:
  boolean_queries = file.read().splitlines() 

with open(file = queries_rankedIR_test_file, mode = 'r') as file:
  rankedIR_queries = file.read().splitlines()

with open(file=stopword_file, mode = "r") as stopwords_file:
    stopwords = set(stopwords_file.read().split())
    
    
    
### Indexting - A Positional Inverted Index ###

term_sequences = defaultdict(list)
with open(file=input_file, mode='r') as file:
  document = file.read()
  # Use regular expression to find all text inside each tags in xml format
  docnos = re.findall(r'<DOCNO>\s*(.*?)\s*</DOCNO>', document, re.DOTALL) 
  headlines = re.findall(r'<HEADLINE>\s*(.*?)\s*</HEADLINE>', document, re.DOTALL) 
  texts = re.findall(r'<TEXT>\s*(.*?)\s*</TEXT>', document, re.DOTALL) 
  for docno, headline, text in zip(docnos, headlines, texts):  
    headline_text = []
    headline_text.append(headline + " " + text)
    # Tokenisation
    doc_all_text = ' '.join(headline_text).lower()
    doc_all_text = ''.join([char if char.isalpha() or char.isspace() else ' ' for char in doc_all_text])
    tokens = list(doc_all_text.split())
    # Stopping
    stopped_tokens = [token for token in tokens if token not in stopwords]
    # Stemming
    stemmed_tokens = [stemmer.stem(token) for token in stopped_tokens]
    for position, token in enumerate(stemmed_tokens):
      if docno not in term_sequences[token]:
        term_sequences[token].append((docno, position+1))

# Sorted inverted index
sorted_data = dict(sorted(term_sequences.items()))

def index_format(data):
  """
  Format a positional inverted index into a given format
  
  Args:
      data (defaultdict(list)): the inverted index

  Returns:
      terms:df
        docID: pos1, pos2, ...
        docID: pos1, pos2, ...
  """
  formatted_data = ""
  for term, pairs in data.items():
    doc_positions = {}
    for doc_id, position in pairs:
      if doc_id not in doc_positions:
        doc_positions[doc_id] = []
      doc_positions[doc_id].append(position)
    frequency = 0
    for doc_id, positions in doc_positions.items():
      frequency += 1
    formatted_data += f"{term}:{frequency}\n"
    for doc_id, positions in doc_positions.items():
      formatted_data += f"\t{doc_id}: {','.join(map(str, positions))}\n"
  return formatted_data

formatted_text = index_format(sorted_data)

# Save to index.txt
with open(file = 'index.txt', mode = 'w') as file:
  file.write(formatted_text)



### Search Engine(a boolean, phrase, proximity search) ###
class SearchEngine:
  """

  """
  def __init__(self) -> None:
    self.inverted_index = {}
    
  def load_index(self, index_file):
    """
    Load an inverted index into memory. 
    index_format:
      { term1: [(docID1, pos25), (docID2, pos75)],
        term2: [(docID1, pos1), (docID6, pos12)], 
        ...}

    Args:
        index_file (defaultdict(list)): a positional inverted index
    """
    self.inverted_index = index_file
  
  def parse_query(self, query):
    """ 
    The function seperate the number and the text from input query,
    and save to the dictionary. 
    Key is query number, Values are a list of terms

    Args:
        query (string): See example
        For instance,  8 "Financial times" AND NOT BBC
    Returns:
        dict: See example
        For instance, {8: ['Financial times', 'NOT BBC']}
    """
    # Initialize an empty dictionary to store the output
    output = {}
    # Seperate the number and the text
    match = re.match(r'^(\d+) (.+)', query)
    if match:
        number = int(match.group(1))
        text = match.group(2)
        # Split the text by " AND " and remove any double quotes
        text_list = [item for item in text.split(' AND ')]
        output[number] = text_list

    return output 
  
  def query_term_preprocessing(self, term):
    term = ''.join([char if char.isalpha() or char.isspace() else '' for char in term]) 
    term = term.lower()
    term = stemmer.stem(term)
    if term not in stopwords:
      return term
  
  def boolean_normal_search(self, term):
    """
    The function returns a list of documents term appeared

    Args:
        term (string): a token from a input query

    Returns:
        list : a list of docIDs appears in documents 
    """
    if 'NOT' in term:
      negation_term = term.split()
      term = self.query_term_preprocessing(negation_term[1])
      term_index = {}
      entire_index = copy.deepcopy(self.inverted_index)
      term_index[term] = self.inverted_index[term]
      result_dict = {}
      
      # Getting the inverted index of execluding documents which posses the term
      for key in entire_index:
        if key in term_index:
          result_values = [posting for posting in entire_index[key] if posting not in term_index[key]]
          # Only add the key if there are values remaining after subtraction
          if result_values:
            result_dict[key] = result_values
        else:
          result_dict[key] = entire_index[key]

      # Getting all document IDs execluding documents which posses the term
      unique_docIDs = set()
      for term, postings_list in result_dict.items():
        for posting in postings_list:
          docID, _ = posting
          if docID not in unique_docIDs:
            unique_docIDs.add(docID)

      return list(unique_docIDs)
              
    term = self.query_term_preprocessing(term)

    if term in self.inverted_index:
      postings = self.inverted_index[term]
      unique_docIDs = []
      for posting in postings:
        docID, _ = posting
        if docID not in unique_docIDs:
          unique_docIDs.append(docID)

      return unique_docIDs
      
  def phrase_search(self, term):
    """
    The function returns a list of all document IDs corresponding to having the phrase in the index

    Args:
        term (string): a token from a input query

    Returns:
        list: a list of all document IDs corresponding to having the phrase in the index

    """
    phrase = term.split()
    phrase = [term.strip('"') for term in phrase]
    phrase = [self.query_term_preprocessing(term) for term in phrase]
    postings = []    
    first_term_postings = self.inverted_index[phrase[0]]
    second_term_postings = self.inverted_index[phrase[1]]
      
    for docID, pos in first_term_postings:
      for docID2, pos2 in second_term_postings:
        if docID == docID2 and pos + 1 == pos2:
          postings.append((docID, pos))
    
    docIDs = list(set([docID for docID, pos in postings]))

    return sorted(docIDs)

  
  def proximity_search(self, term):
    """
    The function returns a list of all document IDs satisfying the proximity distance from the inverted index. 

    Args:
        term (string): a token from a input query

    Returns:
        list: a list of all document IDs satisfying the proximity distance from the inverted index. 
    """
    term_parsed = re.findall(r'\b\w+\b', term)
    proximity = int(term_parsed[0])
    term_parsed = [self.query_term_preprocessing(term) for term in term_parsed]
    postings = []    
    first_term_postings = self.inverted_index[term_parsed[1]]
    second_term_postings = self.inverted_index[term_parsed[2]]
    
    for docID, pos in first_term_postings:
      for docID2, pos2 in second_term_postings:
        if docID == docID2 and abs(pos - pos2) <= proximity:
          postings.append((docID, pos))
        
    docIDs = list(set([docID for docID, pos in postings]))
    return sorted(docIDs)
  
  
  def search(self, term):

    if '\"' in term:
      return self.phrase_search(term)

    if "#" in term:
      return self.proximity_search(term)
      
    else:
      return self.boolean_normal_search(term)

  
  def boolean_search(self, query):
    result = defaultdict(list)
    query_number = 0
    query_parsed = self.parse_query(query)
    docIDs = []
    temp = []
    for query_num, terms in query_parsed.items():
      query_number = query_num
      if 'AND' in query:
        query_parsed[query_num].append('AND')
      
      for term in terms:
        if len(terms) == 1:
          temp.append(self.search(term))
          break
        if 'AND' in terms and term != 'AND':
          temp.append(self.search(term))
        elif 'OR' in terms and term != 'OR':
          temp.append(self.search(term))
        else:
          break
    
    # Uncommented them after search functions done
    if len(temp) == 1:
      docIDs = temp[0]
    if len(temp) == 2:
      docIDs = list(set(temp[0]).intersection(temp[1]))
      
    result[query_number] = (docIDs)

    return result

  def boolean_search_format(self, data, filename):
    """_summary_

    Args:
        data (dafaultdict(list)): 
          {query_num: [docID1, docID2, ...]}
    Returns:
        _type_: _description_
    """
    with open(filename, 'w') as f:
      for query_num, docIDs in data.items():
        for docID in docIDs:
          f.write(f"{query_num},{docID}\n")



### RankedIR Search ###
class RankedIR:


  def __init__(self):
    self.inverted_index = {}
    self.N = len(docnos) # N is the number of documents in a collection 
    self.frequency_index = {}
    
  def index_load(self, data):
    self.inverted_index = data
  
  def query_term_preprocessing(self, term):
    term = ''.join([char if char.isalpha() or char.isspace() else '' for char in term])
    term = term.lower()
    term = stemmer.stem(term)
    if term not in stopwords:
      return term
    
  def parse_query(self, query):
    output = {}
    # Seperate the number and the text
    match = re.match(r'^(\d+) (.+)', query)
    if match:
        number = int(match.group(1))
        text = match.group(2)
        text_list = [item for item in text.split()]
        output[number] = text_list
        
    return output
  
  def df(self, term) -> int: 
    """
    Calculate the number of documents term appered in 

    Args:
        term (string): a single token from the query.
        
    Returns:
        int : the number of documents term appered in
    """
    docIDs = set()
    postings = self.inverted_index[term]
    for posting in postings:
      docID, _ = posting
      docIDs.add(docID)
      
    return len(docIDs)
  
  def tf(self, term, docID):
    """
    Count the number of docID for term based on the inverted index

    Args:
        term (string): a single token from the query.
        docID (string): a document ID 

    Returns:
        _type_: a single token from the query.
    """
    # Count the number of docID for term based on the inverted index
    return sum(1 for doc, _ in self.inverted_index[term] if doc == docID)
  
  def set_frequency_index(self):
    for term, postings in self.inverted_index.items():

      # # Create a set of unique docIDs for the term
      unique_docIDs = set(doc for doc, _ in postings)

      # For each unique docID, get the term frequency
      new_values = [(docID, self.tf(term, docID)) for docID in unique_docIDs]
      self.frequency_index[term] = new_values
    
  def query_documents(self, terms) -> list:
    """
    Returns a list of documents all terms of a query, which appear in 

    Args:
        terms (list): a list of terms 

    Returns:
        list: the common documents in which all terms in a query are included. 
    """
    
    docIDs = set()
    for term in terms:
      postings = self.inverted_index[term]
      for posting in postings:
        docID, _ = posting
        docIDs.add(docID)
        
    return list(docIDs)
  
  def rankedIR_search(self, query):
    result = defaultdict(list)
    query_number = 0
    query_parsed = self.parse_query(query)
    for query_num, terms in query_parsed.items():
      query_number = query_num
      terms = [self.query_term_preprocessing(term) for term in terms]
      terms = list(filter(None, terms))
      docIDs = self.query_documents(terms)
      for docID in docIDs:
        result[query_number].append((docID, self.score(terms, docID)))
    return result
  
  def score(self, terms:list , docID:str) -> float:
    score_sum = 0
    for term in terms:
      score_sum += self.weight_term(term, docID)
    return round(score_sum, 4)
  
  def weight_term(self, term, docID) -> float:
    tf = self.tf(term, docID)
    df = self.df(term)
    if tf != 0:
      return (1 + math.log10(tf)) * math.log10(self.N / df)
    else:
      return 0
    
  def do_format(self, data, filename):
    with open(filename, "w") as f:
      for query_num, docIDs in data.items():
        for docID, score in docIDs:
          f.write(f"{query_num},{docID},{score}\n")
  
  def tweak_data(self, data):  
    for term, postings in data.items():
      sorted_postings = sorted(postings, key=lambda x: x[1], reverse = True)
      if len(postings) >= 150:
        data[term] = sorted_postings[:150]
      else:
        data[term] = sorted_postings
        
    return data
  
  
### Run ###
search_engine = SearchEngine()
search_engine.load_index(sorted_data)
boolean_search_dict = {}
for query in boolean_queries:
  # Skip empty lines
  if not query:
    break
  result = search_engine.boolean_search(query)
  boolean_search_dict.update(result)
  search_engine.boolean_search_format(boolean_search_dict, 'results.boolean.txt')

rankedIR = RankedIR()
rankedIR.index_load(sorted_data)
rankedIR.set_frequency_index()
rankedIR_queries_dict = {}
for query in rankedIR_queries:
  # Skip empty lines
  if not query:
    break
  result = rankedIR.rankedIR_search(query)
  result = rankedIR.tweak_data(result)
  rankedIR_queries_dict.update(result)
rankedIR.do_format(rankedIR_queries_dict, 'results.ranked.txt')
  
# total : 80 seconds

