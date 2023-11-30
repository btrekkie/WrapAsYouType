import functools
import re
import sys

if sys.version_info[0] >= 3:
    from .error import UserFacingError
    from .util import Util
else:
    from error import UserFacingError
    from util import Util


# dict<str, (SettingsParser) -> void> - A map from each wrap_as_you_type_*
#     setting to the SettingsParser method that responds to changes in that
#     setting.
_update_settings_funcs = {}


def _update_setting_method(setting):
    """Decorator that wraps a SettingsParser update settings method.

    Decorator that wraps a SettingsParser method that responds to a
    change in one of the wrap_as_you_type_* settings.  The wrapper
    automatically catches and displays any UserFacingErrors raised in
    the wrapped function, and provides other functionality.

    str setting - The name of the wrap_as_you_type_* setting, e.g.
        'wrap_as_you_type_sections'.
    """
    def wrapper(func):
        def inner_wrapper(self):
            try:
                func(self)
            except UserFacingError as exception:
                print(
                    u'WrapAsYouType error: error in "{0:s}" setting: '
                    '{1:s}'.format(setting, str(exception)))
                Util.status_message(
                    self._view.window(),
                    'WrapAsYouType settings error; see console')

            for listener in self._listeners.get(setting, []):
                listener()
        _update_settings_funcs[setting] = inner_wrapper
        return inner_wrapper
    return wrapper


class SettingsParser(object):
    """Parses all of the wrap_as_you_type_* settings for a given View.

    In the context of SettingsParser, the term "parse" refers to
    validating a setting and presenting it in a format that is useful to
    us.  Whenever a wrap_as_you_type_* setting changes, SettingsParser
    updates the value of the corresponding field.

    Public attributes:

    bool is_disabled - The result of coercing the
        "wrap_as_you_type_disabled" setting to a boolean.
    bool is_passive - The "wrap_as_you_type_passive" setting.  This is
        False if the value of "wrap_as_you_type_passive" is invalid.
    list<dict<str, object>> paragraphs - Equivalent to the
        "wrap_as_you_type_paragraphs" setting, but with the
        "first_line_regex" entries replaced with re.Patterns instead of
        strings (the result of calling re.compile on the entries), with
        default values filled in for the "single_line" entries, and with
        missing "indent", "indent_levels", and "indent_group" entries
        replaced with None.  This is [] if the value of
        "wrap_as_you_type_paragraphs" is invalid.
    list<dict<str, object>> sections - Equivalent to the
        "wrap_as_you_type_sections" setting, but with any "line_start"
        entries replaced with single-element "allowed_line_starts"
        entries, and with missing "wrap_width" and "combining_selector"
        entries replaced with None.  This is [] if the value of
        "wrap_as_you_type_sections" is invalid.
    list<dict<str, object>> space_between_words - Equivalent to the
        "wrap_as_you_type_space_between_words" setting, but with the
        "first_word_regex" and "second_word_regex" entries replaced with
        re.Patterns instead of strings (the result of calling re.compile
        on the entries), and with missing "first_word_regex" and
        "second_word_regex" entries replaced with None.  This is [] if
        the value of "wrap_as_you_type_space_between_words" is invalid.
    re.Pattern word_regex - The value re.compile(word_regex_setting),
        where "word_regex_setting" is the value of the
        "wrap_as_you_type_word_regex" setting.  This is
        DEFAULT_WORD_REGEX if the value of "wrap_as_you_type_word_regex"
        is invalid.
    """

    # Private attributes:
    # dict<str, list<() -> void>> _listeners - A map from wrap_as_you_type_*
    #     settings to the corresponding listeners, as added using
    #     add_on_change.  Settings without any listeners might not have entries
    #     in the map.
    # View _view - The View whose settings we are parsing.

    # The default value for word_regex
    DEFAULT_WORD_REGEX = re.compile(r'[\S\xa0]+')

    def __init__(self, view):
        self._view = view
        self._listeners = {}

        # Register and run update methods
        settings = view.settings()
        for setting, func in _update_settings_funcs.items():
            settings.add_on_change(setting, functools.partial(func, self))
            func(self)

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

    @_update_setting_method('wrap_as_you_type_sections')
    def _update_sections(self):
        """Update the value of self.sections."""
        section_setting = self._view.settings().get(
            'wrap_as_you_type_sections')
        self.sections = []
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
        self.sections = sections

    @_update_setting_method('wrap_as_you_type_word_regex')
    def _update_word_regex(self):
        """Update the value of word_regex."""
        word_regex_setting = self._view.settings().get(
            'wrap_as_you_type_word_regex')
        self.word_regex = SettingsParser.DEFAULT_WORD_REGEX
        if word_regex_setting is not None:
            self.word_regex = self._validate_and_compile_regex(
                word_regex_setting)

    @_update_setting_method('wrap_as_you_type_space_between_words')
    def _update_space_between_words(self):
        """Update the value of space_between_words."""
        space_between_words_setting = self._view.settings().get(
            'wrap_as_you_type_space_between_words')
        self.space_between_words = []
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
            if not Util.is_all_whitespace(space):
                raise UserFacingError(
                    '"space" entry must consist exclusively of whitespace')

            space_between_words.append({
                'first_word_regex': first_word_regex,
                'second_word_regex': second_word_regex,
                'space': space,
            })
        self.space_between_words = space_between_words

    @_update_setting_method('wrap_as_you_type_paragraphs')
    def _update_paragraphs(self):
        """Update the value of self.paragraphs."""
        paragraphs_setting = self._view.settings().get(
            'wrap_as_you_type_paragraphs')
        self.paragraphs = []
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

            indent = paragraph.get('indent', None)
            if 'indent' in paragraph:
                if not Util.is_string(indent):
                    raise UserFacingError('"indent" entry must be a string')
                if not Util.is_all_whitespace(indent):
                    raise UserFacingError(
                        '"indent" entry must consist exclusively of '
                        'whitespace')

            indent_levels = paragraph.get('indent_levels', None)
            if 'indent_levels' in paragraph:
                if not Util.is_int(indent_levels) or indent_levels < 0:
                    raise UserFacingError(
                        '"indent_levels" entry must be a nonnegative integer')
                if indent is not None:
                    raise UserFacingError(
                        '"indent" and "indent_levels" entries may not both be '
                        'present')

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
                    ('indent' in paragraph or 'indent_levels' in paragraph or
                        indent_group is not None)):
                raise UserFacingError(
                    'If "single_line" is true, then the "indent_levels", '
                    '"indent", and "indent_group" entries may not be present')

            paragraphs.append({
                'first_line_regex': first_line_regex,
                'indent': indent,
                'indent_group': indent_group,
                'indent_levels': indent_levels,
                'single_line': single_line,
            })
        self.paragraphs = paragraphs

    @_update_setting_method('wrap_as_you_type_passive')
    def _update_is_passive(self):
        """Update the value of self.is_passive."""
        passive_setting = self._view.settings().get('wrap_as_you_type_passive')
        if passive_setting in (None, False, True):
            self.is_passive = bool(passive_setting)
        else:
            self.is_passive = False
            raise UserFacingError('The value must be a boolean')

    @_update_setting_method('wrap_as_you_type_disabled')
    def _update_is_disabled(self):
        """Update the value of is_disabled."""
        self.is_disabled = bool(
            self._view.settings().get('wrap_as_you_type_disabled'))

    def add_on_change(self, setting, func):
        """Add a listener to changes in the specified setting.

        Add a listener to changes in the specified wrap_as_you_type_*
        setting.  This is equivalent to
        view.settings().add_on_change(setting, func), where "view" is
        the value that was passed to the constructor, except that the
        listener function is guaranteed to be called after the relevant
        SettingsParser field is updated.

        str setting - The name of the setting, e.g.
            'wrap_as_you_type_sections'.  This must be a valid
            wrap_as_you_type_* setting.
        () -> void func - The function to call when the setting is
            changed.
        """
        self._listeners.setdefault(setting, []).append(func)

    def clear_on_change(self):
        """Remove all listeners to changes in wrap_as_you_type_* settings.

        Remove all functions listening to changes in wrap_as_you_type_*
        settings.  This removes not only the listeners registered using
        calls to self.add_on_change, but also any listeners that
        SettingsParser uses internally.  After calling
        clear_on_change(), the SettingsParser's fields will no longer
        reflect any changes in the settings.
        """
        settings = self._view.settings()
        for setting in _update_settings_funcs.keys():
            settings.clear_on_change(setting)
        self._listeners = {}
