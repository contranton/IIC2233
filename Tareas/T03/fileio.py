import csv


def read_csv(path):
    """
    Returns a generator with every line in the file

    TODO: Is this safe for the context manager?
    """
    with open(path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        next(reader)
        for line in reader:
            try:
                yield list(map(str.strip, line))
            except Exception:
                print("An error has ocurred on a generator holding the "
                      "resource ", path)
                import traceback; traceback.print_exc(-1)
                f.close()
                break
