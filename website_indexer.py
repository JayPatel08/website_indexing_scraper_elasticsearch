from html.parser import HTMLParser
from urllib.request import urlopen
from urllib import parse
from elasticsearch import Elasticsearch
from demo import text_from_html

es_client = Elasticsearch(['http://127.0.0.1:9200'])
def index(index_name):

    drop_index = es_client.indices.create(index=index_name, ignore=400)

class LinkParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for (key, value) in attrs:
                if key == 'href':
                    newUrl = parse.urljoin(self.baseUrl, value)
                    if newUrl not in self.links:
                        self.links = self.links + [newUrl]


    def getLinks(self, url):
        self.links = []
        self.baseUrl = url
        response = urlopen(url)
        print(response.getheader('content-Type'))
        if (response.getheader('Content-Type')[0:9] == 'text/html'):

            htmlBytes = response.read()
            htmlString = htmlBytes.decode("utf-8")
            self.feed(htmlString)

            return htmlString, self.links
        else:
            return "", []


def spider(url,index_name,maxPages=100):
    extra_url = url
    pagesToVisit = [url]
    print(pagesToVisit)
    numberVisited = 0
    foundWord = False
    index(index_name)
    visited_links = []
    while numberVisited < maxPages and pagesToVisit != []:
        numberVisited = numberVisited + 1


        url = pagesToVisit[0]
        pagesToVisit = pagesToVisit[1:]
        if(url not in visited_links and extra_url==url[0:len(extra_url)]):
            visited_links.append(url)

            try:
                print(numberVisited, "Visiting:", url)
                parser = LinkParser()
                data, links = parser.getLinks(url)
                text_content=text_from_html(data)
                doc = {
                    'url': url,
                    'content':text_content,
                }
                res = es_client.index(index=index_name, doc_type="docs", body=doc)
                pagesToVisit = pagesToVisit + links
                print(visited_links)
            except:
                print("error")



