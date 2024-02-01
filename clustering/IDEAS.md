Implement all metrics

Evaluate methods

metric idea is Efficient split



metric result should be saved to some csv file

**graph metrics**:
Silhouette Score
Conductance
Modularity
Davies-Bouldin Index
Calinski Harabasz Index
Coverage
Rand index
Shared ancestors
Jaccard Coefficient for ancestors
Jaccard Coefficient for children
Jaccard Coefficient for ancestors of children
**classification metrics**
accuracy
confusion matrix

metrics have 2 dimensions from how they incorporate nlp
nlp
1. similarity as weight
2. additional edges
3. new graph from texts
3.1. Adjusted Rand Index
3.2. Normalized Mutual Information
then 

hybrid methods
Graphsage



MATCH (n:Article)
WITH n.cluster AS cluster, AVG(n.centroidDistance) AS Si
RETURN cluster, Si


Ancestor Similarity
Upstream Overlap



### Co impelmenetuje
#### metrics
Coverage
Conductance
Modularity
Shared ancestors
accuracy
confusion matrix
#### Classification
label propagation
louvain
kmeans
gds.beta.pipeline.nodeClassification
<!-- nlp classification
knn + graphsage/Node2Vec/Fast Random Projection -->
### improvement
knn + graphsage/Node2Vec/Fast Random Projection + nlp embeding
nlp classification + graphsage/Node2Vec/Fast Random Projection
label propagation with added edge weight from similarity !new approach for metrics
louvain/Leiden with added edge weight from similarity !new approach for metrics


label propagation with added edges from keywords matching !new approach for metrics
louvain/Leiden with added edges from keywords matching !new approach for metrics