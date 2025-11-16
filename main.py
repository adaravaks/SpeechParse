import tkinter as tk
from gui import SpeechParser


if __name__ == '__main__':
    root = tk.Tk()
    app = SpeechParser(root)
    root.mainloop()
