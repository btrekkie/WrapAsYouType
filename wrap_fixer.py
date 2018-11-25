import re
import sys

from sublime import Region
import sublime
import sublime_plugin

if sys.version_info[0] >= 3:
    from .error import UserFacingError
    from .util import Util
else:
    from error import UserFacingError
    from util import Util


class WrapFixer(sublime_plugin.TextCommand):
    """Provides the ability to perform word wrapping fixup.

    "Word wrapping fixup" consists of attempting to fix word wrapping in
    the vicinity of the selection cursor.  WrapFixer is the meat /
    brains of the WrapAsYouType plugin.  Each WrapFixer instance manages
    a particular View.  A WrapFixer instance assumes that the
    on_modified() method is called whenever its view is changed.
    """

    # The main body of wrap fixup is the _gen_edits() method.  It is a
    # coroutine - a generator method that yields a sequence of edits to perform
    # to fix word wrap, and requires each edit to be executed before control is
    # returned to the generator.  Each edit is represented as a pair consisting
    # of a Region and a string, and indicates that any text that is in the
    # Region should be replaced with the given string.
    #
    # A number of variable names recur in the implementation of WrapFixer.  The
    # "indent" of a line is the whitespace on that line that precedes the line
    # start under consideration.  The "i_line_start" (indent + line start) of a
    # line is the result of appending the line start to the indent.  The
    # "i_line_start_i" (indent + line start + indent) of a line is the
    # i_line_start, followed by all of the subsequent whitespace on that line,
    # up to the first non-whitespace character or the end of the line.
    #
    # Private attributes:
    #
    # Generator<tuple<Region, str>> _edits_gen - A coroutine that yields the
    #     edits to execute in order to perform word wrapping fixup: an
    #     execution of the _gen_edits() method.  This will normally be at least
    #     partially executed: if has_edit() has been called, then the first
    #     edit is retrieved as _first_edit, and if perform_edits() has been
    #     called, then all of the edits have been retrieved.  This is None if
    #     the view was altered since the beginning of the most recent call to
    #     has_edit() or perform_edits().
    # tuple<Region, str> _first_edit - The first edit that _edits_gen yielded.
    #     This is None if it did not yield any edits or if _edits_gen is None.
    # list<dict<str, object>> _paragraphs - Equivalent to _paragraphs_setting,
    #     but with the "first_line_regex" entries replaced with re.Patterns
    #     instead of strings (the result of calling re.compile on the entries),
    #     with default values filled in for the "indent" and "single_line"
    #     entries, and with missing "indent_group" entries replaced with None.
    #     This is [] if _paragraphs_setting is not a valid value for
    #     "wrap_as_you_type_paragraphs".
    # object _paragraphs_setting - The value of the
    #     "wrap_as_you_type_paragraphs" setting during the most recent call to
    #     _gen_edits().  This is None if we have not called _gen_edits() or
    #     there is no such setting.
    # list<dict<str, object>> _sections - Equivalent to _sections_setting, but
    #     with any "line_start" entries replaced with single-element
    #     "allowed_line_starts" entries, and with missing "wrap_width" and
    #     "combining_selector" entries replaced with None.  This is [] if
    #     _sections_setting is not a valid value for
    #     "wrap_as_you_type_sections".
    # object _sections_setting - The value of the "wrap_as_you_type_sections"
    #     setting during the most recent call to _gen_edits().  This is None if
    #     we have not called _gen_edits() or there is no such setting.
    # list<dict<str, object>> _space_between_words - Equivalent to
    #     _space_between_words_setting, but with the "first_word_regex" and
    #     "second_word_regex" entries replaced with re.Patterns instead of
    #     strings (the result of calling re.compile on the entries), and with
    #     missing "first_word_regex" and "second_word_regex" entries replaced
    #     with None.  This is [] if _space_between_words_setting is not a valid
    #     value for "wrap_as_you_type_space_between_words".
    # object _space_between_words_setting - The value of the
    #     "wrap_as_you_type_space_between_words" setting during the most recent
    #     call to _gen_edits().  This is None if we have not called
    #     _gen_edits() or there is no such setting.
    # View _view - The View that this WrapFixer manages.
    # re.Pattern _word_regex - The value re.compile(_word_regex_setting).  This
    #     is _DEFAULT_WORD_REGEX if _word_regex_setting is None or is not a
    #     valid value for "wrap_as_you_type_word_regex".
    # object _word_regex_setting - The value of the
    #     "wrap_as_you_type_word_regex" setting during the most recent call to
    #     _gen_edits().  This is None if we have not called _gen_edits() or
    #     there is no such setting.

    # The default value for _word_regex
    _DEFAULT_WORD_REGEX = re.compile(r'\S+')

    # Equivalent value is contractual
    _WHITESPACE_REGEX = re.compile(r'\s*')

    # A regular expression for stripping whitespace from the beginning and end
    # of a string.  The result of the stripping is given by re.Match.group(1).
    _STRIP_REGEX = re.compile(r'^\s*(\S.*\S|\S?)\s*$', re.DOTALL)

    # A regular expression matching all of the whitespace at the end of the
    # source string.  It matches the empty string if there is no such
    # whitespace.
    _TRAILING_WHITESPACE_REGEX = re.compile(r'\s*$')

    # A map to each WrapFixer instance from _view.id()
    _instances = {}

    def __init__(self, view):
        """Private constructor."""
        self._view = view
        self._sections_setting = None
        self._sections = []
        self._word_regex_setting = None
        self._word_regex = WrapFixer._DEFAULT_WORD_REGEX
        self._space_between_words_setting = None
        self._space_between_words = []
        self._paragraphs_setting = None
        self._paragraphs = []
        self._edits_gen = None
        self._first_edit = None

    def _validate_and_compile_regex(self, pattern):
        """Return the result of compiling the specified regular expression.

        Return the result of compiling the specified regular expression,
        as in re.compile(pattern).  Raise UserFacingError if "pattern"
        is not a string or is not a valid regular expression.

        object pattern - The purported Python regular expression string.
        return re.Pattern - The regular expression.
        """
        if not Util.is_string(pattern):
            raise UserFacingError('Regular expressions must be strings')
        try:
            return re.compile(pattern)
        except re.error as exception:
            raise UserFacingError(
                u'Error parsing regular expression {0:s}: {1:s}'.format(
                    pattern, str(exception)))

    def _update_sections(self):
        """Update _sections_setting and _sections.

        Update _sections_setting and _sections to reflect the current
        value of the "wrap_as_you_type_sections" setting.  Raise a
        UserFacingError (and set _sections to []) if the setting is
        invalid.
        """
        section_setting = self._view.settings().get(
            'wrap_as_you_type_sections')
        if section_setting == self._sections_setting:
            return
        self._sections_setting = section_setting
        self._sections = []
        if section_setting is None:
            return

        if not isinstance(section_setting, list):
            raise UserFacingError(
                '"wrap_as_you_type_sections" must be an array')
        sections = []
        for section in section_setting:
            if not isinstance(section, dict):
                raise UserFacingError(
                    'The elements of "wrap_as_you_type_sections" must be '
                    'objects')

            wrap_width = section.get('wrap_width')
            if ('wrap_width' in section and
                    (not Util.is_int(wrap_width) or wrap_width <= 0)):
                raise UserFacingError(
                    '"wrap_width" must be a positive integer')

            # Line start
            if 'line_start' in section and 'allowed_line_starts' in section:
                raise UserFacingError(
                    'A section may not have both "line_start" and '
                    '"allowed_line_starts" entries')
            if 'line_start' in section:
                line_start = section['line_start']
                if not Util.is_string(line_start):
                    raise UserFacingError('"line_start" must be a string')
                allowed_line_starts = [line_start]
            elif 'allowed_line_starts' in section:
                allowed_line_starts = section['allowed_line_starts']
                if not isinstance(allowed_line_starts, list):
                    raise UserFacingError(
                        '"allowed_line_starts" must be an array')
                if not allowed_line_starts:
                    raise UserFacingError(
                        '"allowed_line_starts" must not be empty')
                for line_start in allowed_line_starts:
                    if not Util.is_string(line_start):
                        raise UserFacingError(
                            'The elements of "allowed_line_starts" must be '
                            'strings')
            else:
                allowed_line_starts = ['']

            if 'selector' not in section:
                raise UserFacingError('Missing "selector" entry')
            selector = section['selector']
            if not Util.is_string(selector):
                raise UserFacingError('"selector" must be a string')

            combining_selector = section.get('combining_selector', selector)
            if ('combining_selector' in section and
                    not Util.is_string(combining_selector)):
                raise UserFacingError('"combining_selector" must be a string')

            sections.append({
                'allowed_line_starts': allowed_line_starts,
                'combining_selector': combining_selector,
                'selector': selector,
                'wrap_width': wrap_width,
            })
        self._sections = sections

    def _update_word_regex(self):
        """Update _word_regex_setting and _word_regex.

        Update _word_regex_setting and _word_regex to reflect the
        current value of the "wrap_as_you_type_word_regex" setting.
        Raise a UserFacingError (and set _word_regex to
        _DEFAULT_WORD_REGEX) if the setting is invalid.
        """
        word_regex_setting = self._view.settings().get(
            'wrap_as_you_type_word_regex')
        if word_regex_setting != self._word_regex_setting:
            self._word_regex_setting = word_regex_setting
            self._word_regex = WrapFixer._DEFAULT_WORD_REGEX
            if word_regex_setting is not None:
                self._word_regex = self._validate_and_compile_regex(
                    word_regex_setting)

    def _update_space_between_words(self):
        """Update _space_between_words_setting and _space_between_words.

        Update _space_between_words_setting and _space_between_words to
        reflect the current value of the
        "wrap_as_you_type_space_between_words" setting.  Raise a
        UserFacingError (and set _space_between_words to []) if the
        setting is invalid.
        """
        space_between_words_setting = self._view.settings().get(
            'wrap_as_you_type_space_between_words')
        if space_between_words_setting == self._space_between_words_setting:
            return
        self._space_between_words_setting = space_between_words_setting
        self._space_between_words = []
        if space_between_words_setting is None:
            return

        if not isinstance(space_between_words_setting, list):
            raise UserFacingError(
                '"wrap_as_you_type_space_between_words" must be an array')
        space_between_words = []
        for item in space_between_words_setting:
            if not isinstance(item, dict):
                raise UserFacingError(
                    'The elements of "wrap_as_you_type_space_between_words" '
                    'must be objects')

            if 'first_word_regex' not in item:
                first_word_regex = None
            else:
                first_word_regex = self._validate_and_compile_regex(
                    item['first_word_regex'])
            if 'second_word_regex' not in item:
                second_word_regex = None
            else:
                second_word_regex = self._validate_and_compile_regex(
                    item['second_word_regex'])

            if 'space' not in item:
                raise UserFacingError('Missing "space" entry')
            space = item['space']
            if not Util.is_string(space):
                raise UserFacingError('"space" entry must be a string')
            if not self._is_all_whitespace(space):
                raise UserFacingError(
                    '"space" entry must consist exclusively of whitespace')

            space_between_words.append({
                'first_word_regex': first_word_regex,
                'second_word_regex': second_word_regex,
                'space': space,
            })
        self._space_between_words = space_between_words

    def _update_paragraphs(self):
        """Update _paragraphs_setting and _paragraphs.

        Update _paragraphs_setting and _paragraphs to reflect the
        current value of the "wrap_as_you_type_paragraphs" setting.
        Raise a UserFacingError (and set _paragraphs to []) if the
        setting is invalid.
        """
        paragraphs_setting = self._view.settings().get(
            'wrap_as_you_type_paragraphs')
        if paragraphs_setting == self._paragraphs_setting:
            return
        self._paragraphs_setting = paragraphs_setting
        self._paragraphs = []
        if paragraphs_setting is None:
            return

        if not isinstance(paragraphs_setting, list):
            raise UserFacingError(
                '"wrap_as_you_type_paragraphs" must be an array')
        paragraphs = []
        for paragraph in paragraphs_setting:
            if not isinstance(paragraph, dict):
                raise UserFacingError(
                    'The elements of "wrap_as_you_type_paragraphs" must be '
                    'objects')

            if 'first_line_regex' not in paragraph:
                raise UserFacingError('Missing "first_line_regex" entry')
            first_line_regex = self._validate_and_compile_regex(
                paragraph['first_line_regex'])

            indent = paragraph.get('indent', '')
            if 'indent' in paragraph:
                if not Util.is_string(indent):
                    raise UserFacingError('"indent" entry must be a string')
                if not self._is_all_whitespace(indent):
                    raise UserFacingError(
                        '"indent" entry must consist exclusively of '
                        'whitespace')

            indent_group = paragraph.get('indent_group')
            if 'indent_group' in paragraph:
                if Util.is_int(indent_group):
                    if not (0 <= indent_group <= first_line_regex.groups):
                        raise UserFacingError(
                            'The "first_line_regex" entry does not have a '
                            'group {0:d}'.format(indent_group))
                elif Util.is_string(indent_group):
                    if indent_group not in first_line_regex.groupindex:
                        raise UserFacingError(
                            u'The "first_line_regex" entry does not have a '
                            'group named {0:s}'.format(indent_group))
                else:
                    raise UserFacingError(
                        '"indent_group" entry must be a string or an integer')

            single_line = paragraph.get('single_line', False)
            if not isinstance(single_line, bool):
                raise UserFacingError('"single_line" entry must be a boolean')
            if (single_line and
                    ('indent' in paragraph or indent_group is not None)):
                raise UserFacingError(
                    'If "single_line" is true, then the "indent" and '
                    '"indent_group" entries may not be present')

            paragraphs.append({
                'first_line_regex': first_line_regex,
                'indent': indent,
                'indent_group': indent_group,
                'single_line': single_line,
            })
        self._paragraphs = paragraphs

    def _update_settings(self):
        """Update all of the fields that are derived from the settings.

        Update all of the fields that are derived from the settings:
        _sections_setting, _sections, _word_regex_setting, etc.
        """
        has_error_ref = [False]

        def update_setting(setting, update_func):
            try:
                update_func()
            except UserFacingError as exception:
                has_error_ref[0] = True
                print(
                    u'WrapAsYouType error: error in "{0:s}" setting: '
                    '{1:s}'.format(setting, str(exception)))

        update_setting('wrap_as_you_type_sections', self._update_sections)
        update_setting('wrap_as_you_type_word_regex', self._update_word_regex)
        update_setting(
            'wrap_as_you_type_space_between_words',
            self._update_space_between_words)
        update_setting('wrap_as_you_type_paragraphs', self._update_paragraphs)

        if has_error_ref[0]:
            Util.status_message(
                self._view.window(),
                'WrapAsYouType settings error; see console')

    def _add_width(self, width, char, tab_size):
        """Return the resulting width after adding the specified character.

        Return the width (number of columns) that results from appending
        the specified character to a line of the specified width.
        Assume that char is not a newline character.

        Note that this method is conceptually faulty.  See the comments
        for _width for details.

        int width - The width of the line prior to adding "char".
        str char - The character.
        int tab_size - The number of columns per tab.
        return int - The width after adding "char".
        """
        if char != '\t':
            return width + 1
        else:
            return (width // tab_size) * tab_size + tab_size

    def _width(self, line):
        """Return the width of the specified line of text.

        Return the width (number of columns) of the specified line of
        text.  Assume that "line" does not contain any newline
        characters.

        Note that this method is conceptually faulty.  It assumes that
        there is one character per Unicode code point, but this is not
        always true, e.g. for Thai characters.  However, at the time of
        writing, Sublime Text renders each Unicode code point as one
        character, so the behavior of this method conforms to that of
        Sublime.  See
        https://github.com/SublimeTextIssues/Core/issues/663 .
        """
        tab_size = self._view.settings().get('tab_size')
        width = 0
        for char in line:
            width = self._add_width(width, char, tab_size)
        return width

    def _advance_by_width(self, line, width):
        """Return the character at column "width" of "line".

        Return the index of the first character in the specified line of
        text that is at or beyond the specified width (number of
        columns).  For example, _advance_by_width('foo bar', 4) returns
        4.  Assume that "line" does not contain any newline characters.

        Note that this method is conceptually faulty.  See the comments
        for _width for details.
        """
        tab_size = self._view.settings().get('tab_size')
        width_traveled = 0
        for i, char in enumerate(line):
            if width_traveled >= width:
                return i
            width_traveled = self._add_width(width_traveled, char, tab_size)
        return len(line)

    def _wrap_width(self, section):
        """Return the wrap width of the specified section.

        If section['wrap_width'] is None, this method uses the
        appropriate fallback.

        dict<str, object> section - The section, formatted like the
            elements of _sections.
        return int - The wrap width.
        """
        if section['wrap_width'] is not None:
            return section['wrap_width']
        settings = self._view.settings()
        wrap_width = settings.get('wrap_width')
        if wrap_width:
            return wrap_width
        rulers = settings.get('rulers')
        if rulers:
            return rulers[0]
        else:
            return 80

    def _prev_line_region(self, point):
        """Return the Region containing the previous line.

        Return the Region containing the line before the line that
        contains "point", excluding newline characters, if any.

        int point - The point.
        return Region - The previous line region.
        """
        view = self._view
        row = view.rowcol(point)[0]
        if row > 0:
            return view.line(view.text_point(row - 1, 0))
        else:
            return None

    def _next_line_region(self, point):
        """Return the Region containing the next line.

        Return the Region containing the line after the line that
        contains "point", excluding newline characters, if any.

        int point - The point.
        return Region - The next line region.
        """
        view = self._view
        line_region = view.full_line(point)
        if line_region.end() < view.size():
            return view.line(line_region.end())
        else:
            return None

    def _leading_whitespace(self, str_, start=0):
        """Return the whitespace at the beginning of the specified string.

        Return all of the whitespace at the beginning of str_[start:].
        Return '' if there is no such whitespace.

        str str_ - The string.
        int start - The starting index.
        return str - The leading whitespace.
        """
        return WrapFixer._WHITESPACE_REGEX.match(str_, start).group()

    def _end_point_excluding_whitespace(self, str_, region):
        """Return the latest point in "region" that is a whitespace character.

        Return the point of (or rather, immediately before) the latest
        character in "region" that is a whitespace character.  Return
        region.end() if the last character is not a whitespace
        character.  Return region.begin() if all of the characters are
        whitespace characters.

        str str_ - The value of _view.substr(region).
        Region region - The region.
        return int - The point.
        """
        match = WrapFixer._TRAILING_WHITESPACE_REGEX.search(str_)
        return region.end() - match.end() + match.start()

    def _is_all_whitespace(self, str_):
        """Return whether the specified string consists only of whitespace."""
        match = WrapFixer._WHITESPACE_REGEX.match(str_)
        return match.span() == (0, len(str_))

    def _section_indent(self, line, line_start):
        """Return the whitespace at the beginning of "line" before line_start.

        For example, _section_indent('   * Foo', ' * ') returns '  ',
        because there are two spaces prior to the space-asterisk-space.
        Assume that "line" does not contain any newline characters.
        Return None if "line" does not start with whitespace followed by
        line_start.  If line_start consists exclusively of whitespace,
        so that there are multiple possible matches, return the shortest
        possible match.

        str line - The line of text to match.
        str line_start - The line start.
        return str - The whitespace before line_start.
        """
        line_indent = self._leading_whitespace(line)
        if self._is_all_whitespace(line_start):
            index = line_indent.find(line_start)
            if index >= 0:
                return line_indent[:index]
            else:
                return None
        else:
            line_start_indent = self._leading_whitespace(line_start)
            section_indent_length = len(line_indent) - len(line_start_indent)
            if (line_indent.endswith(line_start_indent) and
                    line[
                        len(line_indent):
                        section_indent_length + len(line_start)] ==
                    line_start[len(line_start_indent):]):
                return line_indent[:section_indent_length]
            else:
                return None

    def _i_line_start_i(self, line, line_start):
        """Return the i_line_start_i of the specified line.

        str line - The line of text.
        str line_start - The line start.
        return str - The i_line_start_i.
        """
        indent = self._section_indent(line, line_start)
        if indent is None:
            return None
        post_indent = self._leading_whitespace(
            line, len(indent) + len(line_start))
        return line[:len(indent) + len(line_start) + len(post_indent)]

    def _fix_word_spans(self, raw_spans, str_):
        """Fix errors in the results of applying "wrap_as_you_type_word_regex".

        Return a list of word spans that is like raw_spans, but after
        applying adjustments needed to make the results permissible for
        "wrap_as_you_type_word_regex".  Per README.md,
        "wrap_as_you_type_word_regex" may not produce non-empty words,
        and it must produce words that cover all non-whitespace
        characters.  If raw_spans does not meet these conditions,
        _fix_word_spans attempts to produce similar results that do.
        _fix_word_spans may warn the user of the error.

        list<tuple<int, int>> raw_spans - The word spans produced by
            "wrap_as_you_type_word_regex", formatted like the return
            value of _word_spans.
        str str_ - The string from which the words are taken.
        return list<tuple<int, int>> - The adjusted word spans,
            formatted like the return value of _word_spans.
        """
        # Remove zero-character words
        non_empty_spans = [span for span in raw_spans if span[0] != span[1]]
        warn = len(non_empty_spans) < len(raw_spans)

        # Check each gap between adjacent words (and at the beginning and end
        # of the string) for non-whitespace characters
        spans = []
        for i in range(0, len(non_empty_spans) + 1):
            # Identify the gap
            if i > 0:
                gap_start_index = non_empty_spans[i - 1][1]
            else:
                gap_start_index = 0
            if i < len(non_empty_spans):
                gap_end_index = non_empty_spans[i][0]
            else:
                gap_end_index = len(str_)
            gap = str_[gap_start_index:gap_end_index]

            # Check for non-whitespace characters
            match = WrapFixer._STRIP_REGEX.search(gap)
            if match.start(1) < match.end(1):
                # The gap has a non-whitespace character.  Add a word that
                # covers the non-whitespace characters.
                warn = True
                spans.append((
                    gap_start_index + match.start(1),
                    gap_start_index + match.end(1)))

            if i < len(non_empty_spans):
                spans.append(non_empty_spans[i])

        if warn:
            raw_words = [str_[span[0]:span[1]] for span in raw_spans]
            print(
                u'WrapAsYouType error: The "wrap_as_you_type_word_regex" '
                'setting is faulty, because on the string {0:s}, it yielded '
                'either an empty word, or a gap between words that had '
                'non-whitespace characters.  It produced the following words: '
                '{1:s}.  WrapAsYouType has corrected for this, but you should '
                'fix the setting.'.format(repr(str_.strip()), str(raw_words)))
            Util.status_message(
                self._view.window(),
                'WrapAsYouType settings error; see console')
        return spans

    def _word_spans(self, str_):
        """Return the locations of the words in str_.

        Return the locations of the words in str_, based on the value of
        _word_regex (and after applying any corrections suggested by
        _fix_word_spans).

        str str_ - The string to search.
        return list<tuple<int, int>> - The positions of the words.  Each
            element is a pair indicating the start and end indices of
            the span (the index of the first character, and the index of
            the position right after the last character).  The elements
            are in order.
        """
        # Trim whitespace
        match = WrapFixer._STRIP_REGEX.search(str_)
        trimmed_str = match.group(1)
        if not trimmed_str:
            return []
        trimmed_str_start_index = match.start(1)

        # Compute the words
        spans = []
        for match in self._word_regex.finditer(trimmed_str):
            spans.append((
                trimmed_str_start_index + match.start(),
                trimmed_str_start_index + match.end()))

        # Fix any problems with the words
        if self._word_regex != WrapFixer._DEFAULT_WORD_REGEX:
            return self._fix_word_spans(spans, str_)
        else:
            # Optimization: _DEFAULT_WORD_REGEX is trustworthy, so don't bother
            # calling _fix_word_spans
            return spans

    def _space_between(self, first_word, second_word):
        """Return the space to use between the specified words.

        Return the space to use between the specified words, as
        suggested by _space_between_words.  The space is a string
        consisting of whitespace characters.  It may be the empty string
        ''.

        str first_word - The word before the space.
        str second_word - The word after the space.
        return str - The space.
        """
        for item in self._space_between_words:
            if ((item['first_word_regex'] is None or
                    item['first_word_regex'].search(
                        first_word) is not None) and
                    (item['second_word_regex'] is None or
                        item['second_word_regex'].search(
                            second_word) is not None)):
                return item['space']
        return ' '

    def _combine_extent(self, section, first_point, second_point):
        """Return the furthest that we can combine a section.

        Return the furthest point that we can combine first_point with
        in the specified section, based on section['combining_selector']
        and section['selector'], as we move from first_point to
        second_point.  So if second_point > first_point, this is the
        latest point that is no later than second_point that we can
        combine with first_point, and vice versa if second_point <
        first_point.  _combine_extent does not check whether first_point
        matches the section (as in _point_matches_selector).

        dict<str, object> section - The section, formatted like the
            elements of _sections.
        int first_point - The starting point.
        int second_point - The ending point.
        return int - The furthest point we can combine.
        """
        # Determine the range of points on which to check score_selector
        view = self._view
        if first_point >= second_point:
            points = range(first_point - 1, second_point - 1, -1)
        elif view.rowcol(second_point)[1] > 0:
            points = range(first_point, second_point)
        else:
            # Special-case the first character of a line; see the comment below
            points = range(first_point, second_point + 1)

        prev_scope = None
        for point in points:
            scope = view.scope_name(point)
            if scope == prev_scope:
                # Optimization: Avoid relatively expensive calls to
                # score_selector
                continue

            if (sublime.score_selector(scope, section['selector']) == 0 and
                    (section['combining_selector'] is None or
                        sublime.score_selector(
                            scope, section['combining_selector']) == 0)):
                if first_point >= second_point:
                    return point + 1
                elif view.rowcol(point)[1] > 0:
                    return point
                else:
                    # Special-case the first character of a line.  In a typical
                    # Sublime syntax file, a line-based scope (e.g. a
                    # comment.line) includes the newline character at the end
                    # of the line.  This does not seem quite proper to me, but
                    # in any event it necessitates this special case.
                    return point - 1
            prev_scope = scope
        return second_point

    def _are_combined(self, section, first_point, second_point):
        """Return whether we can combine the specified points.

        Return whether we can combine second_point with first_point in
        the specified section, based on section['combining_selector']
        and section['selector'], by moving from first_point to
        second_point.  _are_combined does not check whether first_point
        matches the section (as in _point_matches_selector).

        dict<str, object> section - The section, formatted like the
            elements of _sections.
        int first_point - The starting point.
        int second_point - The ending point.
        return bool - Whether we can combine second_point with
            first_point.
        """
        return (
            self._combine_extent(section, first_point, second_point) ==
            second_point)

    def _prev_char_scope(self, point, line_region):
        """Return the scope associated with the character before "point".

        Return the scope associated with the character before "point",
        as in _view.scope_name, but if that is a line break character,
        return None instead.

        In a typical Sublime syntax file, a line-based scope (e.g. a
        comment.line) includes the newline character at the end of the
        line.  This does not seem quite proper to me, but in any event
        it requires special behavior in _matches_selector and
        _point_matches_selector concerning the beginning of the line.
        This is why _prev_char_scope returns None at the beginning of a
        line.

        int point - The point.
        Region line_region - The value of _view.line(point).
        return str - The scope.
        """
        if point > line_region.begin():
            return self._view.scope_name(point - 1)
        else:
            return None

    def _matches_selector(self, section, prev_char_scope, next_char_scope):
        """Return whether a position with the given scopes matches "section".

        Return whether a position with the specified preceding and
        succeeding scopes matches "section", based on
        section['selector'].

        We should conceive of a match as being performed not on a
        character, but on the point between two characters.  See the
        comments for _point_matches_selector for more information.

        dict<str, object> section - The section, formatted like the
            elements of _sections.
        str prev_char_scope - The result of calling _prev_char_scope on
            the position.
        str next_char_scope - The scope of the succeeding character, as
            returned by _view.scope_name.
        return bool - Whether the position matches.
        """
        return (
            (prev_char_scope is not None and
                sublime.score_selector(
                    prev_char_scope, section['selector']) > 0) or
            sublime.score_selector(next_char_scope, section['selector']) > 0)

    def _point_matches_selector(self, section, point, line_region):
        """Return whether the specified point matches "section".

        Return whether the specified point matches "section", based on
        section['selector'].

        We should conceive of a match as being performed not on a
        character, but on the point between two characters.  For
        example, in C++ block comments, a selection cursor that is
        immediately before the /* is in the block comment, even though
        the preceding character is not.  Likewise, a selection cursor
        that is immediately after the */ is in the block comment, even
        though the succeeding character is not.

        dict<str, object> section - The section, formatted like the
            elements of _sections.
        int point - The position.
        Region line_region - The value of _view.line(point).
        return bool - Whether the position matches.
        """
        return self._matches_selector(
            section, self._prev_char_scope(point, line_region),
            self._view.scope_name(point))

    def _is_first_line_of_paragraph(self, line):
        """Return whether the specified line matches an element of _paragraphs.

        Return whether the specified line matches a "first_line_regex"
        entry in _paragraphs.

        str line - The line.
        return bool - Whether the line matches.
        """
        for paragraph in self._paragraphs:
            if paragraph['first_line_regex'].search(line) is not None:
                return True
        return False

    def _paragraph_indent(self, line):
        """Return the relative indentation of the line after "line".

        Return the indentation of the line after the specified line,
        relative to the indentation of the specified line, if the
        subsequent line is in the same paragraph.  Return None instead
        if the line is part of a single-line paragraph, as in the
        "single_line" entry of elements of the
        "wrap_as_you_type_paragraphs" setting.

        str line - The line.
        return str - The indentation.  This consists exclusively of
            whitespace characters.
        """
        for paragraph in self._paragraphs:
            match = paragraph['first_line_regex'].search(line)
            if match is not None:
                if paragraph['single_line']:
                    return None

                indent_group = paragraph['indent_group']
                if indent_group is None:
                    return paragraph['indent']
                else:
                    group = match.group(indent_group)
                    if group is None:
                        return paragraph['indent']
                    else:
                        components = []
                        for char in group:
                            components.append(' ' if char != '\t' else '\t')
                        return ''.join(components)
        return ''

    def _same_paragraph_line(
            self, section, point, first_line, second_line,
            first_line_region, second_line_region, line_start):
        """Determine whether the specified lines are in the same paragraph.

        Determine whether the specified consecutive lines are in the
        same paragraph.  If so, return the text in the second line - the
        result of taking that line, removing any characters that are not
        in the same section as "point", removing the line start, and
        then removing any leading or trailing whitespace.  If not,
        return None.

        Note that first_line and second_line need not currently be
        individual lines; they may be portions of the document that we
        are considering as if they were consecutive lines.

        dict<str, object> section - The current section, formatted like
            the elements of _sections.
        int point - The current position.  This must be in
            first_line_region or second_line_region.
        str first_line - The text of the first line.
        str second_line - The text of the second line.
        Region first_line_region - The region containing first_line.
        Region second_line_region - The region containing second_line.
        str line_start - The line start.
        return str - The second line's text, if it is in the same
            paragraph.
        """
        # Compute the lines' indents
        indent = self._section_indent(first_line, line_start)
        if indent is None:
            return None
        second_indent = self._section_indent(second_line, line_start)
        if second_indent != indent:
            return None

        # Compute the lines' text, before applying _combine_extent
        i_line_start_len = len(indent) + len(line_start)
        first_line_text = first_line[i_line_start_len:].strip()
        second_line_text = second_line[i_line_start_len:].strip()
        if not first_line_text or not second_line_text:
            return None

        # Compute the lines' post-line-start indents
        first_paragraph_indent = self._leading_whitespace(
            first_line[i_line_start_len:])
        second_paragraph_indent = self._leading_whitespace(
            second_line[i_line_start_len:])
        if not second_paragraph_indent.startswith(first_paragraph_indent):
            return None

        # Check whether the indentation of the second line is correct for a
        # same-paragraph match
        paragraph_indent = self._paragraph_indent(first_line_text)
        if (paragraph_indent is None or
                second_paragraph_indent[len(first_paragraph_indent):] !=
                paragraph_indent):
            return None

        # Restrict second_line_text by _combine_extent
        combine_extent = self._combine_extent(
            section, point,
            second_line_region.begin() + i_line_start_len +
            len(second_paragraph_indent) + len(second_line_text))
        if (combine_extent <
                second_line_region.begin() + i_line_start_len +
                len(second_paragraph_indent) + 1):
            # "point" does not combine with any text on the second line
            return None
        second_line_extent_text = second_line_text[
            :combine_extent - second_line_region.begin() - i_line_start_len -
            len(second_paragraph_indent)].strip()
        if not second_line_extent_text:
            return None

        if (self._is_first_line_of_paragraph(second_line_extent_text) or
                not self._are_combined(
                    section, point, first_line_region.begin())):
            return None
        return second_line_extent_text

    def _should_erase_preceding_line_break(
            self, section, point, line_start, line, line_region, prev_line,
            prev_line_region, prev_end_point_excluding_whitespace,
            prev_char_scope, next_char_scope):
        """Return whether we should erase the preceding line break.

        Return whether we should erase all of the text from the most
        recent line break up to the selection cursor, if we are using
        the specified section and line start.  We also erase any
        trailing whitespace on the line before the line break.  Assume
        that there is a single, non-empty selection cursor.

        We perform such an erasure when it appears that the user is
        backspacing content from before the earliest text on the current
        line.  To the user, the effect is like deleting the space
        between the last word on the preceding line and the first word
        on the current line.  The purpose of the erasure is to make it
        feel more like editing non-wrapped text content to the user (or
        rather, like editing soft-wrapped content that doesn't have any
        indentation or line start).

        dict<str, object> section - The section we are attempting to
            use, formatted like the elements of _sections.
        int point - The position of the selection cursor.
        str line_start - The line start we are attempting to use.
        str line - The value of _view.substr(line_region).
        Region line_region - The value of _view.line(point).
        str prev_line - The value of _view.substr(prev_line_region).
            This is None if prev_line_region is None.
        Region prev_line_region - The value of _prev_line_region(point).
        int prev_end_point_excluding_whitespace - The value of
            _end_point_excluding_whitespace(prev_line,
            prev_line_region).  This is None if prev_line is None.
        str prev_char_scope - The value of
            _prev_char_scope(prev_line_region.end(), prev_line_reigon).
            This is None if prev_line_region is None.
        str next_char_scope - The value of
            _view.scope_name(prev_line_region.end()).  This is None if
            prev_line_region is None.
        return bool - Whether we should erase the preceding line break.
        """
        if (prev_line_region is None or self._is_all_whitespace(line) or
                # If line_start consists exclusively of whitespace, then the
                # setting is too generic to be confident that the user
                # backspaced past the beginning of a line
                self._is_all_whitespace(line_start)):
            return False

        # Check whether the user appears to have backspaced part of the
        # indentation
        indent = self._section_indent(prev_line, line_start)
        if (indent is None or line.startswith(indent) or
                line[:point - line_region.begin()] !=
                indent[:point - line_region.begin()]):
            return False

        # Check whether prev_line has at least one word
        if self._is_all_whitespace(prev_line[len(indent) + len(line_start):]):
            return False

        # Check whether the first thing after "point" is line_start, in which
        # case the user only appears to be editing the indentation
        if (self._section_indent(
                line[point - line_region.begin():], line_start) is not None):
            return False

        # Check whether prev_line.begin() and "point" are in a single section
        if (not self._matches_selector(
                section, prev_char_scope, next_char_scope) or
                not self._are_combined(
                    section, prev_line_region.begin(), point)):
            return False
        return True

    def _erase_preceding_line_break_edit(self, point):
        """Return a pair with an edit for erasing the preceding line break.

        Return a pair whose first element is an edit for erasing all of
        the text from the most recent line break character up to the
        selection cursor.  This also erases any trailing whitespace on
        the line before the line break.  The second element of the
        return value is the recommended new point - the position to
        which "point" is moved after the erasure.  Clients ought to
        check that _should_erase_preceding_line_break returns True
        before calling this method.  See the comments for
        _should_erase_preceding_line_break for more information
        concerning the motivation of such an edit.

        int point - The position.
        return tuple<tuple<Region, str>, int> - A pair consisting of the
            edit and the new position, respectively.
        """
        # Compute the region to erase
        view = self._view
        line_region = view.line(point)
        line = view.substr(line_region)
        prev_line_region = self._prev_line_region(point)
        prev_line = view.substr(prev_line_region)
        erase_start_point = self._end_point_excluding_whitespace(
            prev_line, prev_line_region)
        erase_end_point = (
            line_region.begin() + len(self._leading_whitespace(line)))
        erase_region = Region(erase_start_point, erase_end_point)

        # Return the edit and the new position
        edit = (erase_region, '')
        if point <= erase_region.begin():
            return (edit, point)
        elif point <= erase_region.end():
            return (edit, erase_region.begin())
        else:
            return (edit, point - erase_region.size())

    def _try_remove_indent_of_next_line_edit(self, section, point, line_start):
        r"""Return an edit for removing subsequent indentation, if appropriate.

        Return an edit for removing the text from "point" up to what
        appears to be the end of the former i_line_start_i of the next
        line, or None if we should not remove such text.

        The goal here is to help the user when he presses the "delete"
        key at the end of a line.  For example, if the line start is
        " * ", the current line of text reads, "   * Foo bar   * baz",
        and the selection cursor is immediately after the word "bar",
        then it looks as though the document used to read,
        "   * Foo bar\n   * baz", and the user just deleted the newline
        character.  In this case, we erase text so that the line reads,
        "   * Foo barbaz" instead.  The purpose of the erasure is to
        make it feel more like editing non-wrapped text content to the
        user (or rather, like editing soft-wrapped content that doesn't
        have any indentation or line start).

        dict<str, object> section - The current section, formatted like
            the elements of _sections.
        int point - The position.
        str line_start - The line start.
        return tuple<Region, str> - The edit, if any.
        """
        line_region = self._view.line(point)
        line = self._view.substr(line_region)
        first_line = line[:point - line_region.begin()]
        second_line = line[point - line_region.begin():]
        i_line_start_i = self._i_line_start_i(second_line, line_start)
        if (i_line_start_i is None or
                self._leading_whitespace(i_line_start_i) in ('', ' ', '  ')):
            # i_line_start_i is too generic for us to confidently guess that
            # the user deleted a newline character
            return None

        # Check _point_matches_selector
        if not self._point_matches_selector(section, point, line_region):
            return None

        # Check whether the "lines" are in the same paragraph
        if (self._same_paragraph_line(
                section, point, first_line, second_line,
                Region(line_region.begin(), point),
                Region(point, line_region.end()), line_start) is None):
            return None

        # Return the edit
        erase_region = Region(point, point + len(i_line_start_i))
        return (erase_region, '')

    def _try_split_edit(self, section, point, line_start):
        """Return a pair containing the edit for splitting the line, if any.

        Return a pair whose first element is the edit for splitting the
        line containing "point", if we should do so.  If the line is
        longer than the wrap width, and it contains at least two words,
        then we split the line after the latest word that is no later
        than the wrap width (or the first word if there is no such
        word), assuming the split is contained in a single section.
        Note that it may take multiple split operations to reduce the
        line down to lines that are all no longer than the wrap width.
        The second element of the return value is the recommended new
        point - the later of the position to which "point" is moved
        after the split, and the position after the i_line_start_i of
        the added line.  This method returns (None, None) if we should
        not perform a split operation.

        dict<str, object> section - The current section, formatted like
            the elements of _sections.
        int point - The current position.
        str line_start - The line start.
        return tuple<tuple<Region, str>, int> - A pair consisting of the
            edit and the new position, respectively.
        """
        # Compute the words on the current line
        view = self._view
        line_region = view.line(point)
        line = view.substr(line_region)
        i_line_start_i = self._i_line_start_i(line, line_start)
        if i_line_start_i is None:
            return (None, None)
        word_spans = self._word_spans(line[len(i_line_start_i):])
        if len(word_spans) <= 1:
            return (None, None)

        # Check whether the line is longer than the wrap width
        wrap_width = self._wrap_width(section)
        wrap_index = self._advance_by_width(line, wrap_width)
        if wrap_index >= len(i_line_start_i) + word_spans[-1][1]:
            return (None, None)

        # Compute the last word on this line and the first word on the next
        # line, post-split
        last_word_span = None
        first_word_span = None
        if len(i_line_start_i) + word_spans[0][1] > wrap_index:
            # The first word does not fit on one line
            last_word_span = word_spans[0]
            first_word_span = word_spans[1]
        else:
            for span in word_spans:
                if len(i_line_start_i) + span[1] <= wrap_index:
                    last_word_span = span
                else:
                    first_word_span = span
                    break
        last_word_region = Region(
            line_region.begin() + len(i_line_start_i) + last_word_span[0],
            line_region.begin() + len(i_line_start_i) + last_word_span[1])
        first_word_region = Region(
            line_region.begin() + len(i_line_start_i) + first_word_span[0],
            line_region.begin() + len(i_line_start_i) + first_word_span[1])

        # Check whether "point" is in the same section as
        # first_word_region.end() and line_region.begin()
        if (not self._point_matches_selector(section, point, line_region) or
                not self._are_combined(
                    section, point, first_word_region.end()) or
                not self._are_combined(section, point, line_region.begin())):
            return (None, None)

        # Compute the edit
        selection_point = view.sel()[0].begin()
        if (last_word_region.end() < selection_point <=
                first_word_region.begin()):
            # Keep any spaces (or tabs) that are just before the cursor at the
            # end of the first line in the split
            replace_start_point = selection_point
        else:
            replace_start_point = last_word_region.end()
        replace_region = Region(replace_start_point, first_word_region.begin())
        line_text = line[
            len(i_line_start_i):last_word_region.end() - line_region.begin()]
        paragraph_indent = self._paragraph_indent(line_text)
        if paragraph_indent is None:
            paragraph_indent = ''
        replacement_str = u'\n{0:s}{1:s}'.format(
            i_line_start_i, paragraph_indent)
        edit = (replace_region, replacement_str)

        # Return the edit and the new position
        if point <= replace_region.end():
            return (edit, replace_region.begin() + len(replacement_str))
        else:
            return (edit, point - replace_region.size() + len(replacement_str))

    def _try_join_edit(self, section, point, line_start):
        """Return a pair containing the edit for joining, if any.

        Return a pair whose first element is the edit for joining the
        line containing "point" with the subsequent line, if we should
        do so.  If adding the first word on the next line to the current
        line results in a line that is no longer than the wrap width,
        then we join the text on the two lines, assuming they are in the
        same paragraph and section.  This would be followed up with a
        split operation (as in _try_split_edit) if necessary to ensure
        that the current line is no longer than the wrap width.  The
        second element of the return value is the recommended new
        point - the position of the former end of the line containing
        "point".  This method returns (None, None) if we should not
        perform a join operation.

        dict<str, object> section - The current section, formatted like
            the elements of _sections.
        int point - The current position.
        str line_start - The line start.
        return tuple<tuple<Region, str>, int> - A pair consisting of the
            edit and the new position, respectively.
        """
        # Check _point_matches_selector
        view = self._view
        line_region = view.line(point)
        line = view.substr(line_region)
        next_line_region = self._next_line_region(point)
        if next_line_region is None:
            return (None, None)
        next_line = view.substr(next_line_region)
        if not self._point_matches_selector(section, point, line_region):
            return (None, None)

        # Check whether the lines are in the same paragraph
        next_line_extent_text = self._same_paragraph_line(
            section, point, line, next_line, line_region, next_line_region,
            line_start)
        if next_line_extent_text is None:
            return (None, None)

        # Compute the last word on this line and the first word on the next
        # line
        i_line_start_i_len = len(self._i_line_start_i(line, line_start))
        last_word_span = self._word_spans(line[i_line_start_i_len:])[-1]
        last_word = line[
            i_line_start_i_len + last_word_span[0]:
            i_line_start_i_len + last_word_span[1]]
        next_i_line_start_i_len = len(
            self._i_line_start_i(next_line, line_start))
        first_word_span = self._word_spans(next_line_extent_text)[0]
        first_word = next_line[
            next_i_line_start_i_len + first_word_span[0]:
            next_i_line_start_i_len + first_word_span[1]]

        # Compute the post-join spacing between last_word and first_word
        if not self._is_all_whitespace(line[-1]):
            keep_space = False
            space = self._space_between(last_word, first_word)
        else:
            # e.g. the user pressed space a few times at the end of the line,
            # then pressed backspace a few times.  Preserve the space that the
            # user entered at the end of the line.
            keep_space = True
            space = line[i_line_start_i_len + last_word_span[1]:]

        # Check whether we can fit first_word on this line
        width = self._width(
            u'{0:s}{1:s}{2:s}'.format(
                line[:i_line_start_i_len + last_word_span[1]], space,
                first_word))
        if width > self._wrap_width(section):
            return (None, None)

        # Compute the edit
        first_word_start_point = (
            next_line_region.begin() + next_i_line_start_i_len)
        replace_region = Region(line_region.end(), first_word_start_point)
        if keep_space:
            edit = (replace_region, '')
        else:
            edit = (replace_region, space)
        return (edit, line_region.end())

    def _try_backwards_join_edit(self, section, point, line_start):
        """Return a pair containing the edit for joining backwards, if any.

        Return a pair whose first element is the edit for joining the
        line containing "point" with the previous line, if we should do
        so.  If adding the first word on the current line to the
        previous line results in a line that is no longer than the wrap
        width, then we join the text on the two lines, assuming they are
        in the same paragraph and section.  This would be followed up
        with a split operation (as in _try_split_edit) if necessary to
        ensure that the current line is no longer than the wrap width.
        The second element of the return value is the recommended new
        point - the position of the former end of the previous line.
        This method returns (None, None) if we should not perform a join
        operation.

        dict<str, object> section - The current section, formatted like
            the elements of _sections.
        int point - The current position.
        str line_start - The line start.
        return tuple<tuple<Region, str>, int> - A pair consisting of the
            edit and the new position, respectively.
        """
        prev_line_region = self._prev_line_region(point)
        if prev_line_region is not None:
            return self._try_join_edit(
                section, prev_line_region.end(), line_start)
        else:
            return (None, None)

    def _find_section(self, point):
        """Compute the section containing the specified position, if any.

        Return a triple whose first element is the section containing
        the specified position, formatted like the elements of
        _sections, if any.  The second element is the line start, and
        the third element is the result of
        _should_erase_preceding_line_break.  (If the third element is
        True, then the section contains a position in the previous line
        instead of "point".)  If there are multiple matching sections
        and line starts, then we take the section that is earliest in
        _sections and the line start that is earliest in the section's
        'allowed_line_starts' entry.  Return (None, None, False) if
        there is no section containing "point".

        int point - The position.
        return tuple<dict<str, object>, str, bool> - The result.
        """
        # Compute information about the current line
        view = self._view
        line_region = view.line(point)
        line = view.substr(line_region)
        prev_char_scope = self._prev_char_scope(point, line_region)
        next_char_scope = view.scope_name(point)

        # Compute information about the previous line
        prev_line_region = self._prev_line_region(line_region.begin())
        if prev_line_region is None:
            prev_line = None
            prev_end_point_excluding_whitespace = None
            prev_line_prev_char_scope = None
            prev_line_next_char_scope = None
        else:
            prev_line = view.substr(prev_line_region)
            prev_end_point_excluding_whitespace = (
                self._end_point_excluding_whitespace(
                    prev_line, prev_line_region))
            prev_line_prev_char_scope = self._prev_char_scope(
                prev_line_region.end(), prev_line_region)
            prev_line_next_char_scope = view.scope_name(prev_line_region.end())

        # Find the first matching section
        for section in self._sections:
            for line_start in section['allowed_line_starts']:
                # We check _should_erase_preceding_line_break separately,
                # because it checks for the line start on the previous line
                # instead of the current line
                if (self._should_erase_preceding_line_break(
                        section, point, line_start, line, line_region,
                        prev_line, prev_line_region,
                        prev_end_point_excluding_whitespace,
                        prev_line_prev_char_scope, prev_line_next_char_scope)):
                    return (section, line_start, True)
                elif (self._section_indent(line, line_start) is not None and
                        self._matches_selector(
                            section, prev_char_scope, next_char_scope)):
                    return (section, line_start, False)
        return (None, None, False)

    def _gen_edits(self):
        """Coroutine for returning edits for word wrap fixup.

        _gen_edits() is a coroutine - a generator method that yields a
        sequence of edits to perform to fix word wrap, and requires each
        edit to be executed before control is returned to the generator.

        return Generator<tuple<Region, str>> - The edits.  Each edit is
            represented as a pair consisting of a Region and a string,
            and indicates that any text that is in the Region should be
            replaced with the given string.
        """
        # Only perform word wrap fixup if there is a single, empty selection
        # cursor.  The main reason for this is to simplify the implementation.
        # A secondary reason is to reduce the performance overhead of
        # WrapAsYouType.
        view = self._view
        selection = view.sel()
        if len(selection) != 1:
            return
        selected_region = selection[0]
        if not selected_region.empty():
            return

        self._update_settings()
        if not self._sections:
            return

        # Find the section that contains the selection cursor
        point = selected_region.begin()
        section, line_start, should_erase_preceding_line_break = (
            self._find_section(point))
        if section is None:
            return

        if should_erase_preceding_line_break:
            edit, point = self._erase_preceding_line_break_edit(point)
            if edit is not None:
                yield edit
        else:
            edit = self._try_remove_indent_of_next_line_edit(
                section, point, line_start)
            if edit is not None:
                yield edit

            edit, join_point = self._try_backwards_join_edit(
                section, point, line_start)
            if edit is not None:
                yield edit
                point = join_point

        # Keep splitting and joining until we reach a steady state
        while True:
            edit, split_point = self._try_split_edit(
                section, point, line_start)
            if edit is not None:
                yield edit
                point = split_point
            else:
                edit, join_point = self._try_join_edit(
                    section, point, line_start)
                if edit is not None:
                    yield edit
                    point = join_point
                else:
                    break

    @staticmethod
    def instance(view):
        """Return a WrapFixer for fixing word wrap in the specified View."""
        view_id = view.id()
        fixer = WrapFixer._instances.get(view_id)
        if fixer is None:
            fixer = WrapFixer(view)
            WrapFixer._instances[view_id] = fixer
        return fixer

    @staticmethod
    def clear_instance(view):
        """Erase any WrapFixer associated with the specified View.

        This allows the WrapFixer to be garbage collected.
        """
        WrapFixer._instances.pop(view.id(), None)

    def has_edit(self):
        """Return whether there is any word wrapping fixup to perform."""
        if self._edits_gen is None:
            self._edits_gen = self._gen_edits()
            try:
                self._first_edit = next(self._edits_gen)
            except StopIteration:
                self._first_edit = None
        return self._first_edit is not None

    def _perform_edit(self, edit, e):
        """Perform the specified edit.

        sublime.Edit edit - The Edit object to use for the edit.
        tuple<Region, str> e - The edit to perform.
        """
        # Compute selection_point
        view = self._view
        selection = view.sel()
        if len(selection) == 1 and selection[0].empty():
            selection_point = selection[0].begin()
        else:
            selection_point = None

        # Perform the edit
        replace_region, replacement_str = e
        if not replacement_str:
            view.erase(edit, replace_region)
        elif replace_region.empty():
            view.insert(edit, replace_region.begin(), replacement_str)
        else:
            view.replace(edit, replace_region, replacement_str)

        # Fix the selection cursor
        if replacement_str and selection_point == replace_region.begin():
            # We want the selection cursor to be right before the replacement
            # string, not right after
            selection.clear()
            selection.add(Region(selection_point, selection_point))

    def perform_edits(self, edit):
        """Perform word wrapping fixup.

        sublime.Edit edit - The Edit object to use for the operation.
        """
        if self.has_edit():
            edits_gen = self._edits_gen
            self._perform_edit(edit, self._first_edit)
            for e in edits_gen:
                self._perform_edit(edit, e)

    def on_modified(self):
        """Respond to a modification to the WrapFixer's View's content."""
        self._edits_gen = None
        self._first_edit = None
