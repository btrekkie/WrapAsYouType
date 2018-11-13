import sys

import sublime

if sys.version_info[0] >= 3:
    from .lru_cache import lru_cache
    from .util import Util
else:
    from lru_cache import lru_cache
    from util import Util


class Section(object):
    """A section type in the "wrap_as_you_type_sections" setting.

    A section type - a Python object representation of an element in the
    "wrap_as_you_type_sections" setting.  See README.md.

    Public attributes:

    list<str> allowed_line_starts - A non-empty list of the allowed line
        starts.
    int wrap_width - The wrap width associated with this section, if
        any.
    """

    # Private attributes:
    # object _combining_selector_rules - The "combining_selector_rules" entry,
    #     if any.
    # object _selector_rules - The "selector_rules" entry.

    def __init__(
            self, wrap_width, allowed_line_starts, selector_rules,
            combining_selector_rules):
        self.wrap_width = wrap_width
        self.allowed_line_starts = allowed_line_starts
        self._selector_rules = selector_rules
        self._combining_selector_rules = combining_selector_rules

    def _matches_selector_rules(self, scope, rules):
        """Return whether the specified scope matches the specified rule set.

        str scope - The scope.  This is a space-delimited sequence of
            scope names.
        object rules - The selector rule set.
        return bool - Whether there is a match.
        """
        if Util.is_string(rules):
            return sublime.score_selector(scope, rules) > 0
        elif isinstance(rules, dict):
            key, value = list(rules.items())[0]
            if key == 'and':
                for sub_rules in value:
                    if not self._matches_selector_rules(scope, sub_rules):
                        return False
                return True
            elif key == 'or':
                return self._matches_selector_rules(scope, value)
            elif key == 'not':
                return not self._matches_selector_rules(scope, value)
        else:
            for sub_rules in rules:
                if self._matches_selector_rules(scope, sub_rules):
                    return True
            return False

    @lru_cache(20)
    def _matches_selector_rules_cached(self, scope, is_combining):
        """Equivalent implementation is contractual."""
        if is_combining:
            return self._matches_selector_rules(
                scope, self._combining_selector_rules)
        else:
            return self._matches_selector_rules(scope, self._selector_rules)

    def matches_selector_rules(self, scope):
        """Equivalent implementation is contractual."""
        return self._matches_selector_rules_cached(scope, False)

    def matches_combining_selector_rules(self, scope):
        """Equivalent implementation is contractual."""
        if self._combining_selector_rules is not None:
            return self._matches_selector_rules_cached(scope, True)
        else:
            return False
