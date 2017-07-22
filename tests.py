from collections import OrderedDict
from test.support import captured_stdin
from test.support import captured_stdout
import datetime
import unittest
from unittest import mock

from work_log import ConsoleUI
from work_log import Entry


class TestConsoleUI(unittest.TestCase):
    """Run Tests on the Console User Interface"""
    def test_main_menu(self):
        """Test the ConsoleUI object main_menu is valid"""
        test_console = ConsoleUI()
        self.assertEqual(test_console.main_menu, OrderedDict([('[A]', 'Add New Entry'),
                                                         ('[L]', 'Lookup Previous Entries'),
                                                         ('[Q]', 'Quit Work Log')]))

    def test_display_main_menu(self):
        """Test the display_main_menu() method has the right output"""
        with captured_stdout() as stdout:
            test_console = ConsoleUI()
            test_console.display_main_menu()
        self.assertIn(('[A] Add New Entry\n'
                       '[L] Lookup Previous Entries\n'
                       '[Q] Quit Work Log\n'), stdout.getvalue())

    def test_run_edit_menu(self):
        """Test the edit menu has the right output"""
        with captured_stdin() as stdin, captured_stdout() as stdout:
            console = ConsoleUI()
            stdin.write('b')
            stdin.seek(0)
            console.run_edit_menu(Entry.get())
            self.assertIn(('[D] Edit Created Date\n'
                           '[T] Edit Task Name\n'
                           '[M] Edit Minutes Spent\n'
                           '[N] Edit Notes\n'
                           '[B] Back to Main Menu\n'), stdout.getvalue())

    @unittest.mock.patch('work_log.os')
    def test_clear_screen(self, mock_os):
        """Test the clear console method"""
        ConsoleUI.clear_console()
        mock_os.system.assert_called()

    def test_format_header(self):
        """Test the format_header() method"""
        self.assertEqual(ConsoleUI.format_header('testing123'), ('       testing123\n'
                                                                 '========================'))

    def test_get_positive_int_regular(self):
        """Test the get_positive_int() method with a valid input"""
        with captured_stdin() as stdin:
            stdin.write('5\n')
            stdin.seek(0)
            self.assertEqual(ConsoleUI.get_positive_int('test'), 5)

    @unittest.expectedFailure
    def test_get_positive_int_with_string(self):
        """The get_positive_int() method should be able to handle ValueError"""
        with self.assertRaises(ValueError):
            with captured_stdin() as stdin:
                stdin.write('five\n')
                stdin.seek(0)
                ConsoleUI.get_positive_int('test')

    def test_get_positive_int_with_negative(self):
        """The get_positive_int() method should be able to handle a negative number"""
        with self.assertRaises(EOFError):
            with captured_stdin() as stdin, captured_stdout() as stdout:
                stdin.write('-5\n')
                stdin.seek(0)
                ConsoleUI.get_positive_int('test')

    def test_get_required_string(self):
        """Should get a string from the user"""
        with captured_stdin() as stdin:
            stdin.write('testing123\n')
            stdin.seek(0)
            self.assertEqual(ConsoleUI.get_required_string('BLAH'), 'testing123')

    def test_get_required_string_with_empty_input(self):
        """Should ask again if given an empty string - test should throw EOFError"""
        with self.assertRaises(EOFError):
            with captured_stdin() as stdin:
                stdin.write('\n')
                stdin.seek(0)
                self.assertEqual(ConsoleUI.get_required_string('BLAH'), '')

    @unittest.expectedFailure
    def test_quit_main_menu(self):
        """Test quitting the main menu"""
        with self.assertRaises(EOFError):
            with captured_stdin() as stdin:
                stdin.write('q')
                stdin.seek(0)
                test_console = ConsoleUI()
                test_console.run_console_ui()

    @unittest.expectedFailure
    def test_display_one_at_a_time(self):
        """Make sure the user input 'b' will break out of the Lookup Menu"""
        test_console = ConsoleUI()
        with captured_stdin() as stdin:
            stdin.write('b')
            stdin.seek(0)
            with self.assertRaises(EOFError):
                test_console.display_one_at_a_time(Entry.select())

    def test_display_entries_with_no_results(self):
        """Make sure the program doesn't break if there's no lookup results"""
        test_console = ConsoleUI()
        with captured_stdin() as stdin, captured_stdout() as stdout:
            stdin.write('test')
            stdin.seek(0)
            test_console.display_one_at_a_time(Entry.select().where(Entry.created_timestamp == datetime.datetime.now()))
            self.assertIn('Sorry, no entries found', stdout.getvalue())

    def test_add_entry(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y']):
            self.assertTrue(test_console.add_new_entry())
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'n']):
            self.assertFalse(test_console.add_new_entry())

    def test_edit_entry_date(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['d', '01-01-1980', 'y']):
            entry = Entry.select().where(Entry.task_name == 'Test Task')[0]
            test_console.run_edit_menu(entry)
            self.assertEqual(entry.created_timestamp, datetime.datetime.strptime('01-01-1980', '%m-%d-%Y'))
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(entry))

    def test_edit_entry_name(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['t', 'did it work?', 'y']):
            entry = Entry.select().where(Entry.task_name == 'Test Task')[0]
            test_console.run_edit_menu(entry)
            self.assertEqual(entry.task_name, 'did it work?')
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(entry))

    def test_edit_entry_minutes(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['m', '888', 'y']):
            entry = Entry.select().where(Entry.task_name == 'Test Task')[0]
            test_console.run_edit_menu(entry)
            self.assertEqual(entry.task_time, 888)
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(entry))

    def test_edit_entry_notes(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['n', 'keep it real', 'y']):
            entry = Entry.select().where(Entry.task_name == 'Test Task')[0]
            test_console.run_edit_menu(entry)
            self.assertEqual(entry.task_notes, 'keep it real')
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(entry))

    def test_delete_entry(self):
        test_console = ConsoleUI()
        entry = Entry.select().where(Entry.task_name == 'Test Task')[0]
        with unittest.mock.patch('builtins.input', return_value='n'):
            self.assertFalse(test_console.delete_entry(entry))
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(entry))

    def test_lookup_by_time(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['unittest', 'Test Time Lookup',
                                                                '777888', 'this should get deleted...', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['t', '777888', 'b', 'b']), captured_stdout() as stdout:
            test_console.lookup_entries()
            self.assertIn('Test Time Lookup', stdout.getvalue())
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(Entry.select().where(Entry.task_name == 'Test Time Lookup')[0]))

    def test_lookup_by_search(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['unittest', 'Test Search Lookup',
                                                                '999', 'this should get deleted...', 'y']):
            test_console.add_new_entry()
        with unittest.mock.patch('builtins.input', side_effect=['s', 'search lookup', 'b', 'b']), captured_stdout() as stdout:
            test_console.lookup_entries()
            self.assertIn('Test Search Lookup', stdout.getvalue())
        with unittest.mock.patch('builtins.input', return_value='y'):
            self.assertTrue(test_console.delete_entry(Entry.select().where(Entry.task_name == 'Test Search Lookup')[0]))



class TestEntryClass(unittest.TestCase):
    """Run Tests on the Database Model Object"""
    def test_entry_string(self):
        """Test the Entry is represented as a string in the correct format"""
        entry = Entry.get()
        self.assertEqual(str(entry), ('Task: {}'.format(entry.task_name)+'\n'
                                      'Created: {}'.format(entry.created_timestamp.strftime('%B %d, %Y'))+'\n'
                                      'Employee: {}'.format(entry.employee_name)+'\n'
                                      'Minutes Spent: {}'.format(entry.task_time)+'\n'
                                      'Notes: {}'.format(entry.task_notes)))

if __name__ == '__main__':
    unittest.main()