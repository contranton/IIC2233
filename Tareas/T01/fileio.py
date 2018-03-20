from collections import namedtuple
from datetime import datetime


def parse_entry_type(datum, type_):
    if type_ == "string":
        return str(datum)
    elif type_ == "int":
        return int(datum)
    elif type_ == "bool":
        return bool(datum)
    else:
        return datetime.strptime(datum, "%Y-%m-%d %H:%M:%S")


def _read_csv(filename):

    # Turns ..\blah\blah2\galaxias.csv into "Galaxia"
    content_name = filename.split("\\")[-1].split(".")[-2][:-1].title()

    with open(filename, 'r') as f:
        lines = [line.strip().split(", ") for line in list(f)]
        header = lines[0]

        # Raymond Hettinger twitter tips for the win!
        # Separates header names and types into separate lists
        names, types = list(zip(*[s.split(": ") for s in header]))

        Entry = namedtuple(content_name, names)
        data = []

        for line in lines[1:]:
            values = [parse_entry_type(val_str, types[i])
                      for i, val_str in enumerate(line)]
            data.append(Entry(*values))
    return data


def read_galaxies():
    return _read_csv("archivos\\galaxias.csv")


def read_planets():
    return _read_csv("archivos\\planetas.csv")
