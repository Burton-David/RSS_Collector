import pandas as pd
from itertools import combinations

def load_data(file_path):
    """
    Load RSS articles from a CSV file.
    Args:
        file_path (str): Path to the CSV file.
    Returns:
        DataFrame: Loaded data.
    """
    return pd.read_csv(file_path)

def preprocess_data(df):
    """
    Preprocess data for association rule mining.
    Args:
        df (DataFrame): Original DataFrame.
    Returns:
        Series: Processed transaction data grouped by date.
    """
    df['published_date'] = pd.to_datetime(
        df['published'], 
        format="%a, %d %b %Y %H:%M:%S %Z",
        errors="coerce"
    ).dt.date

    df = df.dropna(subset=["published_date"])
    transactions = df.groupby('published_date')['source'].apply(list)
    return transactions

def encode_transactions(transactions):
    """
    One-hot encode transaction data.
    Args:
        transactions (Series): Transaction data grouped by date.
    Returns:
        DataFrame: One-hot encoded DataFrame.
    """
    from mlxtend.preprocessing import TransactionEncoder
    te = TransactionEncoder()
    encoded = te.fit(transactions).transform(transactions)
    return pd.DataFrame(encoded, columns=te.columns_)

def generate_frequent_itemsets(encoded_df, min_support=0.1):
    """
    Generate frequent itemsets manually.
    Args:
        encoded_df (DataFrame): One-hot encoded data.
        min_support (float): Minimum support threshold.
    Returns:
        DataFrame: Frequent itemsets.
    """
    total_transactions = len(encoded_df)
    item_support = encoded_df.sum(axis=0) / total_transactions
    frequent_itemsets = item_support[item_support >= min_support].sort_values(ascending=False)
    return frequent_itemsets
def generate_association_rules(frequent_itemsets, transactions, min_confidence=0.1):
    """
    Manually generate association rules from frequent itemsets.
    Args:
        frequent_itemsets (Series): Frequent itemsets with support values.
        transactions (Series): Original transactions grouped by date.
        min_confidence (float): Minimum confidence threshold.
    Returns:
        DataFrame: Association rules.
    """
    item_support = frequent_itemsets.to_dict()
    rules = []
    transaction_list = transactions.tolist()

    for items in combinations(item_support.keys(), 2):
        item1, item2 = items

        # Calculate support for the pair
        pair_support = sum(
            1 for transaction in transaction_list if item1 in transaction and item2 in transaction
        ) / len(transaction_list)

        # Calculate confidence for the rule
        confidence_item1_to_item2 = pair_support / item_support[item1]
        confidence_item2_to_item1 = pair_support / item_support[item2]

        # Append rules if confidence meets threshold
        if confidence_item1_to_item2 >= min_confidence:
            rules.append({
                "antecedent": item1,
                "consequent": item2,
                "support": pair_support,
                "confidence": confidence_item1_to_item2
            })
        if confidence_item2_to_item1 >= min_confidence:
            rules.append({
                "antecedent": item2,
                "consequent": item1,
                "support": pair_support,
                "confidence": confidence_item2_to_item1
            })

    return pd.DataFrame(rules)

if __name__ == "__main__":
    data_path = "data/rss_articles.csv"
    print(f"Loading data from {data_path}...")
    articles_df = load_data(data_path)

    print("Preprocessing data...")
    transactions = preprocess_data(articles_df)

    print("Encoding transactions...")
    encoded_df = encode_transactions(transactions)

    print("Generating frequent itemsets...")
    min_support = 0.1
    frequent_itemsets = generate_frequent_itemsets(encoded_df, min_support)
    print(f"Frequent itemsets:\n{frequent_itemsets}")

    print("Generating association rules...")
    min_confidence = 0.05
    rules = generate_association_rules(frequent_itemsets, transactions, min_confidence)

    output_path = "data/association_rules.csv"
    rules.to_csv(output_path, index=False)
    print(f"Association rules saved to {output_path}")
    print(f"Sample transactions:\n{transactions.head()}")
    print(f"Generated rules:\n{rules}")