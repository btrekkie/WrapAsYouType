import unittest

import sublime


class WrapAsYouTypeCommandTestBase(unittest.TestCase):
    """Base class for testing WrapAsYouTypeCommand.

    The setUp method creates a View, stored as self._view.  It sets a
    tab size of 4.
    """

    def setUp(self):
        self._view = sublime.active_window().new_file()
        settings = self._view.settings()
        settings.set('auto_indent', True)
        settings.set('tab_size', 4)
        settings.set('translate_tabs_to_spaces', False)
        settings.set('trim_automatic_white_space', True)
        settings.set('wrap_as_you_type_disabled', False)
        settings.set('wrap_as_you_type_enter_extends_section', False)
        settings.set('wrap_as_you_type_paragraphs', None)
        settings.set('wrap_as_you_type_passive', None)
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

    def _set_selection_point(self, point):
        """Set the selection cursor to the specified position.

        Assume that there is a single selection cursor.

        int point - The position.
        """
        # Do not alter self._view.sel() directly, because that prevents
        # EventListener.on_selection_modified from being called
        view = self._view
        if point < 0 or point > view.size():
            raise ValueError('The specified point is out of range')
        selection = view.sel()
        if len(selection) != 1:
            raise RuntimeError(
                '_set_selection_point requires a single selection cursor')

        if not selection[0].empty():
            # Move the cursor to an arbitrary position, so that the selection
            # is empty
            view.run_command('move', {'by': 'characters', 'forward': True})
        while view.sel()[0].begin() != point:
            view.run_command(
                'move',
                {'by': 'characters', 'forward': point > view.sel()[0].begin()})

    def _set_selection_region(self, region):
        """Set the selection cursor to the specified region.

        Assume that there is a single selection cursor.

        Region region - The region.
        """
        # Do not alter self._view.sel() directly, because that prevents
        # EventListener.on_selection_modified from being called
        self._set_selection_point(region.a)
        while self._view.sel()[0].b != region.b:
            self._view.run_command(
                'move', {
                    'by': 'characters',
                    'extend': True,
                    'forward': region.b > self._view.sel()[0].b,
                })

    def _insert(self, point, str_):
        """Perform the specified insert operation, one character at a time.

        This has the effect of setting the selection cursor to the
        specified position, and then virtually typing the keystrokes
        suggested by str_, one at a time.

        int point - The position at which to insert.
        str str_ - The text to insert.
        """
        self._set_selection_point(point)
        for char in str_:
            self._view.run_command('insert', {'characters': char})

    def _backspace(self, region):
        """Backspace the specified Region.

        This has the effect of setting the selection cursor to the end
        of the specified region, and then virtually pressing backspace
        until the cursor reaches the beginning of the region.
        """
        self._set_selection_point(region.end())
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
        self._set_selection_point(point)
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
                    'selector':
                        'comment.block - '
                        '(punctuation.definition.comment.begin | '
                        'punctuation.definition.comment.end)',
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '//',
                    'selector': 'comment.line',
                },
            ])

    def _set_up_python(self):
        """Configure _view to use Python.

        This sets the "wrap_as_you_type_sections" setting to a value
        appropriate to wrapping Python block and line comments.
        """
        self._view.set_syntax_file('Packages/Python/Python.tmLanguage')
        settings = self._view.settings()
        settings.set(
            'wrap_as_you_type_sections', [
                {
                    'selector':
                        'comment.block - punctuation.definition.comment',
                    'wrap_width': 72
                },
                {
                    'combining_selector':
                        'source - (comment | constant | entity | invalid | '
                        'keyword | punctuation | storage | string | variable)',
                    'line_start': '#',
                    'selector': 'comment.line',
                    'wrap_width': 79,
                },
            ])
        settings.set(
            'wrap_as_you_type_paragraphs', [{'first_line_regex': r'^""?$'}])
