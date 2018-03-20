from collections import deque, namedtuple
from termcolor import colored
from abc import ABC

"""
Defines menu systems to be used for user interaction and info display
"""


def _validate_num_range(self, n_input):
    pass


MenuItem = namedtuple("MenuItem", "option function")


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

    Menu types are 0, 1, or 2:

        - 0 is a numerical choice menu, in which menu items
        are enumerated and the only valid input is one such number.

        - 1 is a text input menu, in which any valid text string works

        - 2 is a yes/no menu, in which either 'y', 'n', 'c' are valid

    """
    def __init__(self, title, menu_type=0, options=[], functions=[]):

        # Printed at the top in a special color
        self.title = title

        # Main text body of the menu. Can use termcolor's colored function to
        # include particular coloration
        self.content = "The " + colored("options", 'yellow') + " are:"

        # NamedTuple is wrapped in another tuple to
        # fit as a complete unit in deque
        self.items = deque((MenuItem(option="Volver al menu anterior",
                                     function=lambda: False),))

        # Add the options and functions passed in as constructor arguments
        for option, function in zip(options, functions):
            self._add_item(option, function)

    def __str__(self):
        s = "\n".join([self.title, self.content])
        return s

    def _add_item(self, _option, _function):
        self.items.appendleft(MenuItem(option=_option, function=_function))

    @abstractmethod
    def _validate_input(self):
        """Ensures the input is valid for the specified menu type"""
        pass

    @abstractmethod
    def _interact(self):
        """ Allow the user to pick an option and execute its associated function

        prompt is displayed always in the user input line, and
        message is displayed only when input has failed
        """

        pass
