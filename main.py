# main.py
import tkinter as tk
from view.login_screen import LoginScreen

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()
