import sys
sys.path.append('../backend/indexer')
from indexer.PositionalIndex import PositionalIndex
from faker import Faker
import requests
import BeautifulSoup
from dataclasses import dataclass

class SearchRetriever:

    @dataclass
    class ResultCard:
        title: str
        url: str
        image: str
        date: str
        publisher: str
        sentiment: float
        bold_token: int

    def __init__(self):
        self.index = PositionalIndex()
        self.index.load_index('../backend/database/index/index_base.txt')
        self.faker = Faker()

    def get_news(doc_id):
        url = "http://ttds.martinnn.com:5002/api/news/{}".format(doc_id)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    
    def _search(self, query):
        doc_positions_list = self.index.process_query(query)
        return doc_positions_list
    
    def get_results(self, query):
        result_cards = []
        doc_positions_list = self._search(query)
        for doc_id, positions in doc_positions_list:
            card = self.ResultCard(title="Title",
                                    url=self.faker.url(),
                                    image=self.faker.image_url(width=50, height=50),
                                    date="Date", 
                                    publisher="Publisher",
                                    sentiment=0.0,
                                    bold_token=0)
            result_cards.append(card)
        return result_cards

