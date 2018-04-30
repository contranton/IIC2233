import csv

def read_file(path):
    """
    Returns a generator with every line in the file

    TODO: Is this safe for the context manager?
    """
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=", ", quotechar='"')
        for line in reader:
            try:
                yield line
            except:
                print("An error has ocurred on a generator holding the"
                      "resource ", path)
                f.close()
