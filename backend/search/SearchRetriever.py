import sys
sys.path.append("./backend/indexer")
from backend.indexer.PositionalIndex import PositionalIndex
from faker import Faker
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
import random

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
        content: str

    def __init__(self):
        self.index = PositionalIndex()
        self.index.load_index('./backend/database/index/index_base.txt')
        self.faker = Faker()

    def _get_news(self, doc_id):
        pass
    
    def _search(self, query):
        doc_positions_list = self.index.process_query(query)
        return doc_positions_list
    
    def get_results(self, query):
        result_cards = []
        # doc_positions_list = self._search(query)
        # returned_news = [(self._get_news(1), positions) for doc_id, positions in doc_positions_list]
        # for raw_html, positions in returned_news:
        num_results = 5
        for _ in range(num_results):
            date = self.faker.date()
            title = self.faker.sentence()
            publisher = self.faker.name()
            content = " ".join(self.faker.paragraphs(2))
            bold_token = 0
            card = self.ResultCard(title=title,
                                    url=self.faker.url(),
                                    image=self.faker.image_url(width=50, height=50),
                                    date=date,
                                    publisher=publisher,
                                    sentiment=0.0, # TODO
                                    bold_token=bold_token,
                                    content=content)
            result_cards.append(card)
        return result_cards
