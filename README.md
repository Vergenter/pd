# Improving sna with nlp

### method idea
1. importance on topics/keywords/ners
1. Betweeneess for topics/keywords/ners
1. Closness for topics/keywords/ners(kinda dumb)
1. Clusters of topic/keywords/ners
1. Similarity SCC + topic/keywords/ners/word2vec/idf similarity>
1. weights for clustering from topic/keywords/ners/word2vec/idf similarity
1. weights for importance from topic/keywords/ners/word2vec/idf similarity
1. weights for importance from topic/keywords/ners/word2vec dissimilarity
1. RNER for clustering
1. feature for similarity
1. extract keywords define their count as feaure and new similarity
1. (search) importance on topics/keywords/ners affected by idf
1. Clustering and importance on RNER
1. Betweeness on RNER
1. feauture for knn and spectral

### method with greatest potential
meaning
alternatives

#### importance on topics/keywords/ners
meaning: quality 
alternatives: 
    idf
#### Distance for topics/keywords/ners
meaning: similarity
alternatives:
    nlp similarity
or average distance for neighbours
#### clusterigs over topics/keywords/ners
meaning: clustering with meaning of texts
alternatives:
    normal clustering
It should improve clustering by connecting same topics keywords etc.


#### weights from text
it depdends from edge meaning
but you can say more similar text are better connected

#### improve rner with centrality
improves clustering
impreves sna


Improved:
Clustering
Search(importance)