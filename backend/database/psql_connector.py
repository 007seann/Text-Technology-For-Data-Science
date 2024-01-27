from google.cloud.sql.connector import Connector
import sqlalchemy

# TODO : Upload news corpus onto Cloud SQL

INSTANCE_CONNECTION_NAME = "ttds-1-412322:us-central1:news-instance"
DB_USER = "postgres"
DB_PASS = "admin"
DB_NAME = "postgres"


# initialize Connector object
connector = Connector()

# function to return the database connection object
def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pg8000",
        user=DB_USER,
        password=DB_PASS,
        db=DB_NAME
    )
    return conn

# create connection pool with 'creator' argument to our connection object function
pool = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
)


with pool.connect() as db_conn:
  print("hello")