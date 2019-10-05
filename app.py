from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
import  website_indexer
app = Flask(__name__)
es = Elasticsearch('http://127.0.0.1', port=9200)
index_name = ''
@app.route('/')
def home():
    return render_template('home.html')

@app.route("/upload",methods=['POST'])
def upload():
    url = request.form.get('url')
    index_name = request.form.get('index')
    website_indexer.spider(url,index_name, 2500)
    return render_template("search.html")

@app.route('/search/results', methods=['GET', 'POST'])
def search_request():
    search_term = request.form["input"]
    res = es.search(
        index=index_name,
        body={
            "query": {
                "match_phrase": {
                    'content': search_term,
                }
            }
        }
    )
    return render_template('results.html', res=res )

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='localhost', port=5000)