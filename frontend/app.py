import sys
sys.path.append("./")
from backend.search.SearchRetriever import SearchRetriever
from flask import Flask, render_template, request
app = Flask(__name__)

search_retriever = SearchRetriever()

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
        return render_template('search_result.html', query = query)
    else:
        return "Method not Allowed"



if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='192.168.0.48', port=5000, debug=True, threaded=False)
