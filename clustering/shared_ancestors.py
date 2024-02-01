def get_shared_ancestors(
    spark: SparkSession,
    clustering_property: str,
    use_supernodes: bool = False,
    name: str = "nss",
    name_2: str = "avg_nss_distance",
):
    query = f"MATCH (a:Article)-[:CITES]->(b:Article) return a.id as child_id, a.{clustering_property} as child_cluster, b.id as parent_id"
    ancestors = shared.spark.neo4j_query(spark, query)
    ancestors.persist(StorageLevel.DISK_ONLY)
    prefix = ""
    if use_supernodes:
        prefix = "super_"
        for_window = ancestors.select("child_id", "child_cluster").distinct()
        windowSpec = Window.partitionBy("child_cluster").orderBy("child_id")
        ranked_data = for_window.withColumn("rn", row_number().over(windowSpec))
        mapping = (
            ranked_data.select("child_id", "rn")
            .withColumn("target_mapping", (F.col("rn") / 10).cast("int"))
            .select("child_id", "target_mapping")
        )
        mapping.persist(StorageLevel.DISK_ONLY)
        joined_data = (
            ancestors.alias("df1")
            .join(
                mapping.alias("df2"),
                F.col("df1.parent_id") == F.col("df2.child_id"),
                "left",
            )
            .select("df1.child_id", "df1.child_cluster", "df2.target_mapping")
            .withColumnRenamed("target_mapping", "parent_id")
        )
        ancestors = (
            joined_data.alias("df1")
            .join(
                mapping.alias("df2"),
                F.col("df1.child_id") == F.col("df2.child_id"),
                "inner",
            )
            .select(
                "df1.child_id",
                "df2.target_mapping",
                "df1.child_cluster",
                "df1.parent_id",
            )
        )

    aggregated_data = ancestors.groupBy("child_id", "child_cluster").agg(
        F.collect_set("parent_id").alias("parents_ids")
    )
    aggregated_data.persist(StorageLevel.DISK_ONLY)

    paired_data = (
        aggregated_data.alias("df1")
        .join(
            aggregated_data.alias("df2"), F.col("df1.child_id") < F.col("df2.child_id")
        )
        .select(
            F.col("df1.child_id").alias("child_id_src"),
            F.col("df1.child_cluster").alias("child_cluster_src"),
            "df1.parents_ids",
            F.col("df2.child_id").alias("child_id_dsc"),
            F.col("df2.child_cluster").alias("child_cluster_dsc"),
            "df2.parents_ids",
        )
    )

    result = paired_data.withColumn(
        "shared_ancestors_count",
        F.size(F.array_intersect(F.col("df1.parents_ids"), F.col("df2.parents_ids"))),
    )
    aggregated_result = result.groupBy("child_cluster_src", "child_cluster_dsc").agg(
        F.avg("shared_ancestors_count").alias("average_shared_ancestors_count")
    )
    aggregated_result.persist(StorageLevel.DISK_ONLY)
    aggregated_result.write.parquet(
        f"data/{clustering_property}_{aggregated_result.count()}_{prefix}{name_2}.parquet",
        mode="overwrite",
    )
    # Compute cohesion and separation
    cohesion = aggregated_result.filter("child_cluster_src = child_cluster_dsc").select(
        "child_cluster_src", "average_shared_ancestors_count"
    )
    separation = (
        aggregated_result.filter("child_cluster_src != child_cluster_dsc")
        .groupBy("child_cluster_src")
        .agg(
            F.max("average_shared_ancestors_count").alias(
                "max_external_shared_ancestors"
            )
        )
    )
    nss = (
        cohesion.join(separation, on="child_cluster_src")
        .withColumn(
            "NSS",
            F.col("average_shared_ancestors_count")
            / (F.col("max_external_shared_ancestors") + 1),
        )
        .select("child_cluster_src", "NSS")
    )
    nss_pandas_df = nss.toPandas()

    nss_pandas_df.to_parquet(f"data/{clustering_property}_{prefix}{name}.parquet")
    fig = px.histogram(
        nss_pandas_df,
        x="NSS",
        nbins=50,
        labels={"NSS": "NSS Score"},
        title="Distribution of NSS Scores Across Communities",
    )
    fig.write_image(f"images/{clustering_property}_{prefix}{name}.png")


def calculate_accuracy(
    gds: GraphDataScience, clustering_property: str, name="accuracy"
):
    query = f"""MATCH (a:Article)
WHERE a.category = a.{clustering_property} and a.year=2019
WITH count(a) as correctPredictions
MATCH (a:Article)
where a.year=2019
with correctPredictions, count(a) as accuracy
RETURN toFloat(correctPredictions) / accuracy"""
    result = gds.run_cypher(query).values[0][0]
    with open(f"data/{clustering_property}_{name}.txt", "w") as f:
        f.write(str(result))
