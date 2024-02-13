from backend_app import create_conn
import requests
from bs4 import BeautifulSoup
import os

def save_html():
    curr, conn = create_conn("94.156.35.233")
    max_id_sql = """SELECT doc_id FROM news"""
    curr.execute(max_id_sql)
    doc_ids = curr.fetchall()
    
    curr.close()
    conn.close()
    
    for id in doc_ids:
        id = id[0]


        url = f"http://127.0.0.1:5002/api/news/{id}"
        r = requests.get(url).text
        soup = BeautifulSoup(r, "html.parser")
        outlet = soup.find(attrs={"id" : "outlet"}).text.split(" ")[-1].lower()
        folder = f"collection/{outlet}/"
        
        if not os.path.exists(folder):
            os.makedirs(folder)

        with open(f"{folder}news_{id}.html", "w", encoding="utf-8") as f:
            f.write(r)
        
            
    
save_html()
    