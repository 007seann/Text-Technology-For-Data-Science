import sys
sys.path.append("./")
from backend.search.SearchRetriever import SearchRetriever
from backend.indexer.PositionalIndex import PositionalIndex
from flask import Flask, render_template, request
# from flask_paginate import Pagination, get_page_parameter
app = Flask(__name__)

indexer = PositionalIndex()
search_retriever = SearchRetriever(indexer)

@app.route('/')
def index():
    return render_template('index.html', results=None)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/search', methods=['POST'])
def search():
    if request.method == "POST":
        query = request.form['query']
        result_cards = search_retriever.get_results(query)
        '''
        for card in result_cards:
            print("Title:", card.title)
            print("Date:", card.date)
            print("Publisher:", card.publisher)
            print("Content:", card.content)
            # Add more attributes as needed
            print("-" * 50)  # Just for visual separation between cards
        '''
        return render_template('search_result.html', query = query, result_cards=result_cards)
    else:
        return "Method not Allowed"



if __name__ == '__main__':
    app.run(debug=True, port=5002, use_reloader=False)
    # app.run(host='192.168.0.48', port=5000, debug=True, threaded=False)
    #app.run(host='172.20.183.177', port=5000, debug=True, threaded=False)
