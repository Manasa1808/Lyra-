import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import LyraUI

def main():
    app = QApplication(sys.argv)
    # Optional: use a stylesheet for a modern look
    try:
        with open("ui/styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass

    window = LyraUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()