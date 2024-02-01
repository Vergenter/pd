import plotly.graph_objects as go
import pandas as pd

# Data in a pandas DataFrame
df = pd.DataFrame(
    {
        "Metoda": [
            "louvain",
            "louvainTopics",
            "louvainWeighted",
            "louvainTopicsWeighted",
            "labelPropagation",
            "labelPropagationTopics",
            "labelPropagationWeighted",
            "labelPTopicsWeighted",
            "frp512knm",
            "nlpknm",
            "nlpfrp512knm",
            "frp512Topicsknm",
            "frp512Weightknm",
            "frp512TWknm",
        ],
        "Sumaryczny czas oblicze ́n[ms]": [
            10482.29,
            11941.52,
            6810.36,
            10563.6,
            5119.6,
            5032.29,
            2569.03,
            8033.08,
            14162.1,
            20011.43,
            13930.87,
            13496.7,
            14336.71,
            14277.1,
        ],
        "Precyzja": [
            0.4535,
            0.3921,
            0.445,
            0.3911,
            0.4026,
            0.3658,
            0.4438,
            0.3821,
            0.4607,
            0.3564,
            0.4574,
            0.5482,
            0.4603,
            0.5412,
        ],
    }
)

# Create scatter plot figure
fig = go.Figure()

# Predefined list of colors for points and labels
colors = [
    "#ff0000",
    "#ff0000",
    "#ff0000",
    "#ff0000",
    "#00ff00",
    "#00ff00",
    "#00ff00",
    "#00ff00",
    "#0000FF",
    "#FF00BB",
    "#FF00BB",
    "#0000FF",
    "#0000FF",
    "#0000FF",
]

# Iterate over rows and add text annotation with adjustments and matching colors
for i, row in df.iterrows():
    x_pos = row["Sumaryczny czas oblicze ́n[ms]"]
    y_pos = row["Precyzja"] + 0.006
    label = row["Metoda"]
    color = colors[i % len(colors)]  # Cycle through predefined colors

    # Manual adjustments for specific labels
    if label == "nlpfrp512knm":
        y_pos -= 0.012
    elif label == "frp512knm":
        x_pos -= 500
    elif label == "frp512TWknm":
        y_pos -= 0.012
    elif label == "frp512Weightknm":
        y_pos -= 0.006
        x_pos += 1800
    elif label == "louvainTopics":
        y_pos -= 0.012

    fig.add_annotation(
        x=x_pos,
        y=y_pos,
        xref="x",
        yref="y",
        text=label,
        showarrow=False,
        font=dict(
            size=10, color=color
        ),  # Set the label text color based on predefined list
    )

# Add scatter points with matching colors
fig.add_trace(
    go.Scatter(
        x=df["Sumaryczny czas oblicze ́n[ms]"],
        y=df["Precyzja"],
        mode="markers",
        marker=dict(color=colors),
    )
)

# Adjust layout for clarity
fig.update_layout(
    xaxis_title="Sumaryczny czas obliczeń[ms]",
    yaxis_title="Dokładność",
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    # plot_bgcolor="rgba(0,0,0,0)",
)
# Save as PNG
fig.write_image("images/method_space.svg")

# Optionally, show the plot if desired
# fig.show()
