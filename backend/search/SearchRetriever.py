import sys
sys.path.append('../backend/indexer')
from indexer.PositionalIndex import PositionalIndex
from faker import Faker
import requests
import BeautifulSoup
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

    def __init__(self):
        self.index = PositionalIndex()
        self.index.load_index('../backend/database/index/index_base.txt')
        self.faker = Faker()

    def _get_news(doc_id):
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
        returned_news = [(self._get_news(doc_id), positions) for doc_id, positions in doc_positions_list]
        for raw_html, positions in returned_news:
            all_tags = raw_html.find_all('p') # Will be changed when the HTML format is fixed
            date = all_tags[0].text
            title = all_tags[1].text
            content = all_tags[2].text # TODO Need to be processed into publisher/text
            bold_token = random.choice(positions)
            # bold_token = positions[0] # If we don't want to make it random 
            card = self.ResultCard(title=title,
                                    url=self.faker.url(),
                                    image=self.faker.image_url(width=50, height=50),
                                    date=date,
                                    publisher="Publisher",
                                    sentiment=0.0, # TODO
                                    bold_token=int(bold_token))
            result_cards.append(card)
        return result_cards

