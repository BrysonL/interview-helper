import PySimpleGUI as sg
import tkinter as tk
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import sys

def create_window_with_text(text):
    app = QApplication(sys.argv)
    window = QWidget()

    layout = QVBoxLayout()
    label = QLabel(text)
    layout.addWidget(label)
    window.setLayout(layout)

    window.show()
    sys.exit(app.exec())

def teleprompter(text, font_size=24, transparency=0.8):
    root = tk.Tk()
    root.attributes("-alpha", transparency)
    root.attributes("-topmost", True)
    root.configure(bg="systemTransparent")
    root.overrideredirect(1)

    def on_click(event):
        root.destroy()

    label = tk.Label(root, text=text, font=("Helvetica", font_size), bg="systemTransparent", fg="white")
    label.pack(padx=10, pady=10)
    label.bind("<Button-1>", on_click)

    root.update_idletasks()
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x = (root.winfo_screenwidth() - width) // 2
    y = (root.winfo_screenheight() - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")

    root.mainloop()

def teleprompter_sg(text, font_size=24, transparency=1):
    sg.theme("SystemDefaultForReal")
    sg.set_options(font=("Helvetica", font_size))

    layout = [
        [sg.Text(text, background_color=None, text_color="white")]
    ]

    window = sg.Window("Teleprompter", layout, no_titlebar=True, alpha_channel=transparency, grab_anywhere=True)

    while True:
        event, _ = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break

    window.close()

def create_window_with_text_tk(text):
    root = tk.Tk()
    label = tk.Label(root, text=text)
    label.pack()
    root.mainloop()

if __name__ == "__main__":
    text = "Sample text"
    create_window_with_text(text)

