class OutFiles:
    out_folder = "../out_data/"
    centroids_custom = out_folder + "centroids_custom_check.txt"
    centroids_embedded = out_folder + "centroids_embedded_check.txt"


class OutputWriter:

    def write_rewrite(self, filename, data):
        self.write(filename, data, 'w')

    def write_append(self, filename, data):
        self.write(filename, data, 'a')

    def write(self, filename, data, mode):
        with open(filename, mode) as out_file:
            out_file.write(data)
