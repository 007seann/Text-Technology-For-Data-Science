from flask import Flask, render_template, request

app = Flask(__name__)

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
def search_result():
    if request.method == "POST":
        query = request.form['query']
    
        return render_template('search_result.html', query = query)
    else:
        return "Method not Allowed"

@app.route('/search', methods=['POST'])
def process_button():
    if 'timeline' in request.form:
        query = request.form['query']
        return render_template('search_result.html', query = query)
    
    elif 'news' in request.form:
        return render_template('team.html')
    
   

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='192.168.0.48', port=5000, debug=True, threaded=False)
