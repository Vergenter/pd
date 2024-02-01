import shared.utils
import clustering.clustering
import clustering.metrics
import clustering.metric_evaluator


def main():
    clustering.clustering.main(["labelPropagation"])
    clustering.metrics.main(["labelPropagation"])
    clustering.metric_evaluator.main(["labelPropagation"])


if __name__ == "__main__":
    shared.utils.load_env_variables()
    print(3)
    main()


# louvain clean
# accuracy: 0.4703885014438152
# conductance 0.18241958088200294
# modularity 0.08741192897360989
# coverage 0.12751860261569095

#  louvain mincluster20
# accuracy: 0.46515651665554525
# conductance 0.15466445879933313
# modularity 0.08293981434149039
# coverage 0.13814076939123873
