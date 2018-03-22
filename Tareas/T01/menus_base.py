from termcolor import colored
from abc import ABC, abstractmethod

from colorama.ansi import clear_screen as CLS

from typing import Tuple

"""
Defines menu systems to be used for user interaction and info display

From the Abstract class Menu are defined:
    - NumericalChoiceMenu: Menu where any choice consists of a number in a list
    - TextInputMenu: Menu where expected input is some text
    - YesNoMenu: Menu where a boolean reply is expected

"""


class Menu(ABC):
    """Main class for menu display and navigation

    A menu consists of a title, a list of choosable items, and a
    message at the bottom stating the output of some previous
    operation and a user prompt.

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
        placed predictably
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
        """Main execution method for a menu which return a subfunction or value

        Submenus must be defined within each subfunction, such that menus
        are recursively entered until they return False and the previous
        menu becomes active
        """

        # Will behave as a loop recursively until the last menu is exited
        while self._interact():
            continue
        return


class NumericalChoiceMenu(Menu):
    """Menu for selecting items from an item list

    Only menu type with options[] and functions[]

    'items' consists of a deque whose entries are a MenuItem namedtuple,
    with fields 'option' and 'function', where 'option' is the message
    display in the menu list and 'function' is a callable executed on
    selecting said option.

    Item addition is performed through _add_item, which ensures that
    the default option to quit the current menu is always available as
    the last one in the list.
    """
    def __init__(self, **kwargs):
        super(NumericalChoiceMenu, self).__init__(**kwargs)

        # Specifies whether one can return to this menu
        self.is_main = False

        self.content = "Las " + colored("opciones", 'yellow') + " son:"

    def _set_items(self):
        # DEPRECATED: Was once used to add items to deque, no longer used
        # Remove the decorator as well, bruh
        self.options.append("Volver al menu anterior")
        self.functions.append(lambda: False)

    def __str__(self):
        s = super().__str__()
        s += "\n".join(["%i) %s" % (i+1, text)
                        for i, text in enumerate(self.options)])
        return s

    def _validate_input(self, value):
        choices = range(len(self.options))
        try:
            value = int(value) - 1
            if value in choices:
                function = self.functions[value]

                return (True, "", function)
            else:
                return (False,
                        "El valor escogido no está dentro del rango válido",
                        0)
        except ValueError:
            return (False,
                    "El valor ingresado no es un número",
                    0)

    def run(self):
        if self.is_main:
            return super().run()
        else:
            return self._interact()


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

    def run(self):
        return self._interact()


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
        
    def run(self):
        return self._interact()
