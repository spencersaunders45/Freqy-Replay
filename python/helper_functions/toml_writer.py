import os, sys

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
PYTHON_DIR = f'{FILE_DIR}/../'
sys.path.insert(0, PYTHON_DIR)
TOML_FILE = f'{PYTHON_DIR}/config.toml'

class TomlWriter:
    def __init__(self) -> None:
        pass
    
    def __insert_new_value(self, split_line: list, value) -> None:
        """Casts the value into a string before writing it to the file.
        
        Arguments:
            split_line (list): A list of words from a file line.
            
            value (Any): The value to be written to the toml file.
        """
        value_type = type(value)
        accepted_types = [str, float, dict, list, int]
        if not value_type in accepted_types:
            print(f"type: {value_type} is not an acceptable type")
            print(f"Acceptable types are {accepted_types}")
            exit(0)
        if value_type == str:
            split_line[1] = f'"{value}"'
        else:
            split_line[1] = str(value)
    
    def __is_table(self, current_table: str, table_search_name: str) -> bool:
        """Checks if the current table is the table where the updated value
        is located.
        
        Arguments:
            current_table (str): The table found while reading the toml file.
            
            table_search_name (str): The name of table we are looking for.
            
        Returns:
            bool: Indicates if the current table is the table where the
            target key is located.
        """
        if table_search_name in current_table:
            return True
        else:
            return False
    
    def __join_line(self, line_list: list) -> str:
        """Joins the split list into a single string.
        
        Arguments:
            line_list (list): A list of words from a file line.
            
        Returns:
            str: A string containing the updated key value pair.
        """
        new_line: str = ''
        line_list.insert(1, '= ')
        for word in line_list:
            new_line += str(word)
        new_line += '\n'
        return new_line
    
    def __get_comment(self, line: str) -> str:
        """Finds if there is comment in a line and returns the str value if
        there is.
        
        Arguments:
            line (str): A line from the toml file being read.
            
        Returns:
            str: A str of the found comment
        """
        comment: str = ''
        split_line: list = line.split('#')
        if len(split_line) > 1:
            comment += '\t\t\t#'
            for index in range(1, len(split_line)):
                comment += split_line[index].strip('\n')
        return comment
    
    def update(self, table: str, key: str, value) -> bool:
        """Updates a key value pair in a toml file.
        
        Arguments:
            table (str): The name of the table where the key value pair is
            located.
            
            key (str): The name of the key to be updated.
            
            value (Any): The new value for the key.
            
        Returns:
            bool: Indicates if the toml file was updated.
        """
        update_completed: bool = False
        found_section: bool = False
        updated_file: str = ''
        
        f = open(TOML_FILE, 'r')
        for line in f:
            # Check if the searched table has ended
            if '[' in line and ']' in line and found_section:
                f.close()
                return False
            # Find where the table begins
            if self.__is_table(line.strip(), table):
                found_section: bool = True
            split_line: list = line.split('=')
            # Update the key value pair in the toml file
            if split_line[0].strip() == key:
                comment = self.__get_comment(line)
                split_line.append(comment)
                self.__insert_new_value(split_line, value)
                updated_line = self.__join_line(split_line)
                line = updated_line
                update_completed = True
                found_section = False
            updated_file += line
        f.close()
        
        # Write the updated toml file
        f = open(TOML_FILE, 'w')
        f.write(updated_file)
        f.close()
        
        return update_completed
