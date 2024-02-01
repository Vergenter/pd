import os
from pyspark.sql import SparkSession
from sparknlp.pretrained import PretrainedPipeline
from pyspark.sql import functions as F
import time


def main():
    start = time.time()
    os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
    print(os.getenv("JAVA_HOME"))
    # Create SparkSession
    spark = SparkSession.builder\
        .config("spark.driver.memory", "16G")\
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.kryoserializer.buffer.max", "2000M")\
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:4.0.0,org.neo4j:neo4j-connector-apache-spark_2.12:4.1.2_for_spark_3")\
        .getOrCreate()

    articles_abstracts = spark.read.format("org.neo4j.spark.DataSource")\
        .option("url", "bolt://192.168.0.178:7687")\
        .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])\
        .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])\
        .option("query", "MATCH (n:Article) WITH n RETURN n.id as id,n.title +'. '+ n.abstract as text")\
        .option("partitions", "4")\
        .load()

    language_detector_pipeline = PretrainedPipeline(
        'detect_language_21', lang='xx')
    articles_abstracts_with_lang = language_detector_pipeline.annotate(
        articles_abstracts, "text").select('id', 'text', F.col("language.result")[0].alias("lang")).cache()

    # query = """match (a:Article{id:event.id})
    # set a.language=event.lang"""

    # articles_abstracts_with_lang.write.format("org.neo4j.spark.DataSource")\
    # .option("url", "bolt://192.168.0.178:7687")\
    # .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])\
    # .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])\
    # .mode("append")\
    # .option("query", query)\
    # .save()

    print(articles_abstracts_with_lang.groupBy(
        "lang").count().orderBy("count", ascending=False).head(50))
    end = time.time(f"finished in {end - start}")
    print()


if __name__ == "__main__":
    main()
