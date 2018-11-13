import unittest

import sublime
from sublime import Region


class WrapAsYouTypeCommandTestBase(unittest.TestCase):
    """Base class for testing WrapAsYouTypeCommand.

    The setUp method creates a View, stored as self._view.  It sets a
    tab size of 4.
    """

    def setUp(self):
        self._view = sublime.active_window().new_file()
        settings = self._view.settings()
        settings.set('tab_size', 4)
        settings.set('translate_tabs_to_spaces', False)
        settings.set('trim_automatic_white_space', True)
        settings.set('wrap_as_you_type_disabled', False)
        settings.set('wrap_as_you_type_paragraphs', None)
        settings.set('wrap_as_you_type_sections', None)
        settings.set('wrap_as_you_type_space_between_words', None)
        settings.set('wrap_as_you_type_word_regex', None)
        settings.set('wrap_width', None)

    def tearDown(self):
        view = self._view
        view.set_scratch(True)
        view.window().focus_view(view)
        view.window().run_command('close_file')

    def _append(self, str_):
        """Append the specified string to the end of the document."""
        self._view.run_command('append', {'characters': str_})

    def _set_selection(self, point):
        """Set the selection cursor to the specified position.

        Replace any existing selection cursor(s).

        int point - The position.
        """
        self._view.sel().clear()
        self._view.sel().add(Region(point, point))

    def _insert(self, point, str_):
        """Perform the specified insert operation, one character at a time.

        This has the effect of setting the selection cursor to the
        specified position, and then virtually typing the keystrokes
        suggested by str_, one at a time.

        int point - The position at which to insert.
        str str_ - The text to insert.
        """
        self._set_selection(point)
        for char in str_:
            self._view.run_command('insert', {'characters': char})

    def _backspace(self, region):
        """Backspace the specified Region.

        This has the effect of setting the selection cursor to the end
        of the specified region, and then virtually pressing backspace
        until the cursor reaches the beginning of the region.
        """
        self._set_selection(region.end())
        while self._view.sel()[0].begin() > region.begin():
            self._view.run_command('left_delete')

    def _delete(self, point, count):
        """Delete from the specified position.

        This has the effect of setting the selection cursor to the
        specified position, and then virtually pressing delete the
        specified number of times.

        int point - The position.
        int count - The number of deletes to perform.
        """
        self._set_selection(point)
        for i in range(count):
            self._view.run_command('right_delete')

    def _set_up_cpp(self):
        """Configure _view to use C++.

        This sets the "wrap_as_you_type_sections" setting to a value
        appropriate to wrapping C++ block and line comments.
        """
        self._view.set_syntax_file('Packages/C++/C++.tmLanguage')
        self._view.settings().set(
            'wrap_as_you_type_sections', [
                {
                    'line_start': ' * ',
                    'selector_rules': {
                        'and': [
                            'comment.block',
                            {'not': 'punctuation.definition.comment'},
                        ],
                    },
                },
                {
                    'combining_selector_rules': {
                        'not': [
                            'comment', 'constant', 'entity', 'invalid',
                            'keyword', 'punctuation', 'storage', 'string',
                            'variable',
                        ],
                    },
                    'line_start': '//',
                    'selector_rules': 'comment.line',
                },
            ])
