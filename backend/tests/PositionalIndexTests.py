import unittest
import time
from PositionalIndex import PositionalIndex, XMLDocParser 

class TestPositionalIndex(unittest.TestCase):
    
    source_file = "../../exploration/selected_news_articles.xml"
    
    @classmethod
    def setUpClass(cls):
        cls.p = PositionalIndex()

    def test_01_create_index(self):
        print("\n------------------ Creating Index ------------------")
        start_time = time.time()
        document_count = 0
        xml_parser = XMLDocParser(TestPositionalIndex.source_file)
        for doc_text, meta_data in xml_parser.stream_docs():
            TestPositionalIndex.p.insert_document(doc_text, meta_data)
            document_count += 1
        end_time = time.time()
        print(f"Time taken to index {document_count} documents: {end_time - start_time} seconds")

    def test_02_load_index(self):
        print("\n------------------ Loading Index ------------------")
        start_time = time.time()
        TestPositionalIndex.p.load_index()
        load_time = time.time() - start_time
        print(f"Loading index took {load_time} seconds")

    def test_and_query(self):
        print("\n------------------ AND Queries ------------------")
        queries = ["work AND community", "work AND NOT community", "work AND NOT industry AND times"]
        for query in queries:
            with self.subTest(query=query):
                start_time = time.time()
                result = TestPositionalIndex.p.process_query(query)
                query_time = time.time() - start_time
                print(f"AND Query: '{query}' ({len(query.split())} terms) \ntook {query_time} seconds. \nResults: {result}\n")

    def test_or_query(self):
        print("\n------------------ OR Queries ------------------")
        queries = ["year OR previous", "year OR NOT previous", "year OR NOT previous OR democracy"]
        for query in queries:
            start_time = time.time()
            result = TestPositionalIndex.p.process_query(query)
            query_time = time.time() - start_time
            print(f"OR Query: '{query}' ({len(query.split())} terms) \ntook {query_time} seconds. \nResults: {result}\n")

    def test_not_query(self):
        print("\n------------------ NOT Queries ------------------")
        queries = ["NOT today", "NOT today NOT evidence"]
        for query in queries:
            start_time = time.time()
            result = TestPositionalIndex.p.process_query(query)
            query_time = time.time() - start_time
            print(f"NOT Query: '{query}' ({len(query.split())} terms) \ntook {query_time} seconds. \nResults: {result}\n")

    def test_phrase_query(self):
        print("\n------------------ Phrase Queries ------------------")
        queries = ["\"that the\"", "\"that the backing\"", "\"What seems to have happened in recent years is that an increasing number of large companies have appreciated the benefits of community involvement. But this has not filtered down sufficiently to smaller companies, who wonder whether they have the resources to act effectively enough.\""]
        for query in queries:
            start_time = time.time()
            result = TestPositionalIndex.p.process_query(query)
            query_time = time.time() - start_time
            print(f"Phrase Query: '{query}' ({len(query.split())} terms) \ntook {query_time} seconds. \nResults: {result}\n")

    def test_proximity_query(self):
        print("\n------------------ Proximity Queries ------------------")
        queries = ["#2(year, has)", "#10(year, commission)", "#50(year, commission)"]
        for query in queries:
            start_time = time.time()
            result = TestPositionalIndex.p.process_query(query)
            query_time = time.time() - start_time
            print(f"Proximity Query: '{query}' ({len(query.split())} terms) \ntook {query_time} seconds. \nResults: {result}\n")

if __name__ == '__main__':
    unittest.main()
