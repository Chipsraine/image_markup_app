import sys
from PyQt5 import QtWidgets
from example_app import ExampleApp

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = ExampleApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
