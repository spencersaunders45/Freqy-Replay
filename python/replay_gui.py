import tkinter as tk
from tkinter import ttk
import os, sys

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, FILE_DIR)

from widgets.settings import Settings
from widgets.signals import Signals

class ReplayGUI:
    app = tk.Tk()

    def __init__(self):
        self.app.title("Freqy Replay")
        self.app.geometry("500x500")
        self.notebook = ttk.Notebook(self.app)
        self.__create_settings_frame()
        self.signals_tab = tk.Frame(self.notebook)
        self.notebook.add(self.signals_tab, text="Signals")
        # Adds the tabs to the gui
        self.notebook.pack(expand=1, fill='both')
        self.launch()
    
    
    def __configure_scroll_region(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def __configure_canvas_width(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def __create_settings_frame(self) -> None:
        """ Creates the settings frame with a scrollable frame """
        self.canvas = tk.Canvas(self.notebook)
        self.scrollbar: tk.Scrollbar = tk.Scrollbar(
            self.notebook,
            orient="vertical",
            command=self.canvas.yview
            )
        self.settings_tab = tk.Frame(self.canvas)
        self.settings = Settings(self.settings_tab)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack()
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.settings_tab, anchor="nw")
        self.settings_tab.bind("<Configure>", self.__configure_scroll_region)
        self.canvas.bind("<Configure>", self.__configure_canvas_width)
        self.notebook.add(self.canvas, text="Settings")

    def launch(self):
        self.app.mainloop()

if __name__ == '__main__':
    ReplayGUI()