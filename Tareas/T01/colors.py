from termcolor import colored
import colorama

# Ensure colors are nice always instead of ugly ansi codes
colorama.init(convert=True)


def red(text):
    return colored(text, "red", attrs=('bold',))


def green(text):
    return colored(text, "green")


def cyan(text):
    return colored(text, "cyan", attrs=('bold',))


def yellow(text):
    return colored(text, "yellow")


def magenta(text):
    return colored(text, "magenta", attrs=('bold',))
