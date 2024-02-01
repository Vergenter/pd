# %%
import shared.spark
import os
import shared.utils
from sparknlp.base import Finisher, DocumentAssembler, Pipeline, LightPipeline
from sparknlp.annotator import (
    StopWordsCleaner,
    SentenceDetector,
    Tokenizer,
    YakeKeywordExtraction,
    BertForTokenClassification,
    NerConverter,
    LemmatizerModel,
    Normalizer,
    Word2VecModel,
)
from pyspark.ml.feature import StopWordsRemover, CountVectorizer, IDF
import sparknlp

if __name__ == "__main__":
    shared.utils.load_env_variables()

spark = shared.spark.get_spark_session()
# %%
from pyspark import StorageLevel

articles_abstracts = (
    spark.read.format("org.neo4j.spark.DataSource")
    .option("url", "bolt://192.168.0.178:7687")
    .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])
    .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])
    .option(
        "query",
        "MATCH (n:Article) where n.language =\"en\" WITH n RETURN n.id as id,n.title +'. '+ n.abstract as text",
    )
    .option("partitions", "4")
    .load()
)
articles_abstracts.persist(StorageLevel.DISK_ONLY)

# NLP Pipeline
assembler = DocumentAssembler().setInputCol("text").setOutputCol("document")

tokenizer = Tokenizer().setInputCols(["document"]).setOutputCol("token")

lemmatizer = LemmatizerModel.pretrained().setInputCols(["token"]).setOutputCol("lemma")

normalizer = (
    Normalizer()
    .setCleanupPatterns(
        [
            "[^a-zA-Z.-]+",
            "^[^a-zA-Z]+",
            "[^a-zA-Z]+$",
        ]
    )
    .setInputCols(["lemma"])
    .setOutputCol("normalized")
    .setLowercase(True)
)

finisher = (
    Finisher()
    .setInputCols(["normalized"])
    .setOutputCols(["normalized"])
    .setOutputAsArray(True)
)

stopwords = set(StopWordsRemover.loadDefaultStopWords("english"))

sw_remover = (
    StopWordsRemover()
    .setInputCol("normalized")
    .setOutputCol("filtered")
    .setStopWords(list(stopwords))
)

count_vectorizer = CountVectorizer(inputCol="filtered", outputCol="tf", minDF=10)

idf = IDF(inputCol="tf", outputCol="tfidf")

nlp_pipeline = Pipeline(
    stages=[
        assembler,
        tokenizer,
        lemmatizer,
        normalizer,
        finisher,
        sw_remover,
        count_vectorizer,
        idf,
    ]
)

model_nlp = nlp_pipeline.fit(articles_abstracts)

processed_df = model_nlp.transform(articles_abstracts)

# LDA
from pyspark.ml.clustering import LDA

num_topics = 500  # Modify based on your needs
lda = LDA(k=num_topics, maxIter=10, featuresCol="tfidf")
lda_model = lda.fit(processed_df)
topic_distributions = lda_model.transform(processed_df)

# Describe topics
topics = lda_model.describeTopics(maxTermsPerTopic=5)

# Show the topics
# topics.show(truncate=False)

# If you want to match the topic terms to the actual words:
vocab = model_nlp.stages[-2].vocabulary
topics_df = topics.rdd.map(
    lambda row: (row.topic, [vocab[idx] for idx in row.termIndices])
).toDF(["topic_index", "top_keywords"])

topic_terms = topics.rdd.map(
    lambda row: (row.topic, [vocab[idx] for idx in row.termIndices])
).collect()

for topic in topic_terms:
    print("Topic", topic[0])
    print(", ".join(topic[1]))


# %%
from pyspark.sql import Window
from pyspark.sql.functions import posexplode, collect_list, row_number
from pyspark.ml.functions import vector_to_array

topic_distributions = topic_distributions.withColumn(
    "topic_array", vector_to_array("topicDistribution")
)

df_exploded = topic_distributions.select(
    "*", posexplode("topic_array").alias("topic_idx", "weight")
)

# Window specification to order by weight in descending order for each row
window_spec = Window.partitionBy("id").orderBy(df_exploded["weight"].desc())
# Add row number to each exploded row within the window
df_with_rank = df_exploded.withColumn("rank", row_number().over(window_spec))

# Filter out rows where rank is greater than n
n = 3
df_top_n = df_with_rank.filter(df_with_rank["rank"] <= n)

# Group by original id (or any other unique identifier) and aggregate
topic_distributions_with_top_n = df_top_n.groupBy("id").agg(
    collect_list("topic_idx").alias("topic_indices"),
    collect_list("weight").alias("topic_weights"),
)

# %%
# This assumes each topic is uniquely identified by its index

# CREATE CONSTRAINT LDATOPIC_INDEX FOR (topic:LDATopic) REQUIRE topic.id IS UNIQUE

query_create_topics_with_keywords = """
UNWIND event as data
MERGE (t:LDATopic {id: data.topic_index})
SET t.keywords = data.top_keywords
"""

topics_df.write.format("org.neo4j.spark.DataSource").option(
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
    "query", query_create_topics_with_keywords
).save()
# %%
from pyspark.sql.functions import arrays_zip, col

topic_distributions_with_top_n = topic_distributions_with_top_n.withColumn(
    "topics_and_weights", arrays_zip(col("topic_indices"), col("topic_weights"))
)
topic_distributions_with_top_n.persist(StorageLevel.DISK_ONLY)

# %%
query_connect_article_to_topics = """
MATCH (a:Article {id: event.id})
UNWIND event.topics_and_weights as tw
MATCH (t:LDATopic {id: tw.topic_indices})
MERGE (a)-[rel:HAS_TOPIC]->(t)
ON CREATE SET rel.weight = tw.topic_weights
ON MATCH SET rel.weight = tw.topic_weights
"""

topic_distributions_with_top_n.write.format("org.neo4j.spark.DataSource").option(
    "url", "bolt://192.168.0.178:7687"
).option("authentication.basic.username", os.environ["NEO4J_LOGIN"]).option(
    "authentication.basic.password", os.environ["NEO4J_PASSWORD"]
).option(
    "transaction.retries", 5
).option(
    "transaction.retry.timeout", 5
).mode(
    "Append"
).option(
    "query", query_connect_article_to_topics
).save()


# %%

# %%

# %%
