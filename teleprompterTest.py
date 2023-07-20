from Teleprompter import Teleprompter
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)

teleprompter = Teleprompter()

sys.exit(app.exec())
