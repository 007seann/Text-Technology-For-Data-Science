import re
import sys
sys.path.append("./backend/indexer")
from faker import Faker
from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass
import lxml
import os
import requests
import logging

util_dir = Path(os.path.join(os.path.dirname(__file__))).parent.joinpath('utils')
sys.path.append(str(util_dir))

from AppConfig import AppConfig
config = AppConfig()

RETRIEVAL_LIMIT = int(config.get("search_retriever", "result_limit"))
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

    def __init__(self, index):
        self.index = index
        self.faker = Faker()
        self.logger = logging.getLogger(self.__class__.__name__) 
        self.logger.info(f"SearchRetriever loaded. Ready for query")

    def _get_news(self, doc_id):
        url = self.index.docid_to_url[int(doc_id)]
        if config.get("run_config", "dev") == "True":
            self.logger.info(f"Running in local mode, retrieving url {url} from API.")
            html = requests.get(url).text
        else:
            with open(url, "r") as f:
                html = f.read()
                self.logger.info(f"Retrieved url {url}")
        return BeautifulSoup(html, "lxml")
        
    def _get_favicon(self, publisher, size=64):
        mapping = {
            "guardian": "theguardian",
            "journal": "thejournal",
            "NPR": "npr",
            "CBS News": "cbsnews",
            "CNN": "cnn",
            "The Guardian": "theguardian",
            "Politico": "politico",
            "HuffPost": "huffpost",
            "Fox News": "foxnews",
            "ABC News": "abcnews",
            "NBC News": "nbcnews",
            "Chicago Tribune": "chicagotribune",
            "USA Today": "usatoday",
            "Slate": "slate",
            "Reuters": "reuters",
        }
        domain = mapping.get(publisher.lower(), publisher.replace(" ", "").lower())
        return f"https://www.google.com/s2/favicons?sz={size}&domain_url={domain}.com"
        
    def _search(self, query):
        doc_positions_list = self.index.process_query(query)
        self.logger.info(f"Retrieved documents {doc_positions_list} for query {query}")
        if isinstance(doc_positions_list, set):
            # Not sure why but sometimes this registers as a list and other times as a set.
            limited_set = set()
            for item in doc_positions_list:
                if len(limited_set) < RETRIEVAL_LIMIT:
                    limited_set.add(item)
                else:
                    break
            return limited_set
        elif isinstance(doc_positions_list, list):
            return doc_positions_list[:RETRIEVAL_LIMIT]
        else:
            return doc_positions_list

    def _get_relevant_content(self, content, bold_token, left_window=15, right_window=15):
        split_content = content.split()
        if bold_token < left_window:
            left_window = bold_token
        if len(split_content) - bold_token < right_window:
            right_window = len(split_content) - bold_token
        return "...{}...".format(' '.join(split_content[bold_token-left_window:bold_token+right_window]).strip())
    
    def get_results(self, query):
        result_cards = []
        doc_positions_list = self._search(query)
        returned_news = [(self._get_news(doc_id), positions) for doc_id, positions in doc_positions_list]
        for raw_html, positions in returned_news:
            title = raw_html.h1.string
            date = raw_html.sub.string.replace("Published ", "")[:10]
            raw_content = raw_html.find_all('p')
            content = ' '.join([p.string for p in raw_content])
            publisher = raw_html.h3.string.replace("Publication outlet: ", "")
            url=raw_html.find('meta', id='url')['content']
            image=self._get_favicon(publisher)
            bold_token = 0 if positions == [] else positions[0]
            relevant_content = self._get_relevant_content(content, bold_token)
            card = self.ResultCard(title=title,
                                    url=url,
                                    image=image,
                                    date=date,
                                    publisher=publisher,
                                    sentiment=0.0, # TODO
                                    bold_token=bold_token,
                                    content=relevant_content)
            self.logger.info(f"Created result card {card}")
            result_cards.append(card)
        return result_cards
