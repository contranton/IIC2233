from gui.Gui import MyWindow
from PyQt5 import QtWidgets
import sys

from library.process import process_queries
from library.preproc import preprocess_comments
from library.exceptions import BadQuery, MovieError, WrongInput


class T03Window(MyWindow):
    def __init__(self):
        # TODO; preprocess
        super().__init__()
        preprocess_comments()

    def process_query(self, queries):
        # Agrega en pantalla la solucion.
        list(map(self.add_answer, process_queries(queries)))

    def save_file(self, queries):
        # Crea un archivo con la solucion.
        results = list(process_queries(queries))

        with open("results.txt", 'w') as f:
            f.write("".join(results))

if __name__ == '__main__':
    def hook(type, value, traceback):
        print(type)
        print(value)
        print(traceback)


    sys.__excepthook__ = hook

    app = QtWidgets.QApplication(sys.argv)
    window = T03Window()
    sys.exit(app.exec_())
