import pandas as pd

def load_data(qrel_path, ttds_path):
    """
    Load the qrel and ttds system results data from CSV files.
    """
    qrel_df = pd.read_csv(qrel_path)
    ttds_df = pd.read_csv(ttds_path)
    return qrel_df, ttds_df

def calculate_precision_at_k(retrieved_docs, relevant_docs, k=10):
    """
    Calculate precision at cutoff k for a single query.
    """
    top_k_docs = set(retrieved_docs[:k])
    relevant_docs_in_top_k = top_k_docs.intersection(relevant_docs)
    return len(relevant_docs_in_top_k) / k

def calculate_recall_at_k(retrieved_docs, relevant_docs, k=50):
    """
    Calculate recall at cutoff k for a single query.
    """
    top_k_docs = set(retrieved_docs[:k])
    relevant_docs_in_top_k = top_k_docs.intersection(relevant_docs)
    if not relevant_docs:
        return 0
    return len(relevant_docs_in_top_k) / len(relevant_docs)

def calculate_metrics(qrel_df, ttds_df):
    """
    Calculate P@10 and R@50 for all queries in the dataset.
    """
    # Grouping the data
    qrel_grouped = qrel_df.groupby('query_id')['doc_id'].apply(set).to_dict()
    ttds_grouped = ttds_df.groupby('query_number')['doc_number'].apply(list).to_dict()

    # Initialize metrics dictionaries
    precision_at_10 = {}
    recall_at_50 = {}

    # Calculate metrics for each query
    for query_id in qrel_grouped.keys():
        relevant_docs = qrel_grouped[query_id]
        retrieved_docs = ttds_grouped.get(query_id, [])
        precision_at_10[query_id] = calculate_precision_at_k(retrieved_docs, relevant_docs, k=10)
        recall_at_50[query_id] = calculate_recall_at_k(retrieved_docs, relevant_docs, k=50)

    # Calculate average metrics
    avg_precision_at_10 = sum(precision_at_10.values()) / len(precision_at_10)
    avg_recall_at_50 = sum(recall_at_50.values()) / len(recall_at_50)

    return avg_precision_at_10, avg_recall_at_50
