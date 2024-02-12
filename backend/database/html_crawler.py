import os

class HTML_Directory_Crawler:
    def __init__(self):
        self.cwd = os.getcwd()

    def get_html_file(self, doc_id: str):
        """
        Parameter: doc_id - the doc id of the article to be retrieved, e.g. 42
        Returns: html_path - the path to the html file, html - the content of the html file
        """
        html_path = os.path.join(self.cwd, "collection", f'news_{doc_id}.html')

        print(html_path)

        try:
            with open(html_path, "r") as file:
                html = file.read()

            return html_path, html
        
        except FileNotFoundError as e:
            print(e)