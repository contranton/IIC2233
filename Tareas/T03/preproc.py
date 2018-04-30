import re

from fileio import read_file


def clean_html(string):
    """
    Matches text enclosed in tag symbols and replaces it by an empty string

    Items in the database aren't always enclosed in matching tags as
    <b> </b>, quite often having single tags like <p> without matches.

    The following regexp was developed by yours truly using the aid of
    regexr.com
    """
    return re.sub(re.compile(r"<(.+?(?=>)>)"), "",  string)


def is_bot(string):
    words = string.split(" ")
    if len(words) < 6 or len(words) > 84:
        return False
    counts = [{i: words.count(i)} for i in read_file("vocabulary.txt")]
    if sum(map(lambda x: x != 0, counts.values())) < 4:
        return False
    if not any(counts.values()) > 3:
        return False
    return True


if __name__ == '__main__':
    a = clean_html("Hola <a>SACAME DE AQUI</a> Mundo!<b> UH OH</b> "
                   "Habia un segundo tag :S")
