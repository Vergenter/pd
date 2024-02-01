from graphdatascience import GraphDataScience
from graphdatascience.graph.graph_object import Graph
import os
import shared.utils
import plotly.express as px
import plotly.figure_factory as ff
from time import perf_counter


def explode_n(name: str, n: int):
    return [name + f"_{i}" for i in range(n)]


def create_graph_if_not_exist(
    gds: GraphDataScience, clustering_properties: list[str], n: int
) -> Graph:
    name = "Articles_with_clusters"
    if gds.graph.exists(name)[1]:
        gds.graph.drop(gds.graph.get(name))
        # Create the graph if it doesn't exist
    G, result = gds.graph.project(
        name,  # Graph name
        ["Article"],  # Node projection
        "CITES",  # Relationship projection
        readConcurrency=4,  # Configuration parameters
        nodeProperties=[x for p in clustering_properties for x in explode_n(p, n)],
    )
    return G


import pandas as pd


def calculate_metric(
    gds: GraphDataScience,
    G: Graph,
    fetch_data_func,
    clustering_property: str,
    n: int,
    name: str,
):
    combined_data = []
    for i in range(n):
        current_property = f"{clustering_property}_{i}"

        # Use the passed function to fetch the data
        df = fetch_data_func(gds, G, current_property)

        df[clustering_property] = i
        combined_data.append(df)

    combined_df = pd.concat(combined_data, ignore_index=True)
    combined_df.to_parquet(f"data/{clustering_property}_combined_{name}.parquet")

    return combined_df


def fetch_modularity_data(gds, G: Graph, current_property):
    r1 = gds.alpha.modularity.stream(G, communityProperty=current_property)
    return pd.DataFrame(r1)


def fetch_conductance_data(gds, G: Graph, current_property):
    r1 = gds.alpha.conductance.stream(G, communityProperty=current_property)
    newpd = pd.DataFrame(r1)
    newpd.rename(columns={"community": "communityId"}, inplace=True)
    return newpd


def fetch_coverage_data(gds, _: Graph, current_property):
    query = f"""
    MATCH ()-[y:CITES]->()
    with count(y) as total_citations
    MATCH (a1:Article)-[x:CITES]->(a2:Article)
    WHERE a1.{current_property} = a2.{current_property}
    with a1.{current_property} as communityId, count(x) as same_label_count, total_citations
    RETURN communityId, toFloat(same_label_count)/total_citations as coverage
    """
    result = gds.run_cypher(query)
    return pd.DataFrame(result)


def fetch_accuracy_data(gds, G: Graph, current_property: str):
    property_with_consensus = current_property + "consensus"
    query = f"""MATCH (a:Article) WHERE a.year=2019
WITH 
  a.category AS communityId, 
  COUNT(*) AS TotalInCluster,
  SUM(CASE WHEN a.category = a.{property_with_consensus} THEN 1 ELSE 0 END) AS CorrectPredictions

RETURN communityId, toFloat(CorrectPredictions) / TotalInCluster AS accuracy,TotalInCluster,CorrectPredictions
ORDER BY communityId"""
    result = gds.run_cypher(query)
    return pd.DataFrame(result)


def fetch_confusion_matrix_data(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    name: str = "confusion_matrix",
):
    property_with_consensus = clustering_property + "consensus"
    query = f"""MATCH (a:Article) where a.year=2019
WITH a.category AS GroundTruth, a.{property_with_consensus} AS Predicted
RETURN GroundTruth, Predicted, COUNT(*) AS Count
ORDER BY GroundTruth, Predicted"""
    result = gds.run_cypher(query)
    return pd.DataFrame(result)


def calculate_modularity(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    n: int,
    name: str = "modularity",
):
    combined_df = calculate_metric(
        gds, G, fetch_modularity_data, clustering_property, n, name
    )


def calculate_conductance(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    n: int,
    name: str = "conductance",
):
    combined_df = calculate_metric(
        gds, G, fetch_conductance_data, clustering_property, n, name
    )


def calculate_coverage(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    n: int,
    name: str = "coverage",
):
    combined_df = calculate_metric(
        gds, G, fetch_coverage_data, clustering_property, n, name
    )

    # Group by communityId and compute the mean coverage for each community
    avg_coverage_df = (
        combined_df.groupby("communityId")["coverage"].mean().reset_index()
    )
    # Create a histogram for the average coverage scores


def calculate_weighted_accuracy(df: pd.DataFrame) -> float:
    total_weighted_correct = (df["accuracy"] * df["TotalInCluster"]).sum()
    total_articles = df["TotalInCluster"].sum()
    return total_weighted_correct / total_articles


def calculate_accuracy(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    n: int,
    name: str = "accuracy",
):
    # combined_df = fetch_accuracy_data(gds, G, clustering_property)
    combined_df = calculate_metric(
        gds, G, fetch_accuracy_data, clustering_property, n, name
    )
    # Calculate global weighted accuracy
    global_weighted_accuracy = calculate_weighted_accuracy(combined_df)
    with open(f"data/{clustering_property}_{name}.txt", "w") as f:
        f.write(str(global_weighted_accuracy))


import numpy as np


def calculate_confusion_matrix(
    gds: GraphDataScience,
    G: Graph,
    clustering_property: str,
    n: int,
    name: str = "confusion_matrix",
):
    combined_df = calculate_metric(
        gds, G, fetch_confusion_matrix_data, clustering_property, n, name
    )


def fetch_cluster_sizes(gds, G: Graph, current_property):
    query = f"""
    match (a1:Article) return a1.{current_property} as communityId,count(a1) as size
    """
    result = gds.run_cypher(query)
    return pd.DataFrame(result)


def save_cluster_sizes(gds: GraphDataScience, G: Graph, current_property: str, N: int):
    calculate_metric(gds, G, fetch_cluster_sizes, current_property, N, "sizes")


def main(clustering_properties: list[str]):
    gds = GraphDataScience(
        "bolt://192.168.0.178:7687",
        auth=(os.environ["NEO4J_LOGIN"], os.environ["NEO4J_PASSWORD"]),
    )
    N = 10
    G = create_graph_if_not_exist(gds, clustering_properties, N)

    for clustering_property in clustering_properties:
        print(clustering_property)
        save_cluster_sizes(gds, G, clustering_property, N)
        calculate_modularity(gds, G, clustering_property, N)
        calculate_conductance(gds, G, clustering_property, N)
        calculate_coverage(gds, G, clustering_property, N)
        calculate_accuracy(gds, G, clustering_property, N)
        calculate_confusion_matrix(gds, G, clustering_property, N)


if __name__ == "__main__":
    shared.utils.load_env_variables()
    main(
        [
            # "category",  # ground truth
            # "labelPropagation",
            # "louvain",
            "nlp_knm",
            "frp512_knm",
            "frp256_knm_half",
            "nlp_frp512_knm",
            # "labelPropagationTopics",
            # "louvainTopics",
            "frp512Topics_knm",
            # "labelPropagationWeighted",
            # "louvainWeighted",
            "frp512Weighted_knm",
            "nlp_frp512Weighted_knm",
            # "labelPropagationTopicsWeighted",
            # "louvainTopicsWeighted",
            "frp512TopicsWeighted_knm",
        ]
    )
