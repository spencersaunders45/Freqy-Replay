import tkinter as tk
from tkinter import ttk
import os, sys
from tomlkit.toml_file import TOMLFile
from tomlkit.toml_document import TOMLDocument
from tomlkit.items import Integer, String, Float, Array, Table

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f'{FILE_DIR}/../'
sys.path.insert(0, PYTHON_DIR)

TOML_FILE = f'{PYTHON_DIR}/config.toml'

from helper_functions.toml_writer import TomlWriter

class Settings:
    config: TOMLDocument = TOMLFile(TOML_FILE).read()
    config_writer = TomlWriter()
    get_keys = lambda x, y: list(y.keys())

    def __init__(self, master: tk.Frame) -> None:
        self.master: tk.Frame = master
        self.tables: list = self.get_keys(self.config)
        self.__populate_toml_data()
    
    def __update_key_value(self, event, table: str, key: str, value: tk.Entry, value_type) -> None:
        """Updates the key value pair in the toml file.
        
        Arguments:
            table (str): The name of the table where the key value pair is
            located.
            
            key (str): The name of the key to be updated.
            
            value (Any): The new value to replace the old one.
        """
        if value_type == String:
            value = value.get()
        elif value_type == Float:
            value = float(value.get())
        elif value_type == Integer:
            value = int(value.get())
        elif value_type == Table:
            value = dict(value.get())
        elif value_type == Array:
            value = list(value.get())
        self.config_writer.update(table, key, value)

    def __populate_toml_data(self):
        """ Adds all the widgets to the frame with toml data """
        for table in self.tables:
            table_label: tk.Label = tk.Label(self.master, text=table)
            table_label.pack()
            table_data: TOMLDocument = self.config.get(table)
            for key in table_data:
                # Create key labels
                key_label: tk.Label = tk.Label(self.master, text=key)
                key_label.pack()
                # Create value entries
                value_entry: tk.Entry = tk.Entry(self.master)
                value_entry.insert(0, table_data[key])
                value_entry.pack()
                value_type = type(table_data[key])
                value_entry.bind(
                    '<Return>',
                    lambda event,
                    p1=table,
                    p2=key,
                    p3=value_entry,
                    p4=value_type: self.__update_key_value(event, p1, p2, p3, p4)
                    )