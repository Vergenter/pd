
from graphdatascience import GraphDataScience
import os
from dotenv import load_dotenv

# Load environment variables from .envrc
load_dotenv('/home/vergenter/Projects/masterthesis_2/.envrc')
# Use Neo4j URI and credentials according to your setup
gds = GraphDataScience("bolt://192.168.0.178:7687",
                       auth=(os.environ["NEO4J_LOGIN"], os.environ["NEO4J_PASSWORD"]))


res = gds.graph.project.estimate(
    ["Article"],  # Node projection
    "CITES",  # Relationship projection
    readConcurrency=4  # Configuration parameters
)

G, result = gds.graph.project(
    "Articles",  # Graph name
    ["Article"],  # Node projection
    "CITES",  # Relationship projection
    readConcurrency=4  # Configuration parameters
)
print(res)
