from menus_base import (NumericalChoiceMenu,
                        TextInputMenu,
                        YesNoMenu,
                        AreYouSureMenu,
                        InfoMenu)
from termcolor import colored, cprint
from time import sleep

from universe import Planet, Galaxy


def make_planet_dialog(universe, parent_galaxy):

        # Choose planet name
        planet_name_menu = TextInputMenu()
        planet_name_menu.title = "Creando nuevo planeta"
        planet_name_menu.prompt = "Elige el nombre del planeta: "

        forbidden_input = {p.nombre for g in universe.galaxies_list
                           for p in g.planets_list}

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
        planet_race_menu.items = (["Maestro", "Aprendiz", "Asesino"], [])

        planet_race = planet_race_menu.run()

        return Planet(nombre=planet_name,
                      raza=planet_race,
                      galaxia=parent_galaxy)


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

        options = ["Crear Galaxia",
                   "Modificar Galaxia",
                   "Consultar Galaxia",
                   "Jugar con Galaxia",
                   "Salir del programa"]
        
        functions = [CreateGalaxyMenu(universe).run,
                     ModifyGalaxyMenu(universe).run,
                     QueryGalaxyMenu(universe).run,
                     PlayGalaxyMenu(universe).run,
                     self.quit_]

        self.items = options, functions
        
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
        self.new_planets = []

    @property
    def str_created_planets(self):
        if not self.new_planets:
            return "Ningún planeta creado hasta ahora"

        s = colored("Planetas creados: \n", 'green', attrs=('bold',))
        s += colored("\n".join(["\t%s (%s)" % (p.nombre, p.raza.name)
                                for p in self.new_planets]),
                     'green')
        return s

    def run(self):

        # Get galaxy name
        galaxy_name = self._interact()

        # Menu for querying planet creation
        create_planet_menu = YesNoMenu()
        create_planet_menu.title = "Editando galaxia %s" %\
                                   colored(galaxy_name, 'red', attrs=('bold',))
        create_planet_menu.content = self.str_created_planets

        create_planet_menu.prompt = "Crear Planeta? (si/no):"

        # Planet creation loop
        while create_planet_menu.run():

            # TODO: Maybe an issue here with new_galaxy setting?
            self.new_planets.append(make_planet_dialog(self.universe,
                                                       parent_galaxy=None))
            # Update the created planet list for printing
            create_planet_menu.content = self.str_created_planets

        # Only create galaxy once at least one planet has been created
        self.new_galaxy = Galaxy(nombre=galaxy_name)
        self.new_galaxy.minerales = 1000
        self.new_galaxy.deuterio = 1000

        # Initialize planets as a dict to easily choose conquered one later
        self.new_galaxy.planets = {}

        # Add created planets and set their parent galaxy
        for p in self.new_planets:
            self.new_galaxy.planets[p.nombre] = p
            p.galaxia = self.new_galaxy

        # Choose conquered planet
        choose_conquered_planet_menu = NumericalChoiceMenu()
        choose_conquered_planet_menu.title = "Elige el planeta a "\
                                             "comenzar conquistado"

        options = list(map(lambda x: x.nombre,
                           self.new_galaxy.planets.values()))
        functions = [lambda x=x: x for x in self.new_galaxy.planets.values()]
        choose_conquered_planet_menu.items = (options, functions)

        conquered_planet = choose_conquered_planet_menu.run()
        conquered_planet.conquistado = True

        # Populate unconquered planets
        # TODO: Do conquered planets have an initial population??
        for p in self.new_galaxy.planets_list:
            if not p.conquistado:
                # Together, these add to 75% of the total population
                ms = int(p.raza.max_pop * 0.45)
                mw = int(p.raza.max_pop * 0.3)
                
                p.soldados = ms
                p.magos = mw

        # Add new galaxy to universe and write changes
        self.universe.galaxies[galaxy_name] = self.new_galaxy
        self.new_galaxy = None
        self.new_planets = []
        self.universe.write_content()
        
        return True


class ModifyGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        super().__init__()
        self.is_main = True

        self.title = ""

        self.universe = universe
        options = ["Agregar Planeta",
                   "Eliminar planeta conquistado",
                   "Aumentar tasa de minerales",
                   "Aumentar tasa de deuterio",
                   "Agregar soldados",
                   "Agregar magos",
                   "Volver"]

        functions = [self.add_planet,
                     self.eliminate_conquered,
                     self.increase_mins_rate,
                     self.increase_deut_rate,
                     self.add_soldiers,
                     self.add_wizards,
                     lambda: False]

        self.items = (options, functions)

        self.galaxy = None

    def run(self):
        choose_galaxy_menu = NumericalChoiceMenu()
        choose_galaxy_menu.title = "Elige la galaxia a modificar: "
        choose_galaxy_menu.items = ([str(g) for g in self.universe.galaxies],
                                    [])

        galaxy_name = choose_galaxy_menu.run()
        self.galaxy = self.universe.galaxies[galaxy_name]

        self.title = "Modificando galaxia "
        self.title += colored(galaxy_name, 'cyan')

        result = super().run()

        # Always write changes on this menu
        self.universe.write_content()
        return result

    def add_planet(self):
        planet = make_planet_dialog(self.universe, self.galaxy)
        self.galaxy.planets[planet.nombre] = planet

        return True

    def eliminate_conquered(self):
        menu = NumericalChoiceMenu()
        menu.title = "Elige un planeta conquistado a eliminar: "
        menu.items = ([n for n, p in self.galaxy.planets.items()
                       if p.conquistado],)

        planet_name = menu.run()

        sure = AreYouSureMenu(title="Eliminando planeta " +
                              colored(planet_name, 'red') +
                              ". ¿Proceder?")
        if sure.run():
            self.galaxy.planets.pop(planet_name)
            self.universe.write_content()

        return True

    def increase_mins_rate(self):
        menu = NumericalChoiceMenu()
        menu.title = "Elige un planeta para incrementar su tasa de minerales: "
        options = [n for n, p in self.galaxy.planets.items()
                   if not p.conquistado]
        opt_data = [": %i" % p._tasa_minerales
                    for p in self.galaxy.planets.values()
                    if not p.conquistado]
        functions = [None]*len(options)

        menu.items = (options, functions, opt_data)

        if len(menu.options) == 0:
            print("Esta galaxia no posee planetas sin conquistar")
            input("Pulsa para continuar...")
            return True

        planet = menu.run()

        # TODO: Numerical entry menu
        self.galaxy.planets[planet].increase_tasa_minerales()

        return True

    def increase_deut_rate(self):
        menu = NumericalChoiceMenu()
        menu.title = "Elige un planeta para incrementar su tasa de deuterio: "
        options = [n for n, p in self.galaxy.planets.items()
                   if not p.conquistado]
        opt_data = [": %i" % p._tasa_deuterio
                    for p in self.galaxy.planets.values()
                    if not p.conquistado]
        functions = [None]*len(options)

        menu.items = (options, functions, opt_data)
        
        if len(menu.items) == 0:
            print("Esta galaxia no posee planetas sin conquistar")
            input("Pulsa para continuar...")
            return True

        planet = menu.run()

        # TODO: Numerical entry menu
        self.galaxy.planets[planet].increase_tasa_deuterio()

        return True

    def add_soldiers(self):
        pass

    def add_wizards(self):
        pass


class QueryGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        super().__init__()
        self.universe = universe
        self.is_main = True

        self.title = "Consultando Galaxias"
        
        options = ["Informacion general",
                   "Informacion de planetas",
                   "Mejor galaxia",
                   "Ranking de planetas",
                   "Volver"]

        functions = [self.general_info,
                     self.planet_info,
                     self.best_galaxy,
                     self.planet_ranking,
                     lambda: False]

        self.items = (options, functions)

    def general_info(self):
        menu = InfoMenu()
        menu.title = "Información General del Universo\n"
        s = []
        for g in self.universe.galaxies_list:
            s_g = [g.nombre]
            s_g.append("Deuterio: %i" % g.deuterio)
            s_g.append("Minerales: %i" % g.minerales)
            
            # s_pc: string_planets_conquered
            s_pc = []
            for p in filter(lambda x: x.conquistado, g.planets_list):
                s_pc.append("\t%s (Evolucion: %0.2f)" % (p.nombre, p.evolucion))
            # Append if conquered planets exist, else say there aren't any
            if s_pc:
                s_g.append("Planetas Conquistados:")
                s_g.append("\n\t".join(s_pc))
            else:
                s_g.append("Sin planetas conquistados")
            s.append("\n\t".join(s_g))
        menu.content = "\n".join(s)
        menu.run()

        return True

    def planet_info(self):
        planet_choose_menu = NumericalChoiceMenu()
        planet_choose_menu.title = "Elige un planeta para ver su información"
        planet_choose_menu.content += "\n\n" +\
                                     "Planeta\t\t" +\
                                     colored("Evolucion\t", 'red') +\
                                     colored("Galaxia\t", 'cyan')
        
        # Make menu options
        planets_list = [(p, p.galaxia.nombre)
                        for g in self.universe.galaxies_list
                        for p in g.planets_list]

        planets_list.sort(key=lambda t: (t[1], -t[0].evolucion))

        options = [p.nombre for p, g in planets_list]
        functions = [lambda p=p: p for p, g in planets_list]
        opt_data = [colored("\t%0.2f" % p.evolucion, 'red') +
                    colored("\t(%s)" % g, 'cyan')
                    for p, g in planets_list]

        planet_choose_menu.items = (options, functions, opt_data)

        # Run menu to select planet
        planet = planet_choose_menu.run()

        info_menu = InfoMenu(title="Información acerca de %s\n" % planet.nombre)
        info_menu.content = str(planet)
        info_menu.run()

        return True

    def best_galaxy(self):
        pass

    def planet_ranking(self):
        pass
        

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
