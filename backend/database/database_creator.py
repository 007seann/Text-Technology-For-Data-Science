import pandas as pd
from sqlalchemy import create_engine

"""
This script imports the data from polusa corpus into the postgres database on the VPS.
The publish date, headline and body of the news articles are selected to be stored in the database.

Note: The script currently randomly selects 1000 documents to import.
"""

# 110k LW, RW and Central News Article
def filter_news():
    rw_pub = ["Fox News", "TMZ"]
    lw_pub = ["CNN", "The New York Times"]
    central_pub = ["Reuters", "The Hill"]
    
    v1_publicators = ["The New York Times", "CNN", "Reuters",  "The Hill",  "Fox News" , "TMZ"]
    all_news_v1 = pd.read_csv("collection/all-the-news-v1.csv")
    all_news_v1 = all_news_v1[all_news_v1["publication"].isin(v1_publicators)]
    all_news_v1["date"] = pd.to_datetime(all_news_v1["date"])
    
    rw_news = all_news_v1[all_news_v1["publication"].isin(rw_pub)][["date", "title", "article", "url"]]
    
    lw_news = all_news_v1[(all_news_v1["publication"].isin(lw_pub))].groupby("publication").sample(55000)
    lw_news = lw_news[["date", "title", "article", "url"]]
    
    central_news = all_news_v1[(all_news_v1["publication"].isin(central_pub))].groupby("publication").sample(55000)
    central_news = central_news[["date", "title", "article", "url"]]

    v2_publicators = ["Breitbart", "National Review", "New York Post"]
    all_news_v2_list = []

    for article in ["articles1.csv", "articles2.csv", "articles3.csv"]:
        df = pd.read_csv(f"collection/all-the-news-v2/{article}",  index_col=0)
        all_news_v2_list.append(df)
        
    all_news_v2 = pd.concat(all_news_v2_list, ignore_index=True)
    all_news_v2["date"] = pd.to_datetime(all_news_v2["date"])
    
    all_news_v2 = all_news_v2[all_news_v2["publication"].isin(v2_publicators)][["date", "title", "content", "url"]].rename(columns={"content" : "article"})
    rw_news = pd.concat([all_news_v2, rw_news], ignore_index=True)
    rw_news = rw_news.loc[rw_news['date'] >= '2016-01-01']
    
    news_corpus = pd.concat([rw_news, central_news, lw_news], ignore_index=True)
    news_corpus = news_corpus.dropna(subset=["title", "article", "date"])

    news_corpus["date"] = pd.to_datetime(news_corpus["date"]).dt.date
    news_corpus.sort_values(by=['date'], inplace=True)
    news_corpus.to_csv("collection/corpus_1.csv",index=False)
    
     

def load_data(hostname):
    try:
        """
        # Corpus created by Tanatip
        corpus_1 = pd.read_csv("collection/corpus_1.csv")
        # Corpus created by Stella
        corpus_2 = pd.read_csv("collection/corpus_2.csv").rename(columns={"published" : "date", "text" : "article"})
        # Merging both news corpus together and sampling 1000 news from there
        news_corpus = pd.concat([corpus_1, corpus_2], ignore_index=True).sample(1000)
        """

        # Using the Polusa corpus, again only 1000 news for now
        polusa_2017_1 = pd.read_csv("collection/polusa_balanced/2017_1.csv")
        polusa_2017_1 = polusa_2017_1[["date_publish", "headline", "body"]]

        polusa_2017_2 = pd.read_csv("collection/polusa_balanced/2017_2.csv")
        polusa_2017_2 = polusa_2017_2[["date_publish", "headline", "body"]]

        polusa_2018_1 = pd.read_csv("collection/polusa_balanced/2018_1.csv")
        polusa_2018_1 = polusa_2018_1[["date_publish", "headline", "body"]]

        polusa_2018_2 = pd.read_csv("collection/polusa_balanced/2018_2.csv")
        polusa_2018_2 = polusa_2018_2[["date_publish", "headline", "body"]]

        polusa_2019_1 = pd.read_csv("collection/polusa_balanced/2019_1.csv")
        polusa_2019_1 = polusa_2019_1[["date_publish", "headline", "body"]]

        polusa_2019_2 = pd.read_csv("collection/polusa_balanced/2019_2.csv")
        polusa_2019_2 = polusa_2019_2[["date_publish", "headline", "body"]]

        news_corpus = pd.concat([polusa_2017_1, polusa_2017_2, polusa_2018_1, polusa_2018_2, polusa_2019_1, polusa_2019_2], ignore_index=True)
        news_corpus = news_corpus.rename(columns={"date_publish" : "date", "headline" : "title", "body" : "article"})

        news_corpus = news_corpus[["date", "title", "article"]].sample(1000)

        # Adding ID to each sample
        news_corpus.insert(0, "doc_id", list(range(1, news_corpus.shape[0] + 1)))
        
        conn_string = f'postgresql://postgres:12345@{hostname}/postgres'
        db = create_engine(conn_string) 
        conn = db.connect()

        news_corpus.to_sql("news", conn, if_exists="replace", index=False)
        
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


#filter_news()
load_data("94.156.35.233")