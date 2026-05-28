import sys
import os

# Añadimos el directorio raíz al path para que Python resuelva correctamente imports 
# locales como 'from views...' o 'from controllers...'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    """
    Punto de entrada de la aplicación.
    Inicializa el loop de PyQt y levanta la Ventana Principal.
    """
    app = QApplication(sys.argv)
    
    # Instanciamos y mostramos la GUI
    window = MainWindow()
    window.show()
    
    # Ejecutamos el bucle de eventos
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
