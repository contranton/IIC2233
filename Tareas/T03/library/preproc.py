import re

from library.fileio import read_csv, write_csv
from library.databases import read_reviews


def clean_html(string):
    """
    Matches text enclosed in tag symbols and replaces it by an empty string

    Items in the database aren't always enclosed in matching tags as
    <b> </b>, quite often having single tags like <p> without matches.

    The following regexp was developed by yours truly using the aid of
    regexr.com
    """
    string = string.replace(r"&nbsp;", "")
    return re.sub(re.compile(r"<(.+?(?=>)>)"), "",  string)


def is_bot(string):
    words = re.split("[ ,.;?¿!¡]", string)
    if len(words) < 6 or len(words) > 84:
        return False
    counts = {i[0]: words.count(i[0]) for i in read_csv("vocabulary.txt")}

    if sum(map(lambda x: x != 0, counts.values())) < 4:
        return False
    if not any(map(lambda x: x >= 3, counts.values())):
        return False
    return True


def preprocess_comments():
    reviews = map(lambda r: "\"{}\"".format(clean_html(r[1])),
                  filter(lambda r: not is_bot(r[1]), read_reviews()))
    write_csv("reviews_clean.csv", list(enumerate(reviews)),
              header=("id", "review"))

if __name__ == '__main__':
    a = clean_html("Hola <a>SACAME DE AQUI</a> Mundo!<b> UH OH</b> "
                   "Habia un segundo tag :S")
