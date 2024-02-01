import pickle
import pandas as pd
from graphdatascience import GraphDataScience
import shared.utils
import os


def get_cluster_sizes(gds: GraphDataScience, clustering_property: str):
    query = f"MATCH (a:Article) return a.{clustering_property} as communityId,count(a.id) as size"
    return gds.run_cypher(query)


def read_dataframe(path: str):
    return pd.read_parquet(path) if os.path.exists(path) else None


def get_path(clustering_property: str, metric: str):
    return f"data/{clustering_property}_combined_{metric}.parquet"


def accuracy(path_parquet: str):
    path = path_parquet[: -len(".parquet")] + ".txt"
    if not os.path.exists(path):
        return 0
    with open(path) as f:
        return f.read()


nameMapping = {
    "computeMillis": "Czas obliczeń",
    "whole_computation_ms": "Sumaryczny czas obliczeń",
    "frpComputeMillis": "FRP Czas obliczeń",
    "communityCount": "Ilość społeczności",
}


def read_times(clustering_property: str):
    path = f"stats/{clustering_property}_timings.parquet"
    df1 = read_dataframe(path)
    if df1 is None:
        raise Exception()
    if "communityCount" not in df1.columns:
        df1["communityCount"] = 40
    df1["time_s"] = 1000 * df1["time_s"]
    df1.rename(columns={"time_s": "calculating_mayority_ms"}, inplace=True)
    if "frp" in clustering_property:
        path_frp = f"stats/frp{clustering_property}_timings.parquet"
        df2 = read_dataframe(path_frp)
        if df2 is None:
            raise Exception()
        df2.rename(
            columns={
                "mutateMillis": "frpMutateMillis",
                "computeMillis": "frpComputeMillis",
                "preProcessingMillis": "frpPreProcessingMillis",
            },
            inplace=True,
        )
        df1 = df1.merge(df2, on="no")
        cols_to_sum = [
            "writeMillis",
            "postProcessingMillis",
            "computeMillis",
            "calculating_mayority_ms",
            "frpMutateMillis",
            "frpComputeMillis",
            "frpPreProcessingMillis",
        ]
        columns_to_compute = [
            "frpMutateMillis",
            "FRP Czas obliczeń",
            "frpPreProcessingMillis",
            "writeMillis",
            "postProcessingMillis",
            "Czas obliczeń",
            "calculating_mayority_ms",
            "Sumaryczny czas obliczeń",
            "Ilość społeczności",
        ]
    else:
        cols_to_sum = [
            "writeMillis",
            "postProcessingMillis",
            "computeMillis",
            "calculating_mayority_ms",
        ]
        columns_to_compute = [
            "writeMillis",
            "postProcessingMillis",
            "Czas obliczeń",
            "calculating_mayority_ms",
            "Sumaryczny czas obliczeń",
            "Ilość społeczności",
        ]

    df1["whole_computation_ms"] = df1[cols_to_sum].sum(axis=1)
    df1.rename(
        columns=nameMapping,
        inplace=True,
    )
    avg_values = df1[columns_to_compute].mean()
    std_values = df1[columns_to_compute].std()

    stats_df = pd.DataFrame({"Average": avg_values, "Standard Deviation": std_values})
    stats_df = stats_df[
        (stats_df["Average"] != 0) | (stats_df["Standard Deviation"] != 0)
    ]

    # Rounding to two decimal places
    stats_df = stats_df.round(2)

    print(stats_df)

    # latex print
    print()


def read_metrics():
    pass


metricsMapping = {
    "conductance": "Konduktancja",
    "modularity": "Modularność",
    "coverage": "Pokrycie",
    "accuracy": "Precyzja",
}


def main(
    clustering_properties,
    metrics,
):
    confusion_matrix = "confusion_matrix"
    for clustering_property in clustering_properties:
        print("\033[1m", clustering_property, "\033[0m")
        if clustering_property != "category":
            read_times(clustering_property)
        df1 = read_dataframe(get_path(clustering_property, "sizes"))
        if df1 is None:
            raise Exception()

        for metric in metrics:
            df2 = read_dataframe(get_path(clustering_property, metric))
            if df2 is None:
                raise Exception()

            if metric == "accuracy":
                accuracy = (
                    df2.groupby(clustering_property)
                    .agg({"CorrectPredictions": "sum", "TotalInCluster": "sum"})
                    .reset_index()
                )
                accuracy["accuracy"] = (
                    accuracy["CorrectPredictions"] / accuracy["TotalInCluster"]
                )
                avg_metric_value = round(accuracy["accuracy"].mean(), 4)
                std_metric_value = round(accuracy["accuracy"].std(), 4)
                print(f"Precyzja\t\t {avg_metric_value}\t\t\t {std_metric_value}")

                continue
            if "community" in df2.columns:
                df2.rename(columns={"community": "communityId"}, inplace=True)
            merged_df = pd.merge(
                df1,
                df2,
                left_on=[clustering_property, "communityId"],
                right_on=[clustering_property, "communityId"],
                how="left",
            )
            weighted_metric = f"weighted_{metric}"
            merged_df[weighted_metric] = merged_df["size"] * merged_df[metric]
            average_metric = f"avg_{metric}"
            grouped = (
                merged_df.groupby(clustering_property)
                .apply(lambda x: x[weighted_metric].sum() / x["size"].sum())
                .reset_index(name=average_metric)
            )

            # Step 4: Calculate average and standard deviation of average conductance for all algorithm_runs
            avg_metric_value = round(grouped[average_metric].mean(), 4)
            std_metric_value = round(grouped[average_metric].std(), 4)

            print(
                f"{metricsMapping[metric]}\t\t {avg_metric_value}\t\t\t {std_metric_value}"
            )
    # read_times(clustering_properties)
    # for clustering_property in clustering_properties:
    #     print("\033[1m", clustering_property, "\033[0m")
    #     print("accuracy:", accuracy(get_path(clustering_property, "accuracy")))
    #     cluster_sizes = get_cluster_sizes(gds, clustering_property)
    #     filtered_cluster_sizes_df = cluster_sizes[cluster_sizes["communityId"] != -1]
    #     for metric in metrics:
    #         res = read_dataframe(get_path(clustering_property, metric))
    #         if res is None:
    #             continue
    #         if "community" in res.columns:
    #             res.rename(columns={"community": "communityId"}, inplace=True)
    #         res = res.merge(filtered_cluster_sizes_df, on="communityId", how="right")
    #         weighted_avg = (res[metric] * res["size"]).sum() / res["size"].sum()
    #         print(f"{metric}", weighted_avg)


if __name__ == "__main__":
    shared.utils.load_env_variables()
    main(
        [
            "category",  # ground truth
            "louvain",
            "louvainTopics",
            "louvainWeighted",
            "louvainTopicsWeighted",
            "labelPropagation",
            "labelPropagationTopics",
            "labelPropagationWeighted",
            "labelPropagationTopicsWeighted",
            "frp512_knm",
            "frp256_knm_half",
            "nlp_knm",
            "nlp_frp512_knm",
            "frp512Topics_knm",
            "frp512Weighted_knm",
            "frp512TopicsWeighted_knm",
        ],
        ["conductance", "modularity", "coverage", "accuracy"],
    )
