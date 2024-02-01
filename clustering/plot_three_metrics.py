import pickle
import pandas as pd
from graphdatascience import GraphDataScience
import shared.utils
import os
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np


def read_dataframe(path: str):
    return pd.read_parquet(path) if os.path.exists(path) else None


def get_path(clustering_property: str, metric: str):
    return f"data/{clustering_property}_combined_{metric}.parquet"


def should_use_log_scale(data):
    # Apply a heuristic to determine if log scale is needed
    # For this example: use log scale if max value is 100 times greater than median
    return max(data) > 100 * np.median(data)


def main(
    clustering_properties,
):
    for clustering_property in clustering_properties:
        coverage = read_dataframe(get_path(clustering_property, "coverage"))
        modularity = read_dataframe(get_path(clustering_property, "modularity"))
        conductance = read_dataframe(get_path(clustering_property, "conductance"))
        if coverage is None or modularity is None or conductance is None:
            raise Exception()

        conductance.rename(columns={"community": "communityId"}, inplace=True)
        result = conductance.merge(
            coverage, on=[clustering_property, "communityId"]
        ).merge(modularity, on=[clustering_property, "communityId"])

        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=conductance["conductance"],
                opacity=0.75,
                name="Konduktancja",
                marker=dict(color="blue"),
            )
        )

        fig.add_trace(
            go.Histogram(
                x=coverage["coverage"],
                opacity=0.75,
                name="Pokrycie",
                marker=dict(color="green"),
            )
        )

        fig.add_trace(
            go.Histogram(
                x=modularity["modularity"],
                opacity=0.75,
                name="Modularność",
                marker=dict(color="red"),
            )
        )

        # Overlay histograms
        fig.update_layout(
            barmode="overlay",
            font=dict(size=18),
            yaxis_title="Ilość",
            xaxis_title="Wartość metryki",
        )
        if should_use_log_scale(modularity["modularity"]):
            fig.update_yaxes(type="log")
        # fig.show()
        fig.write_image(
            f"images/merged/{clustering_property}_distribution.png",
            width=1000,
            height=600,
        )
        #     print("wololo")

    pass


if __name__ == "__main__":
    shared.utils.load_env_variables()
    main(
        [
            # "category",  # ground truth
            "labelPropagation",
            "louvain",
            "nlp_knm",
            "frp512_knm",
            "frp256_knm_half",
            "nlp_frp512_knm",
            "labelPropagationTopics",
            "louvainTopics",
            "frp512Topics_knm",
            "labelPropagationWeighted",
            "louvainWeighted",
            "frp512Weighted_knm",
            "nlp_frp512Weighted_knm",
            "labelPropagationTopicsWeighted",
            "louvainTopicsWeighted",
            "frp512TopicsWeighted_knm",
        ],
    )
