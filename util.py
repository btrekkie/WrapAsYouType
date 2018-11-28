import numbers
import re

import sublime


class Util(object):
    """Provides static utility methods."""

    # Equivalent value is contractual
    _WHITESPACE_REGEX = re.compile(r'\s*')

    @staticmethod
    def is_string(obj):
        """Return whether "obj" is a string.

        In Python 2, instances of str and unicode are regarded as
        strings.  In Python 3, only instances of str qualify.
        """
        # Taken from https://stackoverflow.com/a/33699705
        return isinstance(obj, (''.__class__, u''.__class__))

    @staticmethod
    def is_int(obj):
        """Return whether the specified object is an integer.

        Return whether the specified object is an integer (or long), but
        not a boolean.
        """
        return isinstance(obj, numbers.Integral) and not isinstance(obj, bool)

    @staticmethod
    def is_all_whitespace(str_):
        """Return whether the specified string consists only of whitespace."""
        match = Util._WHITESPACE_REGEX.match(str_)
        return match.span() == (0, len(str_))

    @staticmethod
    def status_message(window, message):
        """Temporarily show the specified string message in the status bar.

        Window window - The window in which to display the message, if
            the running version of Sublime Text allows us to limit the
            message to a single window.
        str message - The message to display.
        """
        if hasattr(window, 'status_message'):
            # Sublime 3
            window.status_message(message)
        else:
            # Sublime 2
            sublime.status_message(message)
