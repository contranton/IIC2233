from collections import deque, namedtuple
from termcolor import colored
from abc import ABC, abstractmethod

from colorama.ansi import clear_screen as CLS

from typing import Tuple

"""
Defines menu systems to be used for user interaction and info display
"""


def _validate_num_range(self, n_input):
    pass


MenuItem = namedtuple("MenuItem", "option function")


def wrap_init(init):
    """
    Wraps init in super's pre and post initialization

    This allows a menu subclass to comfortably define options and
    functions in its own init while allowing default behavior from
    the super classes
    """
    def _(cls, *args, **kwargs):
        super(cls.__class__, cls).__init__(*args, **kwargs)
        init(cls)
        super(cls.__class__, cls)._set_items()
    return _


class Menu(ABC):
    """Main class for menu display and navigation

    A menu consists of a title, a list of choosable items, and a
    message at the bottom stating the output of some previous
    operation and a user prompt.

    items consists in a deque whose entries are a MenuItem namedtuple,
    with fields 'option' and 'function', where 'option' is the message
    display in the menu list and 'function' is a callable executed on
    selecting said option.

    Item addition is performed through _add_item, which ensures that
    the default option to quit the current menu is always available as
    the last one in the list.
    """
    def __init__(self):

        super().__init__()
        
        # Printed at the top in a special color
        self.title = "Un Menú"

        # Tells the user what to do!
        self.prompt = "Elige una opción"

        # Main text body of the menu. Can use termcolor's colored function to
        # include particular coloration
        self.content = ""

    def __str__(self):
        """
        CLS calls the ansi code to clear the terminal screen, keeping the
        title consistently at the top of the console and other items
        consistently placed
        """
        s = CLS()
        s += colored("--"*10 + "\n", 'cyan', attrs=('bold',))
        s += "\n".join([self.title,
                        self.content,
                        "\n"])
        return s

    @abstractmethod
    def _validate_input(self) -> Tuple[bool, str, callable]:
        """Ensures the input is valid for the specified menu type"""
        pass

    def _interact(self, message=""):
        """ Allow the user to pick an option and execute its associated function

        prompt is displayed always in the user input line, and
        message is displayed only when input has failed
        """

        print(self)
        print("\n" + message if message != "" else "")
        print(colored(self.prompt, 'yellow', attrs=('bold',)))
        choice = input()
        success, msg, function = self._validate_input(choice)
        if not success:
            return self._interact(message="Input inválido. " + msg)
        else:
            # All menus must effectively return callables, using lambdas
            # in case the menus are simply used for data entry.
            return function()

    def run(self):
        """Main execution method, best if called only from main menu
        
        Submenus must be defined within each subfunction, such that menus
        are recursively entered until they return False and the previous
        menu becomes active
        """

        # Will behave as a loop recursively until the last menu is exited
        return self._interact()


class NumericalChoiceMenu(Menu):
    """Menu for selecting items from an item list

    Only menu type with options[] and functions[]
    """
    def __init__(self, **kwargs):
        super(NumericalChoiceMenu, self).__init__(**kwargs)

        self.content = "Las " + colored("opciones", 'yellow') + " son:"
        
        # NamedTuple is wrapped in another tuple to
        # fit as a complete unit in deque
        self.items = deque((MenuItem(option="Volver al menu anterior",
                                     function=lambda: False),))
    
    def _set_items(self):
        # Add the options and functions defined in the init to the items list
        for option, function in zip(self.options, self.functions):
            self._add_item(option, function)
        self.options.append("Volver al menu anterior")

    def __str__(self):
        s = super().__str__()
        s += "\n".join(["%i) %s" % (i+1, text)
                        for i, text in enumerate(self.options)])
        return s

    def _add_item(self, _option, _function):
        self.items.appendleft(MenuItem(option=_option, function=_function))

    def _validate_input(self, value):
        choices = range(len(self.options))
        try:
            value = int(value) - 1
            if value in choices:
                function = self.items[value].function

                return (True, "", function)
            else:
                return (False,
                        "El valor escogido no está dentro del rango válido",
                        0)
        except ValueError:
            return (False,
                    "El valor ingresado no es un número",
                    0)


class TextInputMenu(Menu):
    """Menu for textual value entry

    Forbidden_input is used to ensure no duplicate names are created
    """
    def __init__(self, **kwargs):
        super(TextInputMenu, self).__init__(**kwargs)
        self.forbidden_input = []

    def _validate_input(self, text) -> Tuple[bool, str, callable]:
        if text not in self.forbidden_input:
            return (True, "", lambda: text)
        return (False,
                "Nombre no disponible",
                0)


class YesNoMenu(Menu):
    """Menu for 'yes' or 'no' boolean selection"""
    def __init__(self, **kwargs):
        super(YesNoMenu, self).__init__(**kwargs)

    def _validate_input(self, text):
        if text.lower() not in ["si", "no"]:
            return (False, "Opción inválida", 0)
        else:
            value = {"si": True, "no": False}[text.strip().lower()]
            return (True, "", lambda: value)
        
