import pandas as pd
import sys

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
