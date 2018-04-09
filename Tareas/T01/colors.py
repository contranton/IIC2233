try:
    from termcolor import colored
except ImportError:
    def colored(text, *args):
        return text
import colorama

# Ensure colors are nice always instead of ugly ansi codes
colorama.init(convert=True)


def red(text):
    return colored(str(text), "red", attrs=('bold',))


def green(text):
    return colored(str(text), "green")


def cyan(text):
    return colored(str(text), "cyan", attrs=('bold',))


def yellow(text):
    return colored(str(text), "yellow")


def magenta(text):
    return colored(str(text), "magenta", attrs=('bold',))
