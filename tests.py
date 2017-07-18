from collections import OrderedDict
from test.support import captured_stdin
from test.support import captured_stdout
import unittest

from work_log import ConsoleUI


# create a menu that allows you to add entries, lookup entries, or quit
class TestConsoleUI(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()