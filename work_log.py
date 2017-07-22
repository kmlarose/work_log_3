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

    def run_edit_menu(self, entry):
        """Display the Edit an Entry Menu"""
        edit_menu_choice = None
        while edit_menu_choice != 'B':
            self.clear_console()
            print(self.format_header('Edit Entry'))
            print(entry)
            print('='*24)
            print('[D] Edit Created Date\n'
                  '[T] Edit Task Name\n'
                  '[M] Edit Minutes Spent\n'
                  '[N] Edit Notes\n'
                  '[B] Back to Main Menu')

            # handle user input
            edit_menu_choice = input('> ').upper().strip()
            if edit_menu_choice == 'D':
                new_task_date = self.get_a_date('New Created Date')
                if input('Are you sure? [y/N]: ').lower().strip() == 'y':
                    entry.created_timestamp = new_task_date
                    entry.save()
                    break
            elif edit_menu_choice == 'T':
                new_task_name = self.get_required_string('New Task Name')
                if input('Are you sure? [y/N]: ').lower().strip() == 'y':
                    entry.task_name = new_task_name
                    entry.save()
                    break
            elif edit_menu_choice == 'M':
                new_task_minutes = self.get_positive_int('New Task Time (minutes)')
                if input('Are you sure? [y/N]: ').lower().strip() == 'y':
                    entry.task_time = new_task_minutes
                    entry.save()
                    break
            elif edit_menu_choice == 'N':
                new_task_notes = self.get_required_string('New Task Notes')
                if input('Are you sure? [y/N]: ').lower().strip() == 'y':
                    entry.task_notes = new_task_notes
                    entry.save()
                    break

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
            return True
        return False

    def display_one_at_a_time(self, entries):
        """Display the Entries One At A Time"""
        if not entries:
            self.clear_console()
            print('Sorry, no entries found')
            input('Please press enter to return to Main Menu...')
        else:
            idx = 0
            lookup_menu_choice = None
            while lookup_menu_choice != 'B':
                # set up variables
                entry = entries[idx]
                is_first_entry = idx == 0
                is_last_entry = idx == len(entries) - 1

                # display the header, entry, and menu
                self.clear_console()
                print(ConsoleUI.format_header('Entry {} of {}'.format(idx+1, len(entries))))
                print(entry)
                print('='*24)
                print('[E] Edit Entry')
                print('[D] Delete Entry')
                if not is_first_entry:
                    print('[P] Previous Entry')
                if not is_last_entry:
                    print('[N] Next Entry')
                print('[B] Back to Main Menu')

                # handle user input
                lookup_menu_choice = input('> ').upper().strip()
                if lookup_menu_choice == 'E':
                    self.run_edit_menu(entry)
                elif lookup_menu_choice == 'D':
                    if ConsoleUI.delete_entry(entry):
                        break
                elif lookup_menu_choice == 'P' and not is_first_entry:
                    idx -= 1
                elif lookup_menu_choice == 'N' and not is_last_entry:
                    idx += 1

    def lookup_entries(self):
        """Lookup Previous Entries"""
        lookup_menu_choice = None
        while lookup_menu_choice != 'B':
            self.clear_console()
            print('[N] Lookup by Employee Name\n'
                  '[D] Lookup by Created Date\n'
                  '[T] Lookup by Time Spent\n'
                  '[S] Lookup by Search Term\n'
                  '[B] Back to Main Menu')

            lookup_menu_choice = input('> ').upper().strip()
            if lookup_menu_choice == 'N':
                pass
            elif lookup_menu_choice == 'D':
                pass
            elif lookup_menu_choice == 'T':
                search_time = self.get_positive_int('Enter a Task Time to search for (minutes)')
                entries = Entry.select().order_by(Entry.created_timestamp).where(Entry.task_time == search_time)
                self.display_one_at_a_time(entries)
            elif lookup_menu_choice == 'S':
                search_term = self.get_required_string('Search Entries for')
                entries = Entry.select().order_by(Entry.created_timestamp).where(Entry.task_name.contains(search_term) |
                                                                                 Entry.task_notes.contains(search_term))
                self.display_one_at_a_time(entries)

    def display_main_menu(self):
        """Prints the Main Menu to Console"""
        self.clear_console()
        print(self.format_header('Work Log'))
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
                self.lookup_entries()

    @staticmethod
    def get_a_date(date_label):
        """Gets a date from the user"""
        while True:
            date = input('{} (MM-DD-YYYY): '.format(date_label))
            try:
                date = datetime.datetime.strptime(date, '%m-%d-%Y')
            except ValueError:
                print('Please enter a date in the valid format, (MM-DD-YYYY): ')
            else:
                return date

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

    @staticmethod
    def delete_entry(entry):
        """Delete Entry"""
        if input('Are you sure? [y/N]').lower().strip() == 'y':
            entry.delete_instance()
            return True
        return False

if __name__ == "__main__":
    initialize()
    console = ConsoleUI()
    console.run_console_ui()
