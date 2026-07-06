import sys
from PySide6.QtWidgets import QApplication
from app import FinanceManager
from views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Inicializa o motor lógico de dados
    manager = FinanceManager()
    
    # Inicializa a interface injetando o manager nela
    window = MainWindow(manager)
    window.show()
    
    sys.exit(app.exec())