from Teleprompter import Teleprompter
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import sys

def main():
    app = QApplication(sys.argv)

    teleprompter = Teleprompter()
    print("Teleprompter created")

    # QTimer.singleShot will call the function after a delay (in milliseconds)
    QTimer.singleShot(3000, teleprompter.play)
    print("Teleprompter playing")

    QTimer.singleShot(6000, teleprompter.stop)
    print("Teleprompter stopped")

    QTimer.singleShot(9000, teleprompter.reverse)
    print("Teleprompter reversing")

    QTimer.singleShot(12000, teleprompter.stop)
    print("Teleprompter stopped")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
