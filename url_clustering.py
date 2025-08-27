import argparse
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns


# -------------------- Data Loading --------------------
def load_data(csv_path, limit=100):
    """Load CSV with URLs and performance metrics.

    Parameters
    ----------
    csv_path : str
        Path to CSV file.
    limit : int
        Maximum number of URLs to process.
    """
    df = pd.read_csv(csv_path, encoding="utf-8", errors="replace")
    columns = [
        "P\u00e1ginas principales",
        "Clics",
        "Impresiones",
        "CTR",
    ]
    df = df[columns].dropna().head(limit)
    return df


# -------------------- Web Scraping --------------------
def scrape_text(url, timeout=10):
    """Fetch main text content from a URL."""
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = " ".join(soup.stripped_strings)
        return text
    except Exception:
        return ""


def fetch_texts(urls):
    texts = []
    for url in urls:
        texts.append(scrape_text(url))
    return texts


# -------------------- Topic Clustering --------------------
def cluster_by_topic(urls, texts, eps=0.8, min_samples=2):
    """Cluster URLs by textual similarity using DBSCAN."""
    vectorizer = TfidfVectorizer(stop_words="spanish")
    X = vectorizer.fit_transform(texts)
    reducer = TruncatedSVD(n_components=2, random_state=42)
    coords = reducer.fit_transform(X)
    db = DBSCAN(eps=eps, min_samples=min_samples, metric="cosine")
    labels = db.fit_predict(X)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=coords[:, 0], y=coords[:, 1], hue=labels, palette="tab10")
    plt.title("Cl\u00fasteres de URLs por Tem\u00e1tica")
    plt.xlabel("Componente 1")
    plt.ylabel("Componente 2")
    plt.legend(title="Cl\u00faster")
    plt.tight_layout()
    plt.savefig("topic_clusters.png")
    plt.close()

    return labels


# -------------------- Audience Clustering --------------------
def cluster_by_audience(df, k=3):
    """Cluster URLs using performance metrics."""
    features = df[["Clics", "Impresiones", "CTR"]]
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=k, random_state=42)
    labels = kmeans.fit_predict(X)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        x=df["Clics"],
        y=df["Impresiones"],
        hue=labels,
        size=df["CTR"],
        sizes=(20, 200),
        palette="tab10",
    )
    plt.title("Cl\u00fasteres de URLs por Rendimiento")
    plt.xlabel("Clics")
    plt.ylabel("Impresiones")
    plt.legend(title="Cl\u00faster")
    plt.tight_layout()
    plt.savefig("audience_clusters.png")
    plt.close()

    return labels


# -------------------- Main Routine --------------------
def main():
    parser = argparse.ArgumentParser(description="URL clustering analysis")
    parser.add_argument("csv", help="CSV file with URLs and metrics")
    parser.add_argument("--limit", type=int, default=50, help="Number of URLs to analyze")
    parser.add_argument("--k", type=int, default=3, help="Clusters for audience analysis")
    args = parser.parse_args()

    df = load_data(args.csv, limit=args.limit)
    urls = df["P\u00e1ginas principales"].tolist()
    texts = fetch_texts(urls)

    df["topic_cluster"] = cluster_by_topic(urls, texts)
    df["audience_cluster"] = cluster_by_audience(df, k=args.k)

    df.to_csv("clustered_urls.csv", index=False)
    print("Analysis complete. Results saved to clustered_urls.csv")


if __name__ == "__main__":
    main()
