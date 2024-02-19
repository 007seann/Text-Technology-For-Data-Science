import requests

class QuerySuggestion:
    """
    This is the class responsible for Query Suggestion. It uses the Google Search engine via HTTP GET request
    to suggest queries related to what the user has typed in the search bar.
    """
    
    def __init__(self):
        """
        
        Initialises the Query Suggestion object
        """
        # Set the base URL for which we are going to get the suggested queries from
        self.baseUrl = "https://google.com/complete/search"
        # Defining the parameters to send with the GET request
        self.params = {"client" : "chrome", "hl" : "en"}
        
    def suggest(self,query):
        """
        
        Makes a HTTP GET request to the Google URL to fetch the list of suggested queries

        Args:
            query (str): The query string the user has typed in so far

        Returns:
            List[str]: A list of string representing the suggested queries 
        """
        # Defining the query keyword in the URL
        self.params["q"] = query
        # Performing the GET request with the specified parameters and URL
        r = requests.get(self.baseUrl,params =self.params)
        content = r.json()
        suggestions = content[1]
            
        return suggestions