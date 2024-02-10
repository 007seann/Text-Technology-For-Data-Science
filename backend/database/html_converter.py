from backend_app import create_conn
import requests
import re
def save_html():
    curr, conn = create_conn("94.156.35.233")
    max_id_sql = """SELECT doc_id FROM news"""
    curr.execute(max_id_sql)
    doc_ids = curr.fetchall()
    
    for id in doc_ids:
        id = id[0]


        url = f"http://127.0.0.1:5000/api/news/{id}"
        r = requests.get(url).text
    

        with open(f"collection/news_{id}.html", "w", encoding="utf-8") as f:
            f.write(r)
            
    
save_html()
    