from time import sleep
from random import randrange, sample
from copy import deepcopy
import datetime

from menus_base import (NumericalChoiceMenu,
                        NumericalInputMenu,
                        TextInputMenu,
                        YesNoMenu,
                        AreYouSureMenu,
                        InfoMenu)

from universe import (Planet, Galaxy, COSTO_CUARTEL, COSTO_TORRE,
                      COSTO_MEJORA_ECONOMIA, COSTO_MEJORA_ATAQUE)
from colors import red, green, yellow, cyan
from battle import Battle, Archimago

now = datetime.datetime.now



def make_planet_dialog(universe, parent_galaxy):

        # Choose planet name
        planet_name_menu = TextInputMenu()
        planet_name_menu.title = "Creando nuevo planeta"
        planet_name_menu.prompt = "Elige el nombre del planeta: "

        forbidden_input = {p.nombre for g in universe.galaxies_list
                           for p in g.planets_list}

        planet_name = planet_name_menu.run()

        valid = False
        while not valid:
            if len(planet_name) < 6:
                print(red("El nombre es demasiado corto (minimo 6 caracteres)."
                          "Intenta de nuevo"))
                input("\nPulsa para continuar...")
                planet_name = planet_name_menu.run()
            elif planet_name in forbidden_input:
                print(red("El nombre %s ya está utilizado. Elige otro." %
                          planet_name))
                input("\nPulsa para continuar...")
                planet_name = planet_name_menu.run()
            else:
                valid = True

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

        self.title = green("Bienevenido a ChauCraft!")

        self.prompt = yellow(self.prompt)

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

        self._remove_quit_item()

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

        s = red("Planetas creados: \n")
        s += green("\n".join(["\t%s (%s)" % (p.nombre, p.raza.name)
                              for p in self.new_planets]))
        return s

    def run(self):

        # Get galaxy name
        galaxy_name = self._interact()

        # Menu for querying planet creation
        create_planet_menu = YesNoMenu()
        create_planet_menu.title = "Editando galaxia %s" %\
                                   red(galaxy_name)
        create_planet_menu.content = self.str_created_planets

        create_planet_menu.prompt = "Crear Planeta? (si/no):"

        # Planet creation loop
        while create_planet_menu.run():

            # TODO: Maybe an issue here with new_galaxy setting?
            self.new_planets.append(make_planet_dialog(self.universe,
                                                       parent_galaxy=None))
            # Update the created planet list for printing
            create_planet_menu.content = self.str_created_planets
        else:
            if len(self.new_planets) == 0:
                return True

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

        # User already had a chance to think of adding more planets ;)
        choose_conquered_planet_menu._remove_quit_item()

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
                   "Agregar magos"]

        functions = [self.add_planet,
                     self.eliminate_conquered,
                     self.increase_mins_rate,
                     self.increase_deut_rate,
                     self.add_soldiers,
                     self.add_wizards]

        self.items = (options, functions)

        self.galaxy = None

    def run(self):
        choose_galaxy_menu = NumericalChoiceMenu()
        choose_galaxy_menu.title = "Elige la galaxia a modificar: "
        choose_galaxy_menu.items = ([str(g) for g in self.universe.galaxies],
                                    [])

        galaxy_name = choose_galaxy_menu.run()
        if not galaxy_name:
            return True

        self.galaxy = self.universe.galaxies[galaxy_name]

        self.title = "Modificando galaxia "
        self.title += cyan(galaxy_name)

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
                       if p.conquistado], [])

        planet_name = menu.run()
        if not planet_name:
            return True

        sure = AreYouSureMenu(title="Eliminando planeta " +
                              red(planet_name) +
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
        if not planet:
            return None

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
            # or if user chooses to cancel selection
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
                   "Ranking de planetas"]

        functions = [self.general_info,
                     self.planet_info,
                     self.best_galaxy,
                     self.planet_ranking]

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

        # Make menu options
        planets_list = [(p, p.galaxia.nombre)
                        for g in self.universe.galaxies_list
                        for p in g.planets_list]

        if len(planets_list) == 0:
            InfoMenu("No hay planetas existentes!"
                     " Crea una galaxia primero").run()
            return True

        planets_list.sort(key=lambda t: (t[1], -t[0].evolucion))

        options = [p.nombre for p, g in planets_list]
        longest = len(sorted(options)[-1])
        options = [("{:%i}" % (longest + 5)).format(name) for name in options]
        functions = [lambda p=p: p for p, g in planets_list]
        opt_data = [cyan("\t%0.2f" % p.evolucion) +
                    red("\t(%s)" % g)
                    for p, g in planets_list]

        planet_choose_menu.items = (options, functions, opt_data)

        planet_choose_menu.content += "\n\n" +\
                                      "Planeta" + " "*(longest + 5) +\
                                      cyan("Evolucion\t") +\
                                      red("Galaxia\t")

        # Run menu to select planet
        planet = planet_choose_menu.run()
        if not planet:
            return True

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
        template = "{0}) " + green("{1:12}") +\
                   "{2:10}  en " +\
                   cyan("{3:20}") +\
                   "Evolucion: " + red("{4:.2f}")
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

        self.original_galaxy = None

    def choose_galaxy(self):
        choose_galaxy_menu = NumericalChoiceMenu()
        choose_galaxy_menu.title = "Escoge una galaxia para jugar"
        choose_galaxy_menu.items = ([g.nombre
                                     for g in self.universe.galaxies_list], [])

        galaxy_name = choose_galaxy_menu.run()
        if not galaxy_name:
            return False

        self.galaxy = self.universe.galaxies[galaxy_name]
        self.original_galaxy = deepcopy(self.galaxy)

        self.title = "Jugando con la galaxia %s" % galaxy_name

        options = ["Visitar planeta", "Escribir cambios", "Volver"]
        functions = [self.visit_planet, self.write_changes, self.volver]

        self.items = (options, functions)
        self._remove_quit_item()

        return True

    def visit_planet(self):
        self.wrote_changes = False
        menu = NumericalChoiceMenu()

        menu.title = "Elije un planeta a visitar"

        options = [p.nombre for p in self.galaxy.planets_list]
        functions = [lambda x=p: x for p in self.galaxy.planets_list]
        opt_data = [{True: green("\tConquistado"),
                     False: red("\tSin conquistar")}
                    [p.conquistado] for p in self.galaxy.planets_list]
        menu.items = (options, functions, opt_data)

        planet = menu.run()
        if not planet:
            return True
        elif planet.conquistado:
            VisitConqueredPlanetMenu(planet).run()
        else:
            VisitUnconqueredPlanetMenu(planet).run()
        return self.visit_planet()

    def run(self):
        if not self.galaxy:
            success = self.choose_galaxy()
            if not success:
                # If user has cancelled galaxy selection
                return True

        return super().run()

    def write_changes(self):
        self.universe.write_content()
        self.wrote_changes = True

    def volver(self):
        if not self.wrote_changes:
            if AreYouSureMenu(title="Los cambios no se han guardado y se perderan").run():
                self.galaxy = self.original_galaxy
                return False
            return True
        return False


class VisitPlanetMenu(NumericalChoiceMenu):
    def __init__(self, planet):
        super().__init__()
        self.is_main = True

        self.planet = planet

    @property
    def title(self):
        s = self._title
        temp = ("\nEste planeta posee {solds} soldados y {mags} magos\n" +
                "Su raza es {race}\n" +
                "{has_c} cuartel y {has_t} torre." +
                "\n\nRecursos disponibles:\n"
                "\tMinerales: " + yellow("{mins:,}") +
                "\n\tDeuterio: " + yellow("{deut:,}"))
        s += temp.format(mins=self.planet.galaxia.minerales,
                         deut=self.planet.galaxia.deuterio,
                         solds=green(self.planet.soldados),
                         mags=green(self.planet.magos),
                         race=red(self.planet.raza.name),
                         has_c={1: green("Posee"),
                                0: red("No posee")}[self.planet.cuartel.built],
                         has_t={1: green("posee"),
                                0: red("no posee")}[self.planet.torre.built],)
        s += "\n" + cyan("-"*40) + "\n"
        return s

    @title.setter
    def title(self, value):
        self._title = value

    def _get_conquered_planet(self):
        planet = filter(lambda x: x.conquistado,
                        self.planet.galaxia.planets_list)
        try:
            planet = sample(list(planet), 1)[0]
        except ValueError:
            return None
        return planet

    def event_archmage_invasion(self):

        invaded_planet = self._get_conquered_planet()
        if not invaded_planet:
            return True
        
        input("ESTAS SIENDO INVADIDO POR EL ARCHIMAGO!!")
        infomenu = InfoMenu("Invasion del Archimago!!!")

        a = Archimago(self.planet.galaxia)
        b = Battle(self.planet.galaxia, a, invaded_planet)
        b.attacker.is_player = True
        b.defender.being_invaded = True
        for t in b.battle_turns():
            infomenu.content = t
            infomenu.run()

        b.update_defender(invaded_planet)

        return True

    def event_asteroid_hit(self):
        hit_planet = self._get_conquered_planet()
        if not hit_planet:
            return True

        input("HA CAIDO UN ASTEROIDE EN %s!!" % hit_planet.nombre.upper())

        damage = randrange(1500, 2500)

        for building in (hit_planet.cuartel, hit_planet.torre):
            building.vida -= damage

        hit_planet.soldados //= 2
        hit_planet.magos //= 2

    def run(self):
        # IMPLEMENT ARCHMAGE AND ASTEROID EVENTS
        if randrange(10) in range(2):
            if randrange(2):
                self.event_archmage_invasion()
            else:
                self.event_asteroid_hit()
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

    @property
    def _build_menu_info(self):
        has_c, has_t = self.planet.cuartel.built, self.planet.torre.built
        mins, deut = (self.planet.galaxia.minerales,
                      self.planet.galaxia.deuterio)
        options = ["Cuartel", "Torre"]
        functions = []
        labels = ["\t{}M, {}D".format(c.mins, c.deut)
                  for c in (COSTO_CUARTEL, COSTO_TORRE)]
        if has_c:
            labels[0] += red("\tConstruido")
            functions.append(self._already_purchased)
        elif mins < COSTO_CUARTEL.mins or deut < COSTO_CUARTEL.deut:
            labels[0] += red("\tInsuficientes Recursos")
            functions.append(self._insufficient)
        else:
            labels[0] += green("\tConstruir")
            functions.append(self._buy_cuartel)

        if has_t:
            labels[1] += red("\tConstruido")
            functions.append(self._already_purchased)
        elif mins < COSTO_TORRE.mins or deut < COSTO_TORRE.deut:
            labels[1] += red("\tInsuficientes Recursos")
            functions.append(self._insufficient)
        else:
            labels[1] += green("\tConstruir")
            functions.append(self._buy_torre)

        return options, functions, labels

    def build(self):
        menu = NumericalChoiceMenu()
        menu.title = self.title + cyan("Construyendo nuevos edificios")
        menu.items = self._build_menu_info  # Method returns the tuple

        stay = menu.run()
        if not stay:
            return True

        return self.build()

    def _already_purchased(self):
        menu = InfoMenu(title="Edificio ya está construido")
        return menu.run()

    def _buy_cuartel(self):
        if AreYouSureMenu(title="Comprando Cuartel").run():
            self.planet.cuartel.built = True
            self.planet.galaxia.minerales -= COSTO_CUARTEL.mins
            self.planet.galaxia.deuterio -= COSTO_CUARTEL.deut

        return True

    def _buy_torre(self):
        if AreYouSureMenu(title="Comprando Torre").run():
            self.planet.torre.built = True
            self.planet.galaxia.minerales -= COSTO_TORRE.mins
            self.planet.galaxia.deuterio -= COSTO_TORRE.deut

        return True

    def _insufficient(self):
        return InfoMenu(title="Insuficientes recursos").run()

    @property
    def purchasable_soldiers(self):
        """Returns the maximum amount of soldiers that can be
        purchased with the current resources, unless it exceeds
        the maximum number of soldiers by population
        """
        mins, deut = (self.planet.galaxia.minerales,
                      self.planet.galaxia.deuterio)

        max_soldados = self.planet.max_soldados - self.planet.soldados
        c_mins, c_deut = self.planet.raza.costo_soldado

        return min(min(mins//c_deut, deut//c_deut), max_soldados)

    @property
    def purchasable_wizards(self):
        """Returns the maximum amount of wizards that can be
        purchased with the current resources, unless it exceeds
        the maximum number of wizards by population
        """
        mins, deut = (self.planet.galaxia.minerales,
                      self.planet.galaxia.deuterio)

        max_magos = self.planet.max_magos - self.planet.magos
        c_mins, c_deut = self.planet.raza.costo_mago

        return min(min(mins//c_deut, deut//c_deut), max_magos)

    def create_units(self):
        p = self.planet

        if not p.cuartel:
            return InfoMenu("Necesitas un cuartel antes"
                            " de crear unidades").run()

        if p.raza.has_mago:
            menu = NumericalChoiceMenu()
            menu.title = "Elije la unidad a agregar"
            options = ["Soldados", "Magos"]
            menu.items = (options, [])
            unit = menu.run()
            if not unit:
                return True
        else:
            unit = "Soldados"

        unit_range = ((0, self.purchasable_soldiers) if unit == "Soldados"
                      else (0, self.purchasable_wizards))

        menu = NumericalInputMenu(unit_range)
        menu.title = "Elige el número de %s a comprar" % unit.lower()

        num = menu.run()
        if not num:
            return True

        if unit == "Soldados":
            p.soldados += num
            p.galaxia.minerales -= p.raza.costo_soldado.mins
            p.galaxia.deuterio -= p.raza.costo_soldado.deut
        else:
            p.magos += num
            p.galaxia.minerales -= p.raza.costo_mago.mins
            p.galaxia.deuterio -= p.raza.costo_mago.deut

        return True

    def get_resources(self):
        p = self.planet

        last_collect = p.ultima_recoleccion
        current_t = now().replace(microsecond=0)
        delta = current_t - last_collect

        deuterio = int(p.effective_tasa_deuterio * delta.seconds)
        minerales = int(p.effective_tasa_minerales * delta.seconds)

        menu = AreYouSureMenu()
        menu.title = cyan("Recolectando recursos")

        menu.content = green("{:,} segundos".format(delta.seconds))
        menu.content += (" han transcurrido desde la última recolleción."
                         "\nSi cosechas ahora, obtendrás:\n")
        menu.content += red("{:,} minerales".format(minerales)) + " y "
        menu.content += cyan("{:,} deuterio\n".format(deuterio))

        if menu.run():
            p.galaxia.minerales += minerales
            p.galaxia.deuterio += deuterio

            p.ultima_recoleccion = current_t

        return True

    def make_improvements(self):
        p = self.planet

        menu = NumericalChoiceMenu()
        menu.title = self.title + cyan("Comprando mejoras")

        options = ["Aumentar nivel de economía",
                   "Aumentar nivel de ataque"]

        labels = [green("(%i/3)" % p.nivel_economia) +
                  "\tCosto: 2000M, 4000D",
                  green("(%i/3)" % p.nivel_ataque) +
                  "\tCosto: 1000M, 2000D"]

        functions = [lambda: "ECON", lambda: "ATTK"]

        menu.items = (options, functions, labels)

        attr = menu.run()
        if not attr:
            return True

        elif attr == "ECON":
            if p.nivel_economia == 3:
                InfoMenu(title=self.title +
                         "Nivel de economía ya está maximizado").run()
            else:
                if p.galaxia.minerales < COSTO_MEJORA_ECONOMIA.mins or\
                   p.galaxia.deuterio < COSTO_MEJORA_ECONOMIA.deut:
                    InfoMenu(title=self.title + "Insuficientes recursos!").run()
                else:
                    p.nivel_economia += 1
                    p.galaxia.minerales -= COSTO_MEJORA_ECONOMIA.mins
                    p.galaxia.deuterio -= COSTO_MEJORA_ECONOMIA.deut
        elif attr == "ATTK":
            if p.nivel_ataque == 3:
                InfoMenu(title=self.title +
                         "Nivel de ataque ya está maximizado").run()
            else:
                if p.galaxia.minerales < COSTO_MEJORA_ATAQUE.mins or\
                   p.galaxia.deuterio < COSTO_MEJORA_ATAQUE.deut:
                    InfoMenu(title=self.title + "Insuficientes recursos!").run()
                else:
                    p.nivel_ataque += 1
                    p.galaxia.minerales -= COSTO_MEJORA_ATAQUE.mins
                    p.galaxia.deuterio -= COSTO_MEJORA_ATAQUE.deut

        return self.make_improvements()


class VisitUnconqueredPlanetMenu(VisitPlanetMenu):

    def __init__(self, planet):
        super().__init__(planet)

        self.title = "Visitando planeta no conquistado %s" % self.planet.nombre

        options = ["Comprar planeta",
                   "Invadir planeta"]

        functions = [self.purchase,
                     self.invade]

        self.items = (options, functions)

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

        return False

    def invade(self):

        menu = NumericalChoiceMenu()
        menu.title = "Elige un planeta para enviar su ejército"
        options = [p.nombre for p in self.planet.galaxia.planets_list
                   if p.conquistado]
        if len(options) == 0:
            InfoMenu("No hay planetas conquistados en esta galaxia"
                     " para enviar su ejercito!").run()
            return True
        functions = [lambda x=p: x for p in self.planet.galaxia.planets_list
                     if p.conquistado]
        labels = []
        temp = green("\tPoblación: {}/{}")
        for pf in functions:
            p = pf()
            labels.append(temp.format(p.soldados + p.magos, p.raza.max_pop))
        menu.items = (options, functions, labels)

        attacking_planet = menu.run()
        if not attacking_planet:
            return True

        menu = AreYouSureMenu(title="A punto de invadir planeta %s" %
                              self.planet.nombre)
        if not menu.run():
            return True

        infomenu = InfoMenu("Invasion!")

        b = Battle(self.planet.galaxia, attacking_planet, self.planet)
        b.attacker.is_player = True
        b.defender.being_invaded = True
        for t in b.battle_turns():
            infomenu.content = t
            infomenu.run()
        b.update_attacker(attacking_planet)
        b.update_defender(self.planet)

        return False


if __name__ == '__main__':
    import colorama;
    colorama.init()
    print(colorama.Style.BRIGHT)

    from universe import Universe
    m = MainMenu(Universe())
    m.run()
