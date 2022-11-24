import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"


def get_spark():
    spark = SparkSession.builder\
        .config("spark.driver.memory", "16G")\
        .config("spark.driver.maxResultSize", "0") \
        .config("spark.kryoserializer.buffer.max", "2000M")\
        .config("spark.jars.packages", "com.johnsnowlabs.nlp:spark-nlp_2.12:4.0.0,org.neo4j:neo4j-connector-apache-spark_2.12:4.1.2_for_spark_3")\
        .getOrCreate()
    return spark
