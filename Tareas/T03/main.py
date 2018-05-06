from gui.Gui import MyWindow
from PyQt5 import QtWidgets
import sys

from library import run_query
from exceptions import BadQuery, MovieError, WrongInput


class T03Window(MyWindow):
    def __init__(self):
        # TODO; preprocess
        super().__init__()

    def process_query(self, queries):
        # Agrega en pantalla la solucion.
        results = map(lambda q: (q[0], list(run_query(q))),
                      queries)
        try:
            results = list(results)
        except (BadQuery, MovieError, WrongInput) as exc:
            results = ["Error: ", repr(exc)]

        hdr = "-"*10 + "CONSULTA %i" + "-"*10 + "\n"
        text = [hdr % (i+1) + str(res) + "\n" for i, res in enumerate(results)]
        text = "\n".join(text)
        self.add_answer(text)
        return text

    def save_file(self, queries):
        # Crea un archivo con la solucion.
        print(queries)
        results = self.process_query(queries)

        with open("results.txt", 'w') as f:
            f.write(results)

if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(value)
        print(traceback)


    sys.__excepthook__ = hook

    app = QtWidgets.QApplication(sys.argv)
    window = T03Window()
    sys.exit(app.exec_())
