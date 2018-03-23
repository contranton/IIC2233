from menus_base import NumericalChoiceMenu, TextInputMenu, YesNoMenu
from termcolor import colored, cprint
from time import sleep

from universe import Planet, Galaxy


class AreYouSureMenu(YesNoMenu):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.prompt = "Seguro? (si/no): "

    def run(self):
        return self._interact()


class MainMenu(NumericalChoiceMenu):
    """Initial welcome and action selection menu"""


    def __init__(self, universe):
        super().__init__()
        self.is_main = True
        self.universe = universe

        self.title = colored("Bienevenido a ChauCraft!",
                             'green',
                             attrs=('bold',))

        self.content = colored("Bienvenido, usuario, a tu universo",
                               'cyan')

        self.prompt = colored(self.prompt, 'yellow')

        self.options = ["Crear Galaxia",
                        "Modificar Galaxia",
                        "Consultar Galaxia",
                        "Jugar con Galaxia",
                        "Salir del programa"]

        self.functions = [CreateGalaxyMenu(universe).run,
                          ModifyGalaxyMenu(universe).run,
                          QueryGalaxyMenu(universe).run,
                          PlayGalaxyMenu(universe).run,
                          self.quit_]

    def quit_(self):
        if AreYouSureMenu(title="Saliendo del programa").run():
            print("Bye!")
            sleep(1)
            return False
        else:
            return True


class CreateGalaxyMenu(TextInputMenu):

    def __init__(self, universe):
        super().__init__()
        self.universe = universe

        self.title = "Creando una nueva galaxia"

        self.prompt = "Ingresa un nombre para la galaxia: "

        self.new_galaxy = None

    @property
    def str_created_planets(self):
        s = colored("Planetas creados: \n", 'green', attrs=('bold',))
        s += colored("\n".join(["\t%s (%s)" % (p.nombre, p.raza.name)
                                for p in self.new_galaxy.planets]), 'green')
        return s

    def run(self):

        galaxy_name = self._interact()
        self.new_galaxy = Galaxy(nombre=galaxy_name)

        choose_planet_menu = YesNoMenu()
        choose_planet_menu.title = "Editando galaxia %s" %\
                                   colored(galaxy_name, 'red', attrs=('bold',))
        choose_planet_menu.content = self.str_created_planets

        choose_planet_menu.prompt = "Crear Planeta? (si/no):"

        while choose_planet_menu.run():
            self.make_planet_dialog()
            # Update the created planet list
            choose_planet_menu.content = self.str_created_planets

        choose_conquered_planet_menu = NumericalChoiceMenu()
        choose_conquered_planet_menu.title = "Elige el planeta a"\
                                             "comenzar conquistado"
        # TODO:
        # choose_conquered_planet_menu.options = Universe.GALAXY.planets
        # conquered_planet = choose_conquered_planet_menu.run()

        # TODO: WRITE TO FILE
        return True

    def make_planet_dialog(self):

        # Choose planet name
        planet_name_menu = TextInputMenu()
        planet_name_menu.title = "Creando nuevo planeta"
        planet_name_menu.prompt = "Elige el nombre del planeta: "

        forbidden_input = {p.nombre for g in self.universe.galaxies
                           for p in g.planets}

        planet_name = planet_name_menu.run()
        while len(planet_name) < 6:
            cprint("El nombre es demasiado corto (minimo 6 caracteres)."
                   "Intenta de nuevo", 'red')
            input("\nPulsa para continuar...")
            planet_name = planet_name_menu.run()
        while planet_name in forbidden_input:
            cprint("El nombre %s ya está utilizado. Elige otro." % planet_name,
                   'red')
            input("\nPulsa para continuar...")
            planet_name = planet_name_menu.run()

        # Choose planet race
        planet_race_menu = NumericalChoiceMenu()
        planet_race_menu.title = "Creando nuevo planeta"
        planet_race_menu.content = "Elige la raza del planeta"
        planet_race_menu.options = ["Maestro", "Aprendiz", "Asesino"]
        planet_race_menu.functions = [lambda: "Maestro",
                                      lambda: "Aprendiz",
                                      lambda: "Asesino"]

        planet_race = planet_race_menu.run()

        # Add planet object
        self.new_galaxy.planets.append(Planet(nombre=planet_name,
                                              raza=planet_race))


class ModifyGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        self.universe = universe


class QueryGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        self.universe = universe


class PlayGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        self.universe = universe


if __name__ == '__main__':
    import colorama;
    colorama.init()
    print(colorama.Style.BRIGHT)

    from universe import Universe
    m = MainMenu(Universe())
    m.run()
