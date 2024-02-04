import xml.etree.ElementTree as ET
import csv
"""

This script converts our given financial time articles for CW1 to csv form for sentiment clasficiation task. 

"""


xml_file_path = 'trec.sample.xml'
tree = ET.parse(xml_file_path)
root = tree.getroot()

articles = []

# Iterate over each article (DOC tag)
for doc in root.findall('.//DOC'):
    headline_element = doc.find('.//HEADLINE')
    text_element = doc.find('.//TEXT')

    # Extract text from each element, handling the case where an element might not be found
    headline_text = headline_element.text.strip() if headline_element is not None else 'No Title Found'
    text_content = text_element.text.strip() if text_element is not None else 'No Text Found'

    # Append the extracted data to the articles list
    articles.append([headline_text, text_content])

# Prepare CSV data
csv_header = ['news_title', 'text']
csv_data = [csv_header] + articles

# # Extract needed data
# news_title = root.find('.//HEADLINE')
# text = root.find('.//TEXT')


# # Check if tags were found and extract text
# news_title_text = news_title.text if news_title is not None else 'No Title Found'
# text_text = text.text if text is not None else 'No Text Found'

# # Prepare CSV data
# csv_data = [['news_title', 'text'], [news_title_text, text_text]]

# Write data to CSV
with open('output.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print("Data written to 'output.csv'")