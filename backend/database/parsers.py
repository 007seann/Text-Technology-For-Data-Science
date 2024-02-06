from dominate import document
from dominate.tags import *

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
    def __init__(self, date, title, article):
        self.date = date
        self.title = title
        self.article = article

    def create_html(self):
        # Create a new html file
        with document(title="News") as doc:
            with doc:
                h1("News")
                p(self.date)
                p(self.title)
                p(self.article)

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
