from dominate import document
from dominate.tags import *
import pandas as pd

from lxml.html import document_fromstring

class CSV2XML:
    def __init__(self):
        pass

    def parsing2xml(self, csv_filename):
        with open(csv_filename) as f:
            raw_news = pd.read_csv(f)

        raw_news.index += 1
        raw_news['DOCNO'] = raw_news.index
        raw_news['date'] = pd.to_datetime(raw_news['date']).dt.strftime('%Y-%m-%d')
        raw_news.rename(columns={'article': 'TEXT', 'title':'HEADLINE', 'date':'DATE'}, inplace=True)

        # Select columns to create into the xml file
        raw_news = raw_news[['DOCNO', 'DATE','HEADLINE', 'TEXT']]
        news_xml = raw_news.to_xml(index=False, row_name='DOC', root_name='document', xml_declaration=False)

        return news_xml

class Database2HTML:
    def __init__(self, date, title, article, outlet, lead_paragraph, authors, url, domain, political_leaning):
        self.date = date
        self.title = title
        self.article = article
        self.outlet = outlet
        self.lead_paragraph = lead_paragraph    
        self.authors = authors
        self.url = url
        self.domain = domain
        self.political_leaning = political_leaning

    def create_html(self):
        """
        Create html with the columns in the database. Note that lead_paragraph is used as the description of the article.
        return: Rendered html
        """
        with document(title="News") as doc:
            with doc.head:
                link(rel='stylesheet', href='styling/news_style.css')
                meta(name="lead_paragraph", content=self.lead_paragraph, id="lead_paragraph", hidden="true")
                meta(name="domain", content=self.domain, id="domain", hidden="true")
                meta(name="url", content=self.url, id="url", hidden="true")

            with doc:
                with div(style="display: flex; justify-content: center; width: 100%"):
                    with div(style="display: inline-block; max-width: 60%") :
                        h3(f'Publication outlet: {self.outlet}', id = 'outlet')
                        h4(f"{self.political_leaning}", id = "political_leaning")
                        h1(self.title , id = "title")
                        h4(f'Written by: {self.authors}', id = "authors")
                        sub(f"Published {self.date}", id = "date")
                        
                        with div(id = "article"):
                            for i in self.article.split("\n"):
                                p(i)

        return doc.render()
    
class HTML2Dict:
    # I assume that the html is in form of a string:
    # e.g. "<!DOCTYPE html>\n<html>\n  <head>\n    <title>News</title>\n    <link href="style.css" rel="stylesheet">\n  </head>\n  <body>\n    <h1>News</h1>\n    <p>Date: 03-02-2024</p>\n    <p>Title: test title</p>\n    <p>Article: test article</p>\n  </body>\n</html>"
    def __init__(self, html_string: str):
        self.html_string = html_string

    def parse_html(self):
        parsed_html = document_fromstring(self.html_string)

        date = parsed_html.xpath("//p[1]/text()")
        title = parsed_html.xpath("//p[2]/text()")
        article = parsed_html.xpath("//p[3]/text()")

        return {"date": date, "title": title, "article": article}
