import requests
from parsers import Database2HTML
import os
import schedule
import time
from datetime import datetime as dt
import datetime

MY_API_KEY = "6d11bfe7-76c1-4933-ace0-fd93bd3cabce"
API_ENDPOINT = 'http://content.guardianapis.com/search'
live_id = 0

def fetch_guardian():
    global live_id
    end_date = dt.now()
    start_date = end_date - datetime.timedelta(days=1)
    print(start_date)
    print(end_date)
    
    my_params = {
        'from-date': start_date.strftime('%Y-%m-%d'),
        'to-date' : end_date.strftime('%Y-%m-%d'),
        'show-fields': 'all',
        'page-size': 20,
        'show-references' : 'author',
        'show-tags' : 'contributor',
        'api-key': MY_API_KEY
    }


    response = requests.get(API_ENDPOINT, params=my_params).json()
    articles = response["response"]["results"]

    for article in articles:
        fields = article["fields"]
        title = fields["headline"]
        article_body = fields["bodyText"]
        date = fields['firstPublicationDate']
        outlet = "guardian"
        url = article["webUrl"]
        domain = article["sectionName"]
        authors = []
        
        for tag in article["tags"]:
            if tag["type"] == "contributor":
                authors.append(tag['webTitle'])
                
        authors = ",".join(authors)

        political_leaning = "LEFT"
        lead_paragraph = "UNDEFINED"
        
        news_html = Database2HTML(date,title, article_body, outlet, lead_paragraph,authors, url, domain , political_leaning).create_html()
        
        folder = f"collection/live/"
            
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(f"{folder}live_news_{live_id}.html", "w", encoding="utf-8") as f:
            f.write(news_html)
            
        live_id += 1
    
schedule.every(1).day.at("22:00").do(fetch_guardian)

while True:
    schedule.run_pending()
    time.sleep(1)