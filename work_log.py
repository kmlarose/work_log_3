from collections import OrderedDict
import datetime
import os

from peewee import *

db = SqliteDatabase('work_log.db')


class Entry(Model):
    """Database model for Work Log Entries"""
    employee_name = TextField()
    task_name = TextField()
    task_time = IntegerField()
    task_notes = TextField()
    created_timestamp = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db

    def __str__(self):
        """Presents the Entry in a readable str format"""
        return ('Task: {}'.format(self.task_name)+'\n'
                'Created: {}'.format(self.created_timestamp.strftime('%B %d, %Y'))+'\n'
                'Employee: {}'.format(self.employee_name)+'\n'
                'Minutes Spent: {}'.format(self.task_time)+'\n'
                'Notes: {}'.format(self.task_notes))


def initialize():
    """Create the database and the table if they don't exist"""
    db.connect()
    db.create_tables([Entry], safe=True)


class ConsoleUI:
    """Object for interacting with a user via the console"""
    main_menu = OrderedDict([
        ('[A]', 'Add New Entry'),
        ('[L]', 'Lookup Previous Entries'),
        ('[Q]', 'Quit Work Log')
    ])

    def add_new_entry(self):
        """Add New Entry"""
        self.clear_console()
        print(self.format_header('Add New Entry'))

        employee_name = self.get_required_string("Employee's Name")
        task_name = self.get_required_string("Task Name")
        task_time = self.get_positive_int("Task Time (minutes)")
        task_notes = input("Notes (optional): ")

        if input('Save entry? [Y/n] ').lower() != 'n':
            Entry.create(employee_name=employee_name, task_name=task_name, task_time=task_time, task_notes=task_notes)

    def lookup_entries(self):
        """Lookup Previous Entries"""
        return Entry.select().order_by(Entry.created_timestamp.desc())

        # if there are no results, return some kind of message
        # if there is no search query, then just get 'em all? i guess
        # if there is a search query, then get the filtered query


        #############################################################################

    #######################################################################################

    def display_main_menu(self):
        """Prints the Main Menu to Console"""
        [print(key, value) for key, value in self.main_menu.items()]

    def run_console_ui(self):
        """Runs the console user interface"""
        main_menu_choice = None
        while main_menu_choice != 'Q':
            self.clear_console()
            self.display_main_menu()
            main_menu_choice = input('> ').upper().strip()
            if main_menu_choice == 'A':
                self.add_new_entry()
            if main_menu_choice == 'L':
                entries = self.lookup_entries()
                [print(entry) for entry in entries]

    @staticmethod
    def get_required_string(required_string_label):
        """Gets a required string from the user"""
        while True:
            required_string = input('{}: '.format(required_string_label)).strip()
            if required_string == '':
                print('{} is required...'.format(required_string_label))
            else:
                return required_string

    @staticmethod
    def get_positive_int(positive_int_label):
        """Gets a positive integer from the user"""
        while True:
            positive_int = input('{}: '.format(positive_int_label)).strip()
            try:  # make sure the user input is an int
                positive_int = int(positive_int)
            except ValueError:
                print('Please enter an integer...')
            else:
                if positive_int <= 0:  # make sure the user input is positive
                    print('Please enter a positive integer...')
                else:
                    return positive_int

    @staticmethod
    def clear_console():
        """Clear the Console Screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def format_header(screen_title):
        """Formats the Console Screen Header"""
        leftover_space = 24 - len(screen_title)
        margin = ' ' * int(leftover_space / 2)
        return margin + screen_title + '\n' + ('=' * 24)


if __name__ == "__main__":
    initialize()
    console = ConsoleUI()
    console.run_console_ui()
