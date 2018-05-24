from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication, QLineEdit, QPushButton, QLabel
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 300)
        # Main layout
        vert_layout = QVBoxLayout()

        # Sub layouts
        self.grid_layout = QGridLayout()
        posiciones = [(i, j) for i in range(3) for j in range(3)]
        self.postits = []
        for pos in posiciones:
            p = PostIt(pos, self)
            self.postits.append(p)

        for p in self.postits:
            self.grid_layout.addWidget(p, *p.posicion)
            
        hor_layout = QHBoxLayout()

        self.btn_send = QPushButton('Send', self)
        self.texto_entrada = QLineEdit('', self)
        self.btn_send.clicked.connect(self.nuevo_postit)
        hor_layout.addWidget(self.texto_entrada)
        hor_layout.addWidget(self.btn_send)


        # Assign sublayouts
        vert_layout.addLayout(self.grid_layout)
        vert_layout.addLayout(hor_layout)

        self.setLayout(vert_layout)

        self.indice_postit = 0
        print("SHOWING")
        self.show()

    def nuevo_postit(self):
        postit = next((p for p in self.postits if p.texto == ""))
        if not postit:
            return
        
        texto = self.texto_entrada.text()
        texto_otros = [postit.texto for postit in self.postits]

        if revisar_nota(texto, texto_otros) and self.indice_postit <= 8:
            print("Here")
            postit.crear_nuevo(texto)
            self.show()
            self.indice_postit += 1

    def delete_postit(self):
        pass


class PostIt(QWidget):
    def __init__(self, posicion, parent):
        super().__init__()

        self.texto = ""
        self.posicion = posicion
        self.setFixedSize(300, 100)
        self.parent = parent

        self.btn = QPushButton('Borrar', self)
        self.btn.clicked.connect(self.borrar)
        self.label = QLabel(self.texto, self)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        self.setLayout(layout)

        retain = self.sizePolicy()
        retain.setRetainSizeWhenHidden(True)
        self.setSizePolicy(retain)
        
        self.hide()

    def __repr__(self):
        return self.texto

    def crear_nuevo(self, string):
        self.texto = string
        self.label.setText(self.texto)
        self.show()

    def borrar(self):
        print("Borrando")
        self.texto = ""
        self.label.setText("")
        self.hide()


#True si cumple los requisitos, False caso contrario
def revisar_nota(nota, notas_actuales):
    if nota == '':
        return False
    if len(nota) > 140:
        return False
    if nota.count('\n') > 3:
        return False
    for n in notas_actuales:
        if nota == n:
            return False
    return True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())
