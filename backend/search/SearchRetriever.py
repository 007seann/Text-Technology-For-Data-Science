import sys
sys.path.append("./backend/indexer")
sys.path.append("./backend/logger")
from bs4 import BeautifulSoup
from pathlib import Path
from dataclasses import dataclass
import os
import requests
from backend.logger.SearchLogger import SearchLogger
from backend.logger.PerformanceLogger import PerformanceLogger
from backend.indexer.Tokeniser import Tokeniser
import time

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
        content: str

    def __init__(self, index):
        self.index = index
        self.tokeniser = Tokeniser()

    def _get_news(self, doc_id):
        url = self.index.docid_to_url[int(doc_id)]
        if config.get("run_config", "dev") == "True":
            SearchLogger.log(f"Running in local mode, retrieving url {url} from API.")
            html = requests.get(url).text
        else:
            with open(url, "r") as f:
                html = f.read()
                SearchLogger.log(f"Retrieved url {url}")
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
        start = time.time()
        doc_positions_list = self.index.process_query(query)
        PerformanceLogger.log(f"Entire Search ({query}) took {time.time() - start} seconds")
        SearchLogger.log(f"Retrieved documents {doc_positions_list} for query {query}")
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


    def _get_relevant_content(self, title, body, bold_token_index, left_window=15, right_window=15):
        if bold_token_index == -1:
            return ' '.join(self.tokeniser.tokenise(body)[:right_window])
        content = title + " " + body
        split_content = self.tokeniser.tokenise(content)
        bold_token = split_content[bold_token_index]
        split_content[bold_token_index] = f"<b>{bold_token}</b>"
        start = max(0, bold_token_index-left_window)
        end = min(len(split_content), bold_token_index+right_window)
        relevant_content = split_content[start:end]
        SearchLogger.log(f"Returning relevant content for bold token: {bold_token} and content: {' '.join(relevant_content)}")
        return "...{}...".format(' '.join(relevant_content).strip())
    
    def _get_meaningful_bold_token_index(self, positions, title):
        for position in positions:
            if position >= len(title):
                return position
        return -1
    
    def get_results(self, query):
        result_cards = []
        doc_positions_list = self._search(query)
        returned_news = [(self._get_news(doc_id), positions) for doc_id, positions in doc_positions_list]
        for raw_html, positions in returned_news:
            title = raw_html.h1.string
            date = raw_html.sub.string.replace("Published ", "")[:10]
            body = raw_html.find_all('p')
            body_content = ' '.join([p.string for p in body])
            publisher = raw_html.h3.string.replace("Publication outlet: ", "")
            url=raw_html.find('meta', id='url')['content']
            image=self._get_favicon(publisher)
            bold_token_index = self._get_meaningful_bold_token_index(positions, title)
            relevant_content = self._get_relevant_content(title, body_content, bold_token_index)
            card = self.ResultCard(title=title,
                                    url=url,
                                    image=image,
                                    date=date,
                                    publisher=publisher,
                                    sentiment=0.0, # TODO
                                    content=relevant_content)
            SearchLogger.log(f"Created result card {card}")
            result_cards.append(card)
        return result_cards
