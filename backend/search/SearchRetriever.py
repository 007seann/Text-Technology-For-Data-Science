import sys
sys.path.append("./backend/indexer")
from backend.indexer.PositionalIndex import PositionalIndex
from faker import Faker
from bs4 import BeautifulSoup
from dataclasses import dataclass
import lxml

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
        self.faker = Faker()

    def _get_news(self, doc_id):
        url = self.index.docid_to_url[int(doc_id)]
        with open(url, "r") as f:
            html = f.read()
        return BeautifulSoup(html, "lxml")
    
    def _search(self, query):
        doc_positions_list = self.index.process_query(query)
        return doc_positions_list
    
    def get_results(self, query):
        result_cards = []
        doc_positions_list = self._search(query)
        returned_news = [(self._get_news(doc_id), positions) for doc_id, positions in doc_positions_list]
        for raw_html, positions in returned_news:
            title = raw_html.h1.string
            date = raw_html.sub.string
            raw_content = raw_html.find_all('p')
            content = ' '.join([p.string for p in raw_content])
            publisher = self.faker.name()
            url=self.faker.url()
            image=self.faker.image_url(width=50, height=50),
            bold_token = positions[0]
            card = self.ResultCard(title=title,
                                    url=url,
                                    image=image,
                                    date=date,
                                    publisher=publisher,
                                    sentiment=0.0, # TODO
                                    bold_token=bold_token,
                                    content=content)
            result_cards.append(card)
        return result_cards
