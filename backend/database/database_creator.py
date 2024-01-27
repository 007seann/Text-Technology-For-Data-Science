import pandas as pd
from sqlalchemy import create_engine

# News Type - 
# CNBC = Business News
# CNN = National and International Cable News
# Reuters = Multimedia News
# The New York Times =  American Daily News
# The Hill = US Political News
# Vice = Politic News
# Refinery 29 = Celebrity News

def filter_news():
    df = pd.read_csv("collection/all-the-news-2-1.csv")
    publicators = ["CNBC","The New York Times", "CNN", "Reuters",  "The Hill", "Vice", "Refinery 29"]
    
    df = df[df["publication"].isin(publicators)].groupby("publication").sample(100000)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    df.sort_values(by=['date'], inplace=True)
    df.to_csv("collection/corpus.csv", index=False)


def load_data():
    try:
        corpus = pd.read_csv("collection/corpus.csv")[["date", "title", "article"]]
        corpus.insert(0, "doc_id", list(range(corpus.shape[0])))
    
        conn_string = 'postgresql://postgres:12345@127.0.0.1/postgres'
        db = create_engine(conn_string) 
        conn = db.connect()

        corpus.to_sql("news", conn, if_exists="replace", index=False)
        
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


filter_news()
load_data()