from termcolor import colored
import colorama

# Ensure colors are nice always
colorama.init()


def red(text):
    return colored(text, "red", attrs=('bold',))


def green(text):
    return colored(text, "green", attrs=('bold',))


def cyan(text):
    return colored(text, "cyan", attrs=('bold',))


def yellow(text):
    return colored(text, "yellow", attrs=('bold',))


def magenta(text):
    return colored(text, "magenta", attrs=('bold',))

