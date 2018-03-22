from menus_base import NumericalChoiceMenu, TextInputMenu, YesNoMenu, wrap_init
from termcolor import colored


class MainMenu(NumericalChoiceMenu):
    """Initial welcome and action selection menu"""

    @wrap_init
    def __init__(self):
        self.title = colored("Bienevenido a ChauCraft!",
                             'green',
                             attrs=('bold',))

        self.content = colored("Bienvenido, usuario, a tu universo",
                               'cyan')

        self.prompt = colored(self.prompt, 'yellow')

        self.options = ["Crear Galaxia",
                        "Modificar Galaxia",
                        "Consultar Galaxia",
                        "Jugar con Galaxia"]

        self.functions = [CreateGalaxyMenu().run,
                          ModifyGalaxyMenu().run,
                          QueryGalaxyMenu().run,
                          PlayGalaxyMenu().run]


class CreateGalaxyMenu(TextInputMenu):

    def __init__(self):
        super().__init__()
        self.title = "Creando una nueva galaxia"

        self.prompt = "Ingresa un nombre para la galaxia: "

    def run(self):

        # TODO: Make galaxy
        galaxy_name = self._interact()
        
        choose_planet_menu = YesNoMenu()
        choose_planet_menu.title = "Editando galaxia %s" %\
                                   colored(galaxy_name, 'red', attrs=('bold',))
        choose_planet_menu.prompt = "Crear Planeta? (si/no): "
        
        while choose_planet_menu.run():
            self.make_planet_dialog()

        choose_conquered_planet_menu = NumericalChoiceMenu()
        choose_conquered_planet_menu.title = "Elige el planeta a"\
                                             "comenzar conquistado"

    def make_planet_dialog(self):

        # Choose planet name
        planet_name_menu = TextInputMenu()
        planet_name_menu.title = "Creando nuevo planeta"
        planet_name_menu.prompt = "Elige el nombre del planeta: "

        # TODO: Acquire all planet names in galaxy
        planet_name_menu.forbidden_input = []
        
        planet_name = planet_name_menu.run()

        # Choose planet race
        planet_race_menu = NumericalChoiceMenu()
        planet_race_menu.title = "Creando nuevo planeta"
        planet_race_menu.content = "Elige la raza del planeta"
        planet_race_menu.options = ["Maestro", "Aprendiz", "Asesino"]
        planet_race_menu.functions = [lambda: i
                                      for i in planet_race_menu.options]

        planet_race = planet_race_menu.run()

        # TODO: Assign acquired data to a planet in Universe class

        print(planet_name, planet_race)
        input("Happy?")


class ModifyGalaxyMenu(NumericalChoiceMenu):
    pass


class QueryGalaxyMenu(NumericalChoiceMenu):
    pass


class PlayGalaxyMenu(NumericalChoiceMenu):
    pass


if __name__ == '__main__':
    import colorama;
    colorama.init()
    print(colorama.Style.BRIGHT)
    m = MainMenu()
    m.run()
