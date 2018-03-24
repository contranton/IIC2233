from datetime import datetime


def parse_entry_type(datum, type_):
    if type_ in {"string", "str"}:
        return str(datum)
    elif type_ == "int":
        return int(datum)
    elif type_ == "bool":
        return True if datum == "True" else False
    else:
        return datetime.strptime(datum, "%Y-%m-%d %H:%M:%S")


def read_csv(filename):

    # Turns ..\blah\blah2\galaxias.csv into "Galaxia"
    # content_name = filename.split("\\")[-1].split(".")[-2][:-1].title()

    with open(filename, 'r') as f:
        lines = [line.strip().split(", ") for line in list(f)]
        header = lines[0]

        # Raymond Hettinger twitter tips for the win!
        # Separates header names and types into separate lists
        names, types = list(zip(*[s.split(": ") for s in header]))

        kwargs = []
        
        for line in lines[1:]:
            kwargs.append({names[i]: parse_entry_type(val_str, types[i])
                           for i, val_str in enumerate(line)})

    return kwargs


def write_csv(dict_list, filename):
    """Automatically writes variable name and type on header before data

    This method expects all dicts inside the list to have the exact same keys
    and orders them alphabetically into lists for writing
    """
    
    # Get variable names and types
    variables = [(str(k).strip("_"), type(v).__name__)
                 for k, v in sorted(dict_list[0].items(),
                                    key=lambda x: x[0].strip("_")[0])]

    vars_str = (", ".join([": ".join([var, typ]) for var, typ in variables]))

    data = []

    # Turn dict lists into lists of all values
    for entry in dict_list:
        data.append([str(value) for key, value in
                     sorted(list(entry.items()),
                            key=lambda x: x[0].strip("_")[0])])

    data_str = "\n".join([", ".join(entry) for entry in data])

    with open(filename, 'w') as f:
        f.write(vars_str + "\n")
        f.write(data_str + "\n")


def read_galaxies():
    return read_csv("archivos\\galaxias.csv")


def read_planets():
    return read_csv("archivos\\planetas.csv")


if __name__ == '__main__':
    from universe import Universe
    u = Universe()
