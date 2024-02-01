from pyspark.sql import SparkSession
import os


def get_spark_session():
    return (
        SparkSession.builder.config("spark.driver.memory", "24G")
        .config("spark.driver.maxResultSize", "0")
        .config("spark.kryoserializer.buffer.max", "2000M")
        .config(
            "spark.jars.packages",
            "com.johnsnowlabs.nlp:spark-nlp_2.12:5.1.1,org.neo4j:neo4j-connector-apache-spark_2.12:4.1.5_for_spark_3",
        )
        .config("spark.executor.cores", "8")
        .config("spark.default.parallelism", "16")
        .config("spark.executor.memory", "8g")
        .config("spark.executor.memoryOverhead", "2g")
        .config("spark.local.dir", "/home/vergenter/tmp")
        .getOrCreate()
    )


def neo4j_query(spark: SparkSession, query: str):
    return (
        spark.read.format("org.neo4j.spark.DataSource")
        .option("url", "bolt://192.168.0.178:7687")
        .option("authentication.basic.username", os.environ["NEO4J_LOGIN"])
        .option("authentication.basic.password", os.environ["NEO4J_PASSWORD"])
        .option("query", query)
        .option("partitions", "8")
        .load()
    )
