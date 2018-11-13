import sys

import sublime_plugin

if sys.version_info[0] >= 3:
    from .wrap_fixer import WrapFixer
else:
    from wrap_fixer import WrapFixer


class WrapAsYouTypeCommand(sublime_plugin.TextCommand):
    """A command that performs word wrapping fixup.

    "Word wrapping fixup" consists of attempting to fix word wrapping in
    the vicinity of the selection cursor.
    """

    def run(self, edit):
        WrapFixer.instance(self.view).perform_edits(edit)
