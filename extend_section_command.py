import sys

import sublime_plugin

if sys.version_info[0] >= 3:
    from .wrap_fixer import WrapFixer
else:
    from wrap_fixer import WrapFixer


class WrapAsYouTypeExtendSectionCommand(sublime_plugin.TextCommand):
    """A command that inserts a newline and the current section's line start.

    If the beginning of the selection cursor is in a wrappable section
    that extends to the beginning of the line, this inserts a newline
    and the section's line start string, along with the appropriate
    indentation. Otherwise, the command just inserts a newline followed
    by the appropriate indentation.
    """

    def run(self, edit):
        wrap_fixer = WrapFixer.instance(self.view)
        wrap_fixer.extend_section(edit)
