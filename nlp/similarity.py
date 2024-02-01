# %%
import shared.spark
import os
import shared.utils
import sparknlp
from pyspark import StorageLevel
from pyspark.sql.functions import substring

READFROMMEMORY = True
# Initialization
if __name__ == "__main__":
    shared.utils.load_env_variables()
spark = shared.spark.get_spark_session()
# %%
from pyspark.sql.types import StructType, StructField, StringType, LongType

# Define your schema
article_schema = StructType(
    [StructField("id", LongType(), True), StructField("text", StringType(), True)]
)


query_abstract = "MATCH (n:Article) RETURN n.id as id,n.title +'. '+ n.abstract as text"
articles_abstracts = (
    spark.read.format("org.neo4j.spark.DataSource")
    .option("url", "bolt://192.168.0.178:7687")
    .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])
    .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])
    .option("query", query_abstract)
    .option("partitions", "16")
    .schema(article_schema)  # Apply the schema
    .option("partition.key", "id")
    .load()
)
max_chars = 4000  # You can adjust this to your needs.
articles_abstracts = articles_abstracts.withColumn(
    "truncated_text", substring(articles_abstracts["text"], 0, max_chars)
)
articles_abstracts.persist(StorageLevel.DISK_ONLY)
print(articles_abstracts.count())
# Load data

# Persistence

# %%
# NLP Pipeline
from sparknlp.base import DocumentAssembler, EmbeddingsFinisher
from sparknlp.annotator import Tokenizer, AlbertEmbeddings
from pyspark.ml import Pipeline
from pyspark.sql.functions import expr
from pyspark.sql.functions import substring, slice as spark_slice

document_assembler = DocumentAssembler().setOutputCol("document").setInputCol("text")
tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("token")

# %%
albert_embeddings = (
    AlbertEmbeddings.pretrained()
    .setInputCols(["document", "token"])
    .setOutputCol("embeddings")
    .setCaseSensitive(True)
)
embeddings_finisher = (
    EmbeddingsFinisher()
    .setInputCols(["embeddings"])
    .setOutputCols(["finished_embeddings"])
    .setCleanAnnotations(False)
)

# Pipeline for text embeddings
pipeline_text = Pipeline(
    stages=[document_assembler, tokenizer, albert_embeddings, embeddings_finisher]
)

# %%
# Apply pipelines.
if not READFROMMEMORY:
    result_text_2 = (
        pipeline_text.fit(articles_abstracts)
        .transform(articles_abstracts)
        .select("id", "embeddings")
    )
    result_text_2.persist(StorageLevel.DISK_ONLY)
    result_text_2.write.parquet(
        f"data/result_text_13373.parquet",
        mode="overwrite",
    )
else:
    result_text = spark.read.parquet("data/result_text_1337.parquet")
    result_text_2 = result_text.select("id", "embeddings.embeddings").withColumnRenamed(
        "embeddings", "finished_embeddings"
    )

# %%
from pyspark.sql.functions import udf
from pyspark.sql.types import ArrayType, DoubleType
import numpy as np


def average_arrays(arrays):
    return np.average(arrays, axis=0).tolist()


average_arrays_udf = udf(average_arrays, ArrayType(DoubleType()))

# Apply the UDF to get the average embeddings
averaged_text = result_text_2.withColumn(
    "average_embedding", average_arrays_udf("finished_embeddings")
).select("id", "average_embedding")
# %%
averaged_text.write.parquet(
    f"data/averaged_text_13372.parquet",
    mode="overwrite",
)
# %%
print(3)
# %%
# averaged_text = spark.read.parquet("data/averaged_text_1337.parquet")
# averaged_text.persist(StorageLevel.DISK_ONLY)
# query_save_embeddings = (
#     "MATCH (n:Article{id:event.id}) SET n.albert_text_embedding=event.average_embedding"
# )
# averaged_text.write.format("org.neo4j.spark.DataSource").option(
#     "url", "bolt://192.168.0.178:7687"
# ).option("authentication.basic.username", os.environ["NEO4J_LOGIN"]).option(
#     "authentication.basic.password", os.environ["NEO4J_PASSWORD"]
# ).option(
#     "transaction.retries", 5
# ).option(
#     "transaction.retry.timeout", 5
# ).mode(
#     "Overwrite"
# ).option(
#     "query", query_save_embeddings
# ).save()
# %%
averaged_text.persist(StorageLevel.DISK_ONLY)
# %%
edges_schema = StructType(
    [
        StructField("a1_id", LongType(), False),
        StructField("edge_id", StringType(), False),
        StructField("a2_id", LongType(), False),
    ]
)
query_edges = "MATCH (a1:Article)-[c:CITES]->(a2:Article) RETURN a1.id as a1_id ,elementID(c) as edge_id,a2.id as a2_id"
edges = (
    spark.read.format("org.neo4j.spark.DataSource")
    .option("url", "bolt://192.168.0.178:7687")
    .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])
    .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])
    .option("query", query_edges)
    .option("partitions", "16")
    .schema(edges_schema)  # Apply the schema
    .option("partition.key", "a1_id")
    .load()
)
edges.persist(StorageLevel.DISK_ONLY)
# %%
from pyspark.sql.functions import col

edges_1 = (
    edges.join(averaged_text, col("a1_id") == col("id"), "left")
    .withColumnRenamed("average_embedding", "average_embedding_1")
    .select("edge_id", "a2_id", "average_embedding_1")
).repartition("a2_id")
# %%
edges_2 = (
    edges_1.join(averaged_text, col("a2_id") == col("id"), "left")
    .withColumnRenamed("average_embedding", "average_embedding_2")
    .select("edge_id", "average_embedding_1", "average_embedding_2")
)

# %%
from pyspark.sql.functions import udf
from pyspark.sql.types import FloatType
from pyspark.ml.linalg import Vectors, VectorUDT
from pyspark.sql.functions import col
import numpy as np

# Join the results


# Compute the cosine similarity
def cosine_similarity(v1, v2):
    dot_product = np.dot(v1, v2)
    magnitude_v1 = np.sqrt(np.dot(v1, v1))
    magnitude_v2 = np.sqrt(np.dot(v2, v2))
    if magnitude_v1 * magnitude_v2 == 0:
        return 0.0
    else:
        return float(dot_product / (magnitude_v1 * magnitude_v2))


cosine_similarity_udf = udf(cosine_similarity, FloatType())

# Apply cosine similarity function on the data
result = edges_2.withColumn(
    "cosine_similarity",
    cosine_similarity_udf(col("average_embedding_1"), col("average_embedding_2")),
).select("edge_id", "cosine_similarity")
# %%
result.persist(StorageLevel.DISK_ONLY)
result.write.parquet(
    f"data/similarity_1337.parquet",
    mode="overwrite",
)
# %%
# Write similarity back to Neo4j
query_similarity = """
MATCH ()-[c:CITES]->()
WHERE elementID(c)=event.edge_id
SET c.similarity = event.cosine_similarity
"""

result.write.format("org.neo4j.spark.DataSource").option(
    "url", "bolt://192.168.0.178:7687"
).option("authentication.basic.username", os.environ["NEO4J_LOGIN"]).option(
    "authentication.basic.password", os.environ["NEO4J_PASSWORD"]
).option(
    "transaction.retries", 5
).option(
    "transaction.retry.timeout", 5
).mode(
    "Overwrite"
).option(
    "query", query_similarity
).save()

# %%
