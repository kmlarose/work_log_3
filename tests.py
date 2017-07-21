from collections import OrderedDict
from test.support import captured_stdin
from test.support import captured_stdout
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

from work_log import ConsoleUI
from work_log import Entry
from work_log import initialize


# create a menu that allows you to add entries, lookup entries, or quit
class TestConsoleUI(unittest.TestCase):
    """Run Tests on the Console User Interface"""
    def test_main_menu(self):
        """Test the ConsoleUI object main_menu is valid"""
        console = ConsoleUI()
        self.assertEqual(console.main_menu, OrderedDict([('[A]', 'Add New Entry'),
                                                         ('[L]', 'Lookup Previous Entries'),
                                                         ('[Q]', 'Quit Work Log')]))

    def test_display_main_menu(self):
        """Test the display_main_menu() method has the right output"""
        with captured_stdout() as stdout:
            console = ConsoleUI()
            console.display_main_menu()
        self.assertEqual(stdout.getvalue(), ('[A] Add New Entry\n'
                                             '[L] Lookup Previous Entries\n'
                                             '[Q] Quit Work Log\n'))

    @unittest.mock.patch('work_log.os')  # assign a mock OS to work_log.py
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

    # @patch('builtins.input', lambda: '123')
    def test_add_entry(self):
        test_console = ConsoleUI()
        with unittest.mock.patch('builtins.input', side_effect=['Test Name', 'Test Task', '999', 'Test Notes', 'y)']):
            test_console.add_new_entry()


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

    # def test_db_initialize(self):
    #     initialize()



    # def test_mock_db_add(self):
    #     """Test adding to the database with a MagicMock object"""
    #     with captured_stdin() as stdin:
    #         import pdb; pdb.set_trace()
    #         stdin.write('123\n')
    #         stdin.seek(0)
    #         Entry.create = MagicMock(return_value=True)
    #         test_console = ConsoleUI()
    #         test_console.add_new_entry()
    #     Entry.create.assert_called_with(employee_name='123', task_name='123', task_time=123, task_notes='123')

if __name__ == '__main__':
    unittest.main()