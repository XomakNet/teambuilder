from typing import List

from models.user import User


def dec_number_to_base(dec_number: int, base: int, result_digits_count: int) -> List[int]:
    digits_new_base = []
    while dec_number > 0:
        older_digit = dec_number % base
        digits_new_base = [older_digit] + digits_new_base
        dec_number = int(dec_number / base)

    while len(digits_new_base) < result_digits_count:
        digits_new_base = [0] + digits_new_base

    return digits_new_base


class Clusterings:

    def __init__(self, clusters_in_clustering_count):
        self._clusterings = {}
        self._clusters_in_clustering_count = clusters_in_clustering_count

    def add_clustering_for_list(self, clustering: List[List[User]], list_number: int):
        if self._is_clustering_full(list_number):
            raise ValueError("Error adding clustering: number of clusters in the clustering must be %d, not %d"
                             % (self._clusters_in_clustering_count, len(clustering + 1)))

        self._clusterings[list_number] = clustering

    def add_cluster_to_clustering(self, cluster: List[User], list_number: int):
        if self._is_clustering_full(list_number):
            raise ValueError("Error adding cluster to clustering for list %d: this clustering is full")

        self._clusterings.setdefault(list_number, []).append(cluster)

    def get_clustering_by_list_number(self, list_number: int) -> List[List[User]]:
        if list_number not in self._clusterings.keys():
            raise KeyError("Error getting clustering for list %d: there is no clustering for the list" % list_number)

        return self._clusterings[list_number]

    def _is_clustering_full(self, list_number: int) -> bool:
        clustering = self._clusterings.get(list_number)

        if clustering:
            if len(clustering) >= self._clusters_in_clustering_count:
                return True

        return False

    def _get_product_of_clusterings_sizes(self) -> int:
        product = 1
        for clustering in self._clusterings.values():
            product *= len(clustering)
        return product

    @staticmethod
    def _get_common_part_of_clusters(clusters_for_comparison) -> List[User]:
        if len(clusters_for_comparison) == 0:
            return []

        common_part = set(clusters_for_comparison[0])
        for cluster_number in range(1, len(clusters_for_comparison)):
            common_part = common_part.intersection(set(clusters_for_comparison[cluster_number]))

        return list(common_part)

    def get_max_common_part_of_clusterings(self) -> List[User]:
        max_length_of_common_part = 0
        max_common_part = []
        lists_count = len(self._clusterings)
        total_comparisons_count = self._get_product_of_clusterings_sizes()

        # On each iteration, mutually compare clusters from different lists
        for current_comparison_number in range(0, total_comparisons_count):

            # Getting indexes of clusters which we will compare on this step
            current_clusters_indexes = dec_number_to_base(current_comparison_number,
                                                          self._clusters_in_clustering_count,
                                                          lists_count)
            # Create list of clusters for comparison
            clusters_for_comparison = [self._clusterings[list_number][cluster_number]
                                       for list_number, cluster_number in enumerate(current_clusters_indexes)]

            # Mutually compare all clusters in the list and get common mutual common part
            current_common_part = self._get_common_part_of_clusters(clusters_for_comparison)

            # Remember common part with maximum length
            if len(current_common_part) > max_length_of_common_part:
                max_length_of_common_part = len(current_common_part)
                max_common_part = current_common_part

        return max_common_part


