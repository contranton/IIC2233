from gui.Gui import MyWindow
from PyQt5 import QtWidgets
import sys

from library import get_function_from_name
from exceptions import BadQuery, MovieError, WrongInput


class T03Window(MyWindow):
    def __init__(self):
        super().__init__()

    def run_query(self, *args):
        return map(lambda arg: self.run_query(arg)
                   if isinstance(arg, list) else
                   get_function_from_name(arg[0])(args[1:]),
                   args)

    def process_query(self, queries):
        # Agrega en pantalla la solucion.
        functions = [q[0] for q in queries]
        results = map(lambda q: list(self.run_query(*q)),
                      queries)

        try:
            results = list(results)
        except (BadQuery, MovieError, WrongInput) as exc:
            results = ["Error: ", str(exc)]

        text = "Probando funcion\n"
        text += "\n".join(functions)
        text += "\n\nResultados:\n"
        text += "\n".join([str(i) for i in results])
        self.add_answer(text)

    def save_file(self, queries):
        # Crea un archivo con la solucion.
        print(queries)

if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(value)
        print(traceback)


    sys.__excepthook__ = hook

    app = QtWidgets.QApplication(sys.argv)
    window = T03Window()
    sys.exit(app.exec_())
