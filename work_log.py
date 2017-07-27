from collections import OrderedDict
import datetime
import os

from peewee import *

db = SqliteDatabase('entries.db')


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

    def lookup_by_employee(self):
        """Find Entries by Employee Name"""
        self.clear_console()
        print(self.format_header('Lookup by Employee'))

        get_employee_names = Entry.select().distinct(Entry.employee_name).execute()
        employee_names = set()
        [employee_names.add(employee.employee_name.title()) for employee in get_employee_names]
        # allow the user to choose from a name
        [print(name) for name in employee_names]
        while True:
            chosen_name = input('Choose an employee: ').strip()
            if chosen_name == '':
                print('Please choose from the list of available names, or type "back" to return to lookup menu')
                continue
            # get the number of matches...
            name_matches = ConsoleUI.get_matches(chosen_name, employee_names)
            if len(name_matches) > 1:
                # clarify...
                while True:
                    print(self.clear_console())
                    print('Multiple matches:')
                    [print(name) for name in name_matches]
                    specific_name = input('Choose an exact name, or enter "all" to get all matches: ').lower().strip()
                    if specific_name == 'all':
                        # return all results
                        entries = Entry.select().order_by(Entry.created_timestamp.desc())
                        entries = entries.where(fn.Lower(Entry.employee_name).contains(chosen_name.lower()))
                        self.display_one_at_a_time(entries)
                        return True
                    elif specific_name.title() in name_matches:
                        # return the specific name results
                        entries = Entry.select().order_by(Entry.created_timestamp.desc())
                        entries = entries.where(fn.Lower(Entry.employee_name) == specific_name.lower())
                        self.display_one_at_a_time(entries)
                        return True
            elif len(name_matches) == 1:
                # run the query
                entries = Entry.select().order_by(Entry.created_timestamp.desc())
                entries = entries.where(fn.Lower(Entry.employee_name) == chosen_name.lower())
                self.display_one_at_a_time(entries)
                return True
            elif chosen_name == 'Back':
                break
            else:
                # no matches...
                print('Please choose from the list of available names, or type "back" to return to lookup menu')

    def lookup_entries_by_exact_date(self):
        """Display Entry Dates and allows the user to look up entries by exact date"""
        get_created_dates = Entry.select().distinct(Entry.created_timestamp).execute()
        created_dates = set()
        [created_dates.add(entry.created_timestamp.strftime('%m-%d-%Y')) for entry in get_created_dates]
        created_dates = list(created_dates)
        created_dates.sort()

        self.clear_console()
        print(self.format_header('Lookup by Exact Date'))
        [print(date) for date in created_dates]
        while True:
            chosen_date = input('Enter a date to see entries from (MM-DD-YYYY): ')
            try:
                chosen_date = datetime.datetime.strptime(chosen_date, '%m-%d-%Y')
            except ValueError:
                print('Please enter a date in the valid format')
            else:
                if chosen_date.strftime('%m-%d-%Y') not in created_dates:
                    print('hey-o! there are no entries with that date. Try another...')
                else:
                    break
        entries = Entry.select().order_by(Entry.created_timestamp.desc())
        entries = entries.where(Entry.created_timestamp.between(
            chosen_date,
            chosen_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        ))
        self.display_one_at_a_time(entries)

    def lookup_entries_by_date_range(self):
        """Find Entries by Date Range"""
        self.clear_console()
        print(self.format_header('Lookup by Date Range'))
        print('Search for entries from...')
        from_date = ConsoleUI.get_a_date('enter From Date')
        self.clear_console()
        print(self.format_header('Lookup by Date Range'))
        print('Search for entries from {} to...'.format(from_date.strftime('%m-%d-%Y')))
        # get the end date
        while True:
            to_date = ConsoleUI.get_a_date('enter To date')
            if to_date.strftime('%m-%d-%Y') < from_date.strftime('%m-%d-%Y'):
                print('Please enter a date AFTER the From Date')
            else:
                break
        entries = Entry.select().order_by(Entry.created_timestamp.desc())
        entries = entries.where(Entry.created_timestamp.between(
            from_date,
            to_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)
        ))
        self.display_one_at_a_time(entries)

    def lookup_entries(self):
        """Lookup Previous Entries"""
        lookup_menu_choice = None
        while lookup_menu_choice != 'B':
            self.clear_console()
            print(self.format_header('Lookup Entries'))
            print('[N] Lookup by Employee Name\n'
                  '[D] Lookup by Created Date\n'
                  '[T] Lookup by Time Spent\n'
                  '[S] Lookup by Search Term\n'
                  '[B] Back to Main Menu')

            lookup_menu_choice = input('> ').upper().strip()
            if lookup_menu_choice == 'N':
                self.lookup_by_employee()
            elif lookup_menu_choice == 'D':
                date_search_choice = ''
                while date_search_choice != 'B':
                    self.clear_console()
                    print(self.format_header('Lookup by Date'))
                    print('[E] Search for exact date\n'
                          '[R] Search by date range\n'
                          '[B] Back to Lookup Menu')
                    date_search_choice = input('> ').upper().strip()
                    if date_search_choice == 'E':
                        self.lookup_entries_by_exact_date()
                        break
                    elif date_search_choice == 'R':
                        self.lookup_entries_by_date_range()
                        break
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

    @staticmethod
    def get_matches(string, some_iterable):
        """Finds the number of matches for a string inside some iterable"""
        matches = []
        for item in some_iterable:
            if string.lower() in item.lower():
                matches.append(item)
        return matches

if __name__ == "__main__":
    initialize()
    console = ConsoleUI()
    console.run_console_ui()
