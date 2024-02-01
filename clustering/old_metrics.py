from pyspark import StorageLevel
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
import plotly.graph_objects as go
from shared.utils import load_env_variables
import os


def get_spark_session():
    return SparkSession.builder\
        .config("spark.driver.memory", "16G")\
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.kryoserializer.buffer.max", "2000M")\
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:4.0.0,org.neo4j:neo4j-connector-apache-spark_2.12:4.1.2_for_spark_3")\
        .config("spark.executor.cores", "8")\
        .config("spark.default.parallelism", "16")\
        .config("spark.local.dir","/home/vergenter/tmp")\
        .getOrCreate()


def neo4j_query(spark: SparkSession, query: str):
    return spark.read.format("org.neo4j.spark.DataSource")\
        .option("url", "bolt://192.168.0.178:7687")\
        .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])\
        .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"]).option("query", query)\
        .option("partitions", "8")\
        .load()


def get_articles(spark: SparkSession):
    query = "MATCH (n:Article)--(c:Category) where n.language =\"en\" WITH n,c RETURN n.id as id, n.year as year, n.labelPropagation as cluster, c.id as category"
    articles_abstracts = neo4j_query(spark, query)
    articles_abstracts.persist(StorageLevel.DISK_ONLY)
    return articles_abstracts


def get_shared_ancestors(spark: SparkSession,k: int=1):
    query = """MATCH (a:Article)-[:CITES]->(b:Article)
return a.id as child, a.labelPropagation as child_cluster, b.id as parent, b.labelPropagation as parent_cluster"""
    
    ancestors = neo4j_query(spark, query)
    
    # Aggregation
    aggregated_data = ancestors.groupBy("child", "child_cluster")\
                    .agg(F.collect_set("parent").alias("parents"))
    
     # Iteratively find ancestors up to k levels
    for _ in range(1, k):
        aggregated_data = aggregated_data.alias("agg_data")\
                            .join(ancestors.alias("orig_data"), F.col("agg_data.ancestors") == F.col("orig_data.child"))\
                            .groupBy("agg_data.child", "agg_data.child_cluster")\
                            .agg(F.collect_set("orig_data.ancestor").alias("ancestors"))
    
    # Cache as this DataFrame is used multiple times
    aggregated_data.cache()
    
    paired_data = aggregated_data.alias("df1")\
                    .join(aggregated_data.alias("df2"), F.col("df1.child") < F.col("df2.child"))\
                    .select("df1.child", "df1.child_cluster", "df1.parents", "df2.child", "df2.child_cluster", "df2.parents")

    # Use native Spark operations for list intersection
    result = paired_data.withColumn(
        "shared_ancestors_count",
        F.size(F.array_intersect(F.col("df1.parents"), F.col("df2.parents")))
    )
    
    # Aggregating the result to compute average shared ancestors count by child clusters
    aggregated_result = result.groupBy("df1.child_cluster", "df2.child_cluster")\
                              .agg(F.avg("shared_ancestors_count").alias("average_shared_ancestors_count"))
    
    print(aggregated_result.count())
    
    # If you cached the DataFrame, it's good to unpersist to free up memory once you're done.
    aggregated_data.unpersist()
    
    return aggregated_result




def get_cluster_count(articles_abstracts: DataFrame):
    cluster_count = articles_abstracts.select('cluster').distinct().count()
    print("Cluster count", cluster_count)


def visualize_distribution(articles_abstracts: DataFrame):
    # Group articles by cluster and count the number of articles in each cluster
    cluster_counts = articles_abstracts.groupBy("cluster").count()

    # Group clusters by the count of articles and calculate the number of clusters for each count
    community_size_distribution = cluster_counts.groupBy(
        "count").agg(F.count("cluster").alias("cluster_count"))

    # Optionally, sort the results by the count of articles in ascending or descending order
    community_size_distribution = community_size_distribution.orderBy("count")
    # Convert the Spark DataFrame to a Pandas DataFrame for plotting
    community_size_pd = community_size_distribution.toPandas()

    top_100 = community_size_pd.head(100)  # it works!

    # Create a bar chart using Plotly with the top 100 values
    fig = go.Figure(data=go.Bar(
        x=top_100['count'], y=top_100['cluster_count']))
    fig.update_layout(title='Community Size Distribution (Top 100)',
                      xaxis_title='Community Size', yaxis_title='Number of Clusters')

    # Save the plot as a PNG file
    fig.write_image('community_size_distribution.png')


def calculate_chi(articles_abstracts: DataFrame):
    # Calculate the count of papers in each category within each cluster
    category_count = articles_abstracts.groupBy('cluster', 'category').count()

    # Find the maximum count of papers in each cluster
    max_count_per_cluster = category_count.groupBy(
        'cluster').agg(F.max('count').alias('max_count'))

    # Join the original DataFrame with the maximum count per cluster
    joined_df = category_count.join(max_count_per_cluster, on='cluster')

    # Calculate the CHI by dividing the count of papers in the most common category by the maximum count
    chi = joined_df.withColumn('chi', F.col('count') / F.col('max_count'))

    # Calculate the average CHI value for the whole graph
    average_chi = chi.groupBy().avg('chi').collect()[0][0]

    print("Average CHI: ", average_chi)


def calculate_tc(articles_abstracts: DataFrame):
    tc = articles_abstracts.groupBy('cluster').agg(
        F.stddev('year').alias('tc'))
    average_tc = tc.agg(F.avg('tc')).collect()[0][0]
    print("Average TC: ", average_tc)


def calculate_citation_density(spark: SparkSession):
    query = """MATCH ()-[y:CITES]->()
with count(y) as total_citations
MATCH (a1:Article)-[x:CITES]->(a2:Article)
WHERE a1.labelPropagation = a2.labelPropagation
with count(x) as same_label_count,total_citations
RETURN toFloat(same_label_count)/total_citations as Citation_Density"""
    average_cd = neo4j_query(spark, query)

    print("Average cd: ", average_cd.head(1)[0][0])

def calculate_conductance(spark: SparkSession):
    uery = """MATCH (a1:Article)-[:Cites]->(a2:Article)
WHERE a1.predicted_category = a2.predicted_category
WITH a1.predicted_category AS predictedCategory, COUNT(*) AS internalEdges

MATCH (a1:Article)-[:Cites]->(a2:Article)
WHERE a1.predicted_category <> a2.predicted_category AND a1.predicted_category = predictedCategory
WITH predictedCategory, internalEdges, COUNT(*) AS externalEdges

RETURN predictedCategory, 
       externalEdges * 1.0 / CASE WHEN internalEdges < externalEdges THEN internalEdges ELSE externalEdges END AS conductance;"""

def calculate_Inter_Cluster_Citation_Ratio(spark: SparkSession):
    query = 0
    # cluster cites itself instead of others
    # cites in cluster vs cites out of cluster


if __name__ == "__main__":
    load_env_variables()
    spark = get_spark_session()
    articles_abstracts = get_articles(spark)

    # get_shared_ancestors(spark)
    get_cluster_count(articles_abstracts)
    # calculate_chi(articles_abstracts)
    # calculate_tc(articles_abstracts)
    # calculate_citation_density(spark)
