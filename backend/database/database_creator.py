import pandas as pd
from sqlalchemy import create_engine

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
    news_corpus.to_csv("collection/news_corpus.csv",index=False)
    
     

def load_data(hostname):
    try:
        corpus = pd.read_csv("collection/news_corpus.csv")
        corpus.insert(0, "doc_id", list(range(corpus.shape[0])))
        corpus = corpus.sample(50)
        
        conn_string = f'postgresql://postgres:12345@{hostname}/postgres'
        db = create_engine(conn_string) 
        conn = db.connect()

        corpus.to_sql("news", conn, if_exists="replace", index=False)
        
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()


#filter_news()
#"94.156.35.233"
load_data("94.156.35.233")