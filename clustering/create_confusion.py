import pickle
import pandas as pd
from graphdatascience import GraphDataScience
import shared.utils
import os
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import numpy as np


def calculate_confusion_matrix(
    combined_df: pd.DataFrame,
    clustering_property: str,
    name: str = "confusion_matrix",
):
    matrix = [[0 for _ in range(41)] for _ in range(41)]

    # Populate the matrix from the data
    for _, row in combined_df.iterrows():
        ground_truth = int(row["GroundTruth"])
        predicted = 40 if np.isnan(row["Predicted"]) else int(row["Predicted"])

        if ground_truth < 0 or ground_truth > 39:
            ground_truth = 40
        if predicted < 0 or predicted > 39:
            predicted = 40

        matrix[ground_truth][predicted] = row["Count"]

    matrix_normalized = np.array(matrix, dtype=float)
    for i in range(matrix_normalized.shape[0]):
        row_sum = matrix_normalized[i].sum()
        if row_sum > 0:  # To avoid division by zero
            matrix_normalized[i] = np.round(
                matrix_normalized[i] / row_sum, 2
            )  # rounding to 2 decimal places

    # Create color_matrix with the same shape as matrix_normalized
    color_matrix = np.zeros_like(matrix_normalized)

    for i in range(matrix_normalized.shape[0]):
        for j in range(matrix_normalized.shape[1]):
            if i == j and i < 40:  # Diagonal
                color_matrix[i][j] = 0.5 + 0.5 * matrix_normalized[i][j]
            else:  # Non-diagonal
                color_matrix[i][j] = 0.5 - 0.5 * matrix_normalized[i][j]

    # Define custom colorscale
    colorscale = [
        [0, "purple"],
        [0.25, "red"],
        [0.5, "white"],
        [0.75, "yellow"],
        [1, "green"],
    ]

    # Plot the heatmap using color_matrix for color and matrix_normalized for annotations
    figure = ff.create_annotated_heatmap(
        z=color_matrix,
        colorscale=colorscale,
        annotation_text=matrix_normalized,
        showscale=True,
        zmin=0,
        zmax=1,
    )

    # Update layout
    figure.update_layout(
        xaxis_title="Predicted",
        yaxis_title="Ground Truth",
        font=dict(size=18),
        xaxis_title_font=dict(size=64),  # Adjust the font size for x-axis title
        yaxis_title_font=dict(size=64),
    )
    # figure.show()

    figure.write_image(
        f"images/{clustering_property}_{name}.png", width=2000, height=2000
    )


def read_dataframe(path: str):
    return pd.read_parquet(path) if os.path.exists(path) else None


def get_path(clustering_property: str, metric: str):
    return f"data/{clustering_property}_combined_{metric}.parquet"


def main(
    clustering_properties,
):
    for clustering_property in clustering_properties:
        confusion_matrix = read_dataframe(
            get_path(clustering_property, "confusion_matrix")
        )
        if confusion_matrix is None:
            raise Exception()
        calculate_confusion_matrix(confusion_matrix, clustering_property)


if __name__ == "__main__":
    main(
        [
            "category",  # ground truth
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
        ]
    )
