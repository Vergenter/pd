### TODO!
1. Prepare database

### Find metrics 

label propagation defined for directed graphs

#### Clustering Methods

1. Category Homogeneity Index (CHI):

    Metric: For each cluster, calculate the fraction of papers that belong to the most common category within the cluster.
    Meaning: This measures how homogeneous a cluster is with respect to categories. If CHI is close to 1, it means the cluster mainly contains papers from a single category, indicating that the clustering method is good at grouping papers based on category.

2. Temporal Cohesion (TC):

    Metric: For each cluster, calculate the standard deviation of the publication years of the papers within the cluster.
    Meaning: A lower standard deviation indicates that the publication years are close to each other, suggesting that the cluster contains papers from a specific time frame.

3. Citation Density (CD):

    Metric: For each cluster, calculate the ratio of the number of citations within the cluster to the total number of possible citations within the cluster.
    Meaning: This quantifies the internal connectedness of the cluster based on citations. A high CD means that the papers within the cluster have a high number of citations amongst themselves.

4. Inter-Cluster Citation Ratio (ICCR):

    Metric: For each cluster, calculate the ratio of the number of citations pointing outside the cluster to the number of citations within the cluster.
    Meaning: A lower ratio suggests that the cluster is more self-contained in terms of citations, indicating that the clustering method has identified a tightly-knit community.

5. Silhouette Score

    What it Measures: It measures how similar an object is to its own cluster compared to other clusters. The values range from -1 to 1, where a high value indicates that the object is well matched to its own cluster and poorly matched to neighboring clusters.
    How to Use: Compute the silhouette score for each data point and average them. A higher average silhouette score indicates better-defined clusters.

6. Davies-Bouldin Index

    What it Measures: It measures the average similarity between each cluster and its most similar cluster, where similarity is the ratio of within-cluster distances to between-cluster distances. Lower values indicate better clustering.
    How to Use: Compute the Davies-Bouldin Index after clustering. Lower values indicate more distinct clusters.

7. Adjusted Rand Index (ARI)

    What it Measures: It measures the similarity between two clusterings by considering all pairs of samples and counting pairs that are assigned to the same or different clusters in the predicted and true clusterings.
    How to Use: Since you have known categories, you can treat them as ground truth and compare your clustering results to them using ARI. Values close to 1 indicate high similarity to the true categories.


Citation Homophily


### TODO!
1. policz label_propagation
2. 