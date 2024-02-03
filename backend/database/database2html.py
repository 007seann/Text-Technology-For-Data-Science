from dominate import document
from dominate.tags import *

# Create a class that will be used to create the html file

class Database2HTML:
    def __init__(self, date, title, article):
        self.date = date
        self.title = title
        self.article = article


    def create_html(self):
        # Create a new html file
        with document(title="News") as doc:
            with doc.head:
                link(rel='stylesheet', href='style.css')
            with doc:
                h1("News")
                p("Date: " + self.date)
                p("Title: " + self.title)
                p("Article: " + self.article)
        
        return doc.render()