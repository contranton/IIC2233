from menus_base import (NumericalChoiceMenu,
                        NumericalInputMenu,
                        TextInputMenu,
                        YesNoMenu,
                        AreYouSureMenu,
                        InfoMenu)
from termcolor import colored, cprint
from time import sleep

from universe import Planet, Galaxy, COSTO_CUARTEL, COSTO_TORRE


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
        
        functions = [self.create_galaxy,
                     self.modify_galaxy,
                     self.query_galaxy,
                     self.play_galaxy,
                     self.quit_]

        self.items = options, functions

    def create_galaxy(self):
        return CreateGalaxyMenu(self.universe).run()

    def modify_galaxy(self):
        return ModifyGalaxyMenu(self.universe).run()

    def query_galaxy(self):
        return QueryGalaxyMenu(self.universe).run()

    def play_galaxy(self):
        return PlayGalaxyMenu(self.universe).run()
        
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

    def _choose_unconquered_planet(self, menu_title, data_attr=None):
        """
        Prompts selection of an unconquered planet for editing

        Menu_title displays the selection prompt, and data_attr is a field
        name belonging to the Planet class, e.g. "soldados", "_tasa_deuterio",
        "tasa_deuterio" (affected by economy level), "evolucion", etc
        """
        menu = NumericalChoiceMenu()
        menu.title = menu_title
        options = [n for n, p in self.galaxy.planets.items()
                   if not p.conquistado]
        if data_attr:
                # We use getattr to be able to access class properties
                opt_data = [": %i" % getattr(p, data_attr)
                            for p in self.galaxy.planets.values()
                            if not p.conquistado]
        else:
                opt_data = []

        functions = [None]*len(options)

        menu.items = (options, functions, opt_data)

        if len(menu.options) == 0:
            print("Esta galaxia no posee planetas sin conquistar")
            input("Pulsa para continuar...")
            return None

        planet = menu.run()
        return self.galaxy.planets[planet]

    def increase_mins_rate(self):

        title = "Elige un planeta para incrementar su tasa de minerales"
        planet = self._choose_unconquered_planet(title, "tasa_minerales")
        if not planet:
            # Returned only if galaxy doesn't have valid planets
            return True

        num_range = (0, 10 - planet.tasa_minerales)
        num_entry_menu = NumericalInputMenu(num_range)

        planet.tasa_minerales += num_entry_menu.run()

        return True

    def increase_deut_rate(self):

        title = "Elige un planeta para incrementar su tasa de deuterio"
        planet = self._choose_unconquered_planet(title, "tasa_deuterio")
        if not planet:
            # Returned only if galaxy doesn't have valid planets
            return True

        num_range = (0, 15 - planet.tasa_deuterio)
        num_entry_menu = NumericalInputMenu(num_range)

        planet.tasa_deuterio += num_entry_menu.run()

        return True

    def add_soldiers(self):
        title = "Elige un planeta para añadir soldados"
        planet = self._choose_unconquered_planet(title, "soldados")
        if not planet:
            return True

        num_range = (0, planet.max_soldados - planet.soldados)
        num_entry_menu = NumericalInputMenu(num_range)

        planet.soldados += num_entry_menu.run()

        return True

    def add_wizards(self):
        title = "Elige un planeta para añadir magos"
        planet = self._choose_unconquered_planet(title, "soldados")
        if not planet:
            return True

        if not planet.raza.has_mago:
            print("Este planeta no es capaz de tener magos (Raza %s)" %
                  planet.raza.name)
            input("Pulsa para continuar...")
            return True

        num_range = (0, planet.max_magos - planet.magos)
        num_entry_menu = NumericalInputMenu(num_range)

        planet.magos += num_entry_menu.run()

        return True


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
                s_pc.append("\t%s (Evolucion: %0.2f)" % (p.nombre,
                                                         p.evolucion))
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
                                      colored("Evolucion\t", 'red',
                                              attrs=('bold',)) +\
                                      colored("Galaxia\t", 'cyan',
                                              attrs=("bold",))

        # Make menu options
        planets_list = [(p, p.galaxia.nombre)
                        for g in self.universe.galaxies_list
                        for p in g.planets_list]

        planets_list.sort(key=lambda t: (t[1], -t[0].evolucion))

        options = [p.nombre for p, g in planets_list]
        functions = [lambda p=p: p for p, g in planets_list]
        opt_data = [colored("\t%0.2f" % p.evolucion, 'red',
                            attrs=('bold',)) +
                    colored("\t(%s)" % g, 'cyan',
                            attrs=('bold',))
                    for p, g in planets_list]

        planet_choose_menu.items = (options, functions, opt_data)

        # Run menu to select planet
        planet = planet_choose_menu.run()

        info_menu = InfoMenu(title="Información acerca de %s\n" %
                             planet.nombre)
        info_menu.content = str(planet)
        info_menu.run()

        return True

    def best_galaxy(self):
        galaxies = list(filter(lambda x: len(x.planets_list) >= 3,
                               self.universe.galaxies_list))

        if len(galaxies) == 0:
            input("No hay ninguna galaxia con por lo menos 3 planetas!")
            return True

        # Is the 80 character limit strictly enforced?
        best_galaxy =\
            sorted(galaxies,
                   key=lambda g:
                   sum([p.evolucion for p in g.planets_list])
                   / len(g.planets_list))[0]

        info_menu = InfoMenu(title="La mejor galaxia es:")
        info_menu.content = str(best_galaxy)
        info_menu.run()

        return True

    def planet_ranking(self):
        planets = [p for g in self.universe.galaxies_list
                   for p in g.planets_list]

        planets.sort(key=lambda p: p.evolucion, reverse=True)

        s = []
        template = "{0}) " + colored("{1:12}", 'green', attrs=('bold',)) +\
                   "{2:10}  en " +\
                   colored("{3:20}", 'cyan', attrs=('bold',)) +\
                   "Evolucion: " + colored("{4:.2f}", 'red', attrs=('bold',))
        for i, p in enumerate(planets[:min(5, len(planets))]):
            s.append(template.format(i + 1, p.nombre, "(%s)" % p.raza.name,
                                     p.galaxia.nombre, p.evolucion))

        info_menu = InfoMenu(title="Los mejores planetas:")
        info_menu.content = "\n".join(s)
        info_menu.run()

        return True


class PlayGalaxyMenu(NumericalChoiceMenu):
    def __init__(self, universe):
        super().__init__()
        self.universe = universe
        self.is_main = True
        self.galaxy = None

    def choose_galaxy(self):
        choose_galaxy_menu = NumericalChoiceMenu()
        choose_galaxy_menu.title = "Escoge una galaxia para jugar"
        choose_galaxy_menu.items = ([g.nombre
                                     for g in self.universe.galaxies_list], [])

        galaxy_name = choose_galaxy_menu.run()

        self.galaxy = self.universe.galaxies[galaxy_name]

        self.title = "Jugando con la galaxia %s" % galaxy_name
        
        options = ["Visitar planeta", "Escribir cambios"]
        functions = [self.visit_planet, self.write_changes]

        self.items = (options, functions)
        self._add_return_option()
        
    def visit_planet(self):
        menu = NumericalChoiceMenu()
        
        menu.title = "Elije un planeta a visitar"

        options = [p.nombre for p in self.galaxy.planets_list]
        functions = [lambda x=p: x for p in self.galaxy.planets_list]
        opt_data = [{True: "Conquistado", False: "Sin conquistar"}
                    [p.conquistado] for p in self.galaxy.planets_list]
        menu.items = (options, functions, opt_data)
        menu._add_return_option()

        planet = menu.run()
        return planet

    def run(self):
        if not self.galaxy:
            self.choose_galaxy()
        
        planet = self.visit_planet()

        if not planet:
            # If user has chosen to go back without selecting a planet
            return True
        
        if planet.conquistado:
            _ = VisitConqueredPlanetMenu(planet).run()
        else:
            _ = VisitUnconqueredPlanetMenu(planet).run()
        if _:
            return self.run()
        else:
            return True
        

    def write_changes(self):
        pass


class VisitPlanetMenu(NumericalChoiceMenu):
    def __init__(self, planet):
        super().__init__()
        self.is_main = True

        self.planet = planet
        
    @property
    def title(self):
        return (self._title + "\nRecursos disponibles:"
                "Minerales: %i\tDeuterio: %i" % (self.planet.galaxia.minerales,
                                                 self.planet.galaxia.deuterio))

    @title.setter
    def title(self, value):
        self._title = value
        
    def run(self):
        # IMPLEMENT ARCHMAGE AND ASTEROID EVENTS
        return super().run()


class VisitConqueredPlanetMenu(VisitPlanetMenu):

    def __init__(self, planet):
        super().__init__(planet)

        self.title = "Visitando planeta conqusitado %s" % self.planet.nombre

        options = ["Construir edificios",
                   "Generar unidades",
                   "Recolectar recursos",
                   "Implementar mejoras"]

        functions = [self.build,
                     self.create_units,
                     self.get_resources,
                     self.make_improvements]

        self.items = (options, functions)
        self._add_return_option()

    def build(self):
        menu = NumericalChoiceMenu()
        menu.title = super().title + "\nConstruyendo nuevos edificios"
        has_c, has_t = self.planet.cuartel, self.planet.torre
        mins, deut = (self.planet.galaxia.minerales,
                      self.planet.galaxia.deuterio)
        options = ["Cuartel", "Torre"]
        functions, labels = [[], []]
        if has_c:
            labels.append("\tConstruido")
            functions.append(self._already_purchased)
        elif mins < COSTO_CUARTEL.mins or deut < COSTO_CUARTEL.deut:
            labels.append("\tInsuficientes Recursos")
            functions.append(self._insufficient)
        else:
            labels.append("\tConstruir")
            functions.append(self._buy_cuartel)

        if has_t:
            labels.append("\tConstruido")
            functions.append(self._already_purchased)
        elif mins < COSTO_TORRE.mins or deut < COSTO_TORRE.deut:
            labels.append("\tInsuficientes Recursos")
            functions.append(self._insufficient)
        else:
            labels.append("\tConstruir")
            functions.append(self._buy_torre)

        menu.items = (options, functions, labels)
        return menu.run()

    def _already_purchased(self):
        menu = InfoMenu(title="Edificio ya está construido")
        return menu.run()

    def _buy_cuartel(self):
        if AreYouSureMenu(title="Comprando Cuartel").run():
            self.planet.cuartel = True
            self.planet.galaxia.minerales -= COSTO_CUARTEL.mins
            self.planet.galaxia.deuterio -= COSTO_CUARTEL.deut

        return True

    def _buy_torre(self):
        if AreYouSureMenu(title="Comprando Torre").run():
            self.planet.torre = True
            self.planet.galaxia.minerales -= COSTO_TORRE.mins
            self.planet.galaxia.deuterio -= COSTO_TORRE.deut

        return True

    def _insufficient(self):
        return InfoMenu(title="Insuficientes recursos").run()

    def create_units(self):
        pass

    def get_resources(self):
        pass

    def make_improvements(self):
        pass


class VisitUnconqueredPlanetMenu(VisitPlanetMenu):

    def __init__(self, planet):
        super().__init__(planet)

        self.title = "Visitando planeta no conquistado %s" % self.planet.nombre

        options = ["Comprar planeta",
                   "Invadir planeta"]

        functions = [self.purchase,
                     self.invade]

        self.items = (options, functions)
        self._add_return_option()

    def purchase(self):
        mins, deut = (self.planet.galaxia.minerales,
                      self.planet.galaxia.deuterio)
        if mins > 1000000 and deut > 500000:
            menu = AreYouSureMenu("Comprando planeta %s" % self.planet.nombre)
            if menu.run():
                self.planet.conquistado = True
        else:
            menu = InfoMenu()
            menu.title = "Insuficientes recursos"
            menu.content = ("Necesitas 1.000.000 minerales y 500.000 deuterio"
                            " para comprar el planeta.\n\nActualmente tienes"
                            " %i minerales y %i deuterio. Intenta colectar"
                            " recursos de otros planetas!" % (mins, deut))
            menu.run()

        return True
                

    def invade(self):
        menu = AreYouSureMenu("A punto de invadir planeta %s" %
                              self.planet.nombre)
        if menu.run():
            input("WAAAAAR")

        return True


if __name__ == '__main__':
    import colorama;
    colorama.init()
    print(colorama.Style.BRIGHT)

    from universe import Universe
    m = MainMenu(Universe())
    m.run()
