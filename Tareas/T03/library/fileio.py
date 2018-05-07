import csv


def read_csv(path):
    """
    Returns a generator with every line in the file

    TODO: Is this safe for the context manager?
    """
    with open(path, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"',
                            quoting=csv.QUOTE_ALL,
                            skipinitialspace=True)
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


def write_csv(path, iterable, header=()):
    with open(path, 'w', encoding="utf-8", newline="") as f:
        writer = csv.writer(f, dialect="excel",
                            delimiter=",", quotechar='"')
        writer.writerow(header)
        writer.writerows(iterable)
