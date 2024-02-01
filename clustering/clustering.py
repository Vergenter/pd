from typing import Optional
from graphdatascience import GraphDataScience
import os
from graphdatascience.graph.graph_object import Graph
from shared.utils import load_env_variables
from dataclasses import dataclass
from neo4j.exceptions import ClientError
import time
import pandas as pd

REPEATS = 10


@dataclass
class GraphConfiguration:
    name: str
    labels: list[str]
    edges: list[str]
    nodeProperties: list[str]
    relationshipProperties: list[str]


CONFIGURATIONS = [
    GraphConfiguration("Articles", ["Article"], ["CITES"], ["known_category"], []),
    GraphConfiguration(
        "Articles_topics",
        ["Article", "LDATopic"],
        ["CITES", "HAS_TOPIC"],
        ["known_category"],
        [],
    ),
    GraphConfiguration(
        "Articles_weights",
        ["Article"],
        ["CITES"],
        ["known_category"],
        ["weight"],
    ),
    GraphConfiguration(
        "Articles_topics_and_weights",
        ["Article", "LDATopic"],
        ["CITES", "HAS_TOPIC"],
        ["known_category"],
        ["weight"],
    ),
]
# Use Neo4j URI and credentials according to your setup
CLUSTERING_REPEATS = 10


def create_graph_if_not_exist(
    gds: GraphDataScience,
    configuration: GraphConfiguration,
) -> Graph:
    # should check avaiable porperties
    if not gds.graph.exists(configuration.name)[1]:
        G, result = gds.graph.project(
            configuration.name,  # Graph name
            configuration.labels,  # Node projection
            configuration.edges,  # Relationship projection
            readConcurrency=4,  # Configuration parameters
            nodeProperties=["known_category", "albert_text_embedding"],
            relationshipProperties=configuration.relationshipProperties,
        )
    else:
        G = gds.graph.get(configuration.name)
    return G


def take_majority_label(
    inputProperty: str, outputProperty: str, gds: GraphDataScience, G: Graph
):
    start_time = time.time()  # Start the timer
    create_mapping_query = f"""
    MATCH (a:Article)
    WITH a.{inputProperty} AS cluster, a.known_category AS category, COUNT(*) AS count
    ORDER BY cluster, count DESC
    WITH cluster, COLLECT(category)[0] AS topCategory
    CREATE (:Mapping {{tmp: cluster, label: topCategory}})
    """
    gds.run_cypher(create_mapping_query)

    # Use the mapping nodes to update `Article` nodes
    update_nodes_query = f"""
    MATCH (m:Mapping), (a:Article)
    WHERE a.{inputProperty} = m.tmp
    SET a.{outputProperty} = coalesce(m.label,-1)
    """
    gds.run_cypher(update_nodes_query)

    # Cleanup - delete the temporary mapping nodes
    cleanup_query = """
    MATCH (m:Mapping)
    DELETE m
    """
    gds.run_cypher(cleanup_query)

    end_time = time.time()  # Stop the timer
    elapsed_time = end_time - start_time  # Calculate the elapsed time

    return elapsed_time  # Return how many seconds it took


def calculate_labelPropagation(
    writeProperty: str, gds: GraphDataScience, G: Graph, weight: Optional[str] = None
):
    collected_results = []  # List to collect each r2 series

    for i in range(REPEATS):
        writeProperty_i = writeProperty + f"_{i}"
        r2 = gds.labelPropagation.write(
            G,
            writeProperty=writeProperty_i,
            seedProperty="known_category",
            maxIterations=100,
            relationshipWeightProperty=weight,
        )
        time_s = take_majority_label(
            writeProperty_i, writeProperty_i + "consensus", gds, G
        )

        r2["no"] = i
        r2["time_s"] = time_s
        collected_results.append(r2)  # Append r2 to the list

    if REPEATS > 1:  # Save only if REPEATS is greater than 1
        result = pd.concat(collected_results, axis=1).transpose()
        result.to_parquet(f"stats/{writeProperty}_timings.parquet")
    # ALl result from there should be saved to single parquet file


def calculate_louvain(
    writeProperty: str, gds: GraphDataScience, G: Graph, weight: Optional[str] = None
):
    collected_results = []  # List to collect each r2 series
    for i in range(REPEATS):
        writeProperty_i = writeProperty + f"_{i}"
        # Execute Louvain and write results to `writeProperty_tmp`
        r2 = gds.louvain.write(
            G,
            writeProperty=writeProperty_i,
            maxIterations=100,
            maxLevels=10,
            relationshipWeightProperty=weight,
        )
        # Generate the mapping nodes
        time_s = take_majority_label(
            writeProperty_i, writeProperty_i + "consensus", gds, G
        )
        r2["no"] = i
        r2["time_s"] = time_s
        collected_results.append(r2)  # Append r2 to the list

    if REPEATS > 1:  # Save only if REPEATS is greater than 1
        result = pd.concat(collected_results, axis=1).transpose()
        result.to_parquet(f"stats/{writeProperty}_timings.parquet")


def calculate_nlp_knm(
    writeProperty: str,
    gds: GraphDataScience,
    G: Graph,
    text_property: Optional[str] = None,
    k: int = 120,
):
    collected_results = []  # List to collect each r2 series
    for i in range(REPEATS):
        writeProperty_i = writeProperty + f"_{i}"
        r2 = gds.beta.kmeans.write(
            G, writeProperty=writeProperty_i, nodeProperty=text_property, k=k
        )
        time_s = take_majority_label(
            writeProperty_i, writeProperty_i + "consensus", gds, G
        )
        r2["no"] = i
        r2["time_s"] = time_s
        collected_results.append(r2)  # Append r2 to the list

    if REPEATS > 1:  # Save only if REPEATS is greater than 1
        result = pd.concat(collected_results, axis=1).transpose()
        result.to_parquet(f"stats/{writeProperty}_timings.parquet")


def calculate_frp_knm(
    writeProperty: str,
    gds: GraphDataScience,
    G: Graph,
    weight: Optional[str] = None,
    text_property: Optional[list[str]] = None,
    dimension: int = 512,
    k: int = 120,
):
    collected_results_1 = []  # List to collect each r2 series
    collected_results_2 = []  # List to collect each r2 series
    for i in range(REPEATS):
        writeProperty_i = writeProperty + f"_{i}"
        frpProperty = "frp128"
        err_result = "Failed to invoke procedure `gds.fastRP.mutate`: Caused by: java.lang.IllegalArgumentException: Node property `frp128` already exists in the in-memory graph."
        if frpProperty in G.node_properties().Article:
            gds.graph.nodeProperties.drop(G, [frpProperty])
        try:
            r1 = gds.fastRP.mutate(
                G,
                embeddingDimension=dimension,
                mutateProperty=frpProperty,
                relationshipWeightProperty=weight,
                featureProperties=text_property,
            )
            r1["no"] = i
            collected_results_1.append(r1)
        except ClientError as ex:
            if ex.message != err_result or REPEATS > 1:
                raise

        r2 = gds.beta.kmeans.write(
            G, writeProperty=writeProperty_i, nodeProperty=frpProperty, k=k
        )
        time_s = take_majority_label(
            writeProperty_i, writeProperty_i + "consensus", gds, G
        )
        r2["no"] = i
        r2["time_s"] = time_s
        collected_results_2.append(r2)
    if REPEATS > 1:  # Save only if REPEATS is greater than 1
        result_1 = pd.concat(collected_results_1, axis=1).transpose()
        result_2 = pd.concat(collected_results_2, axis=1).transpose()
        result_1.to_parquet(f"stats/frp{writeProperty}_timings.parquet")
        result_2.to_parquet(f"stats/{writeProperty}_timings.parquet")


def main():
    gds = GraphDataScience(
        "bolt://192.168.0.178:7687",
        auth=(os.environ["NEO4J_LOGIN"], os.environ["NEO4J_PASSWORD"]),
    )

    G0 = create_graph_if_not_exist(gds, CONFIGURATIONS[0])
    # calculate_labelPropagation("labelPropagation", gds, G0)
    # calculate_louvain("louvain", gds, G0)
    calculate_nlp_knm("nlp_knm", gds, G0, text_property="albert_text_embedding")
    calculate_frp_knm("frp512_knm", gds, G0)
    calculate_frp_knm("frp256_knm_half", gds, G0, dimension=256)
    calculate_frp_knm(
        "nlp_frp512_knm", gds, G0, text_property=["albert_text_embedding"]
    )
    G1 = create_graph_if_not_exist(gds, CONFIGURATIONS[1])
    # # calculate_labelPropagation("labelPropagationTopics", gds, G1)
    # # calculate_louvain("louvainTopics", gds, G1)
    calculate_frp_knm("frp512Topics_knm", gds, G1)

    G2 = create_graph_if_not_exist(gds, CONFIGURATIONS[2])
    # calculate_labelPropagation("labelPropagationWeighted", gds, G2, weight="weight")
    # calculate_louvain("louvainWeighted", gds, G2, weight="weight")
    calculate_frp_knm("frp512Weighted_knm", gds, G2, weight="weight")
    calculate_frp_knm(
        "nlp_frp512Weighted_knm",
        gds,
        G2,
        weight="weight",
        text_property=["albert_text_embedding"],
    )
    G3 = create_graph_if_not_exist(gds, CONFIGURATIONS[3])
    # calculate_labelPropagation(
    #     "labelPropagationTopicsWeighted", gds, G3, weight="weight"
    # )
    # calculate_louvain("louvainTopicsWeighted", gds, G3, weight="weight")
    calculate_frp_knm("frp512TopicsWeighted_knm", gds, G3, weight="weight")


if __name__ == "__main__":
    load_env_variables()
    main()

# %%
# community size distribution
# community count
