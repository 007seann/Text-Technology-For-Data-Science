from flask import Flask
import psycopg2 
from parsers import Database2HTML

app = Flask(__name__)



def create_conn(hostname):
    conn = psycopg2.connect(database="postgres", user="postgres", 
                            password="12345", host=hostname, port="5432") 
    curr = conn.cursor()
    return curr, conn


@app.route('/api/news/<int:id>', methods=["GET"])
def retrieve_new(id):
    curr, conn = create_conn("94.156.35.233")
    sql = """SELECT date, title, article FROM news WHERE doc_id = %s"""
    curr.execute(sql, (str(id),))
    data = curr.fetchone()
    
    if data is None:
        return "News Not Found", 404
    
    date, title, article = data
    curr.close()
    conn.close()

    # Create html result
    html = Database2HTML(date, title, article).create_html()
    
    return html, 200

if __name__ == "__main__":
    app.run(debug=True, port=5002, host='0.0.0.0')
