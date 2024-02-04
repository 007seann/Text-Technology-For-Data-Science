import pandas as pd
import sys

"""A Script to be called from command line to convert a csv file to xml file."""

def parsing2xml(csv_filename, xml_filename):
    with open(csv_filename) as f:
        raw_news = pd.read_csv(f)

    raw_news.index += 1
    raw_news['DOCNO'] = raw_news.index
    raw_news['date'] = pd.to_datetime(raw_news['date']).dt.strftime('%Y-%m-%d')
    raw_news.rename(columns={'article': 'TEXT', 'title':'HEADLINE', 'date':'DATE'}, inplace=True)

    # Select columns to create into the xml file
    raw_news = raw_news[['DOCNO', 'DATE','HEADLINE', 'TEXT']]
    raw_news.to_xml(xml_filename, index=False, row_name='DOC', root_name='document', xml_declaration=False)


def main():
    # Check if the number of arguments is correct
    if len(sys.argv) != 3:
        print("Usage: python csv_to_xml.py <csv_filename> <xml_filename>")
        sys.exit(1)

    csv_filename = sys.argv[1]
    xml_filename = sys.argv[2]

    parsing2xml(csv_filename, xml_filename)


if __name__ == "__main__":
    main()