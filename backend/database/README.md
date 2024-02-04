# Setup for Accessing Live Database via API

Note 1 - Only news with ID 1 to 1000 have been added to the database

Note 2 - If you query for news that are not within the ID range, a 404 error will be returned

On Windows:

1. Please make sure to have the Flask installed in Python using **pip install flask**/ **pip install flask --user**

2. From the root directory, navigate to the database folder using **cd backend/database**

3. Run the backend application on local machine with **py backend_app.py**

4. When you want to call the API to query a news with ID **x**, i.e either on Postman or in a Python application, use the GET request with URL **http://127.0.0.1:5000/api/news/x**

5. The API will return the news' article, title and date published as a HTML page

If there are any issues with connecting , please let Tanatip know so he can fix it. The database may sometimes refuse connection so it needs to be restarted
