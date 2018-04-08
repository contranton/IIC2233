from abc import ABC, abstractmethod
from collections import namedtuple

from colorama.ansi import clear_screen as CLS
from colors import red, green, cyan, yellow

"""
Defines menu systems to be used for user interaction and info display

From the Abstract class Menu are defined:
    - NumericalChoiceMenu: Menu where any choice consists of a number in a list
    - TextInputMenu: Menu where expected input is some text
    - YesNoMenu: Menu where a boolean reply is expected

"""

menu_item = namedtuple("Item", "option function opt_data")


class Menu(ABC):
    """Main class for menu display and navigation

    A menu consists of a title, a list of choosable items, and a
    message at the bottom stating the output of some previous
    operation and a user prompt.

    """
    def __init__(self, title="Un Menú", prompt="Elige una opción"):

        super().__init__()

        # Specifies whether or not this menu can be come back to
        self.is_main = False
        
        # Printed at the top in a special color
        self.title = title

        # Tells the user what to do!
        self.prompt = prompt

        # Main text body of the menu. Can use color functions to
        # include particular coloration
        self.content = ""

    def __str__(self):
        """
        CLS calls the ansi code to clear the terminal screen, keeping the
        title consistently at the top of the console and other items
        placed predictably
        """
        s = CLS()
        s += cyan("--"*20 + "\n")
        s += self.title + "\n"
        s += self.content + "\n" if self.content != "" else ""
        return s

    @abstractmethod
    def _validate_input(self):
        """Ensures the input is valid for the specified menu type

        Returns a tuple(bool success, str error_message, callable function)
        """
        pass

    def _interact(self, message=""):
        """ Allow the user to pick an option and execute its associated function

        prompt is displayed always in the user input line, and
        message is displayed only when input has failed
        """

        print(self)
        print("\n" + message if message != "" else "")
        print(yellow(self.prompt))
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
        return True


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
        self.content = "Las opciones son:"
        self.prompt = "Elige una opción"

        self.items = (list(), list())

        super(NumericalChoiceMenu, self).__init__(**kwargs)

    def _add_return_option(self):
        self.items[len(self.items)] = menu_item(option="Volver",
                                                function=lambda: False,
                                                opt_data="")

    def _remove_quit_item(self):
        """
        Used only in a Principal Menu where the 'return' option is redundant
        """
        self._items.pop(len(self.items)-1)

    @property
    def options(self):
        return [item.option for item in self.items.values()]

    @property
    def functions(self):
        return [item.function for item in self.items.values()]

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, item_info):
        """
        item_info is a 3-tuple containing lists of equal length that describe
        the menu options

        Options: Strings that describe a function
        Functions: function objects executed upon selection
                   If a function is None, it will return the option name
        Opt_data: For when options must display additional information
                   that mustn't be returned with a None function
        """

        # Unpack item info tuple
        try:

            options, functions, *opt_data = item_info

            # For some reason the optionals get wrapped in another list
            if opt_data:
                opt_data = opt_data[0]
        except ValueError:
            raise ValueError("Menu 'items' setter received "
                             "incorrect info tuple")

        # opt_data is Optional, and default values are empty strings
        if len(opt_data) == 0:
            opt_data = [""] * len(options)

        # By default, empty functions maps to None
        if len(functions) == 0:
            functions = [None] * len(options)

        # All lists must have the same length
        if len(options) != len(functions) or len(functions) != len(opt_data):
            raise ValueError("Menu 'item' lists have different lenghts")

        # A function left as None returns the name of the chosen option
        for i, f in enumerate(functions):
            if f is None:
                # It's necessary to add a default value to the lambda,
                # as it stores references to the value and not the
                # value itself. For example,
                #
                # [x() for x in [lambda: m for m in [1,2,3]]]
                # >>> [3, 3, 3]
                functions[i] = lambda x=options[i]: x

        self._items = {i: menu_item(option=opt, function=func, opt_data=dat)
                       for i, (opt, func, dat)
                       in enumerate(zip(options, functions, opt_data))}

        self._add_return_option()

    def __str__(self):
        s = super().__str__() + "\n"
        s += "\n".join(["%i) %s %s" % (i+1, item.option, item.opt_data)
                        for i, item in self.items.items()])
        return s

    def _validate_input(self, value):
        choices = range(len(self.options))
        try:
            value = int(value) - 1

            # If number is in range
            if value in choices:
                return (True, "", self.items[value].function)
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
            # Continues a main loop
            return super().run()
        else:
            # Returns a value and quits
            return self._interact()


class TextInputMenu(Menu):
    """Menu for textual value entry

    Forbidden_input is used to ensure no duplicate names are created
    """
    def __init__(self, **kwargs):
        super(TextInputMenu, self).__init__(**kwargs)
        self.forbidden_input = []

    def _validate_input(self, text):
        if text not in self.forbidden_input:
            return (True, "", lambda: text)
        return (False,
                "Nombre no disponible",
                0)

    def run(self):
        return self._interact()


class NumericalInputMenu(Menu):
    """
    Menu for inputting a number between specified maximum ranges
    """
    def __init__(self, num_range, accept_floats=False):
        super().__init__()
        self.accept_floats = accept_floats
        self.num_range = num_range

        self.title = "Ingresa un valor%s dentro del rango especificado: " %\
                     {False: red(" entero"),
                      True: " cualquiera"}[accept_floats]
        self.content = "Minimo: %s\n" % green(str(num_range[0])) +\
                       "Maximo: %s" % green(str(num_range[1]))

    def _validate_input(self, text):
        text = text.replace(",", ".")
        try:
            val = float(text)
            if not self.accept_floats:
                if val != int(val):
                    return (False,
                            "Este menú no acepta decimales."
                            "Ingresa un número entero",
                            0)
                else:
                    return (True, "", lambda x=int(val): x)

            else:
                return (True, "", lambda x=val: x)

        except ValueError:
            return (False,
                    "El valor ingresado no es un número",
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


class AreYouSureMenu(YesNoMenu):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = "Seguro? (si/no): "

    def run(self):
        return self._interact()


class InfoMenu(Menu):
    def __init__(self, title="Informacion"):
        """Menu for info display with a unique input option for returning"""
        self.title = title
        self.content = ""
        self.prompt = "Pulsa para continuar..."

    def _validate_input(self, _):
        return (True, "", lambda: False)

if __name__ == '__main__':
    M = NumericalChoiceMenu()

    options = "Op1 Op2 Op3".split()
    functions = "Foo1 FOo2 FOo3".split()
    opt_data = "? ! Wow".split()

    M.items = (options, functions)

    print(M.items)

    M.items = (options, functions, opt_data)

    print(M.items)
