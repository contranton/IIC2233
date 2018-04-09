from menus import MainMenu
from universe import Universe
import colorama

if __name__ == '__main__':
    import traceback
    colorama.init()
    print(colorama.Style.BRIGHT)

    try:
        MainMenu(Universe()).run()
    except:
        traceback.print_exc()
        input("Ayudante, te he fallado :cc")
