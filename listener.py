import sys

import sublime_plugin

if sys.version_info[0] >= 3:
    from .wrap_fixer import WrapFixer
else:
    from wrap_fixer import WrapFixer


class WrapAsYouTypeListener(sublime_plugin.EventListener):
    """An EventListener for the WrapAsYouType plugin.

    WrapAsYouTypeListener listens for changes to views and runs the
    wrap_as_you_type command as appropriate.
    """

    # Private attributes:
    # bool _is_running: Whether on_modified is currently being called.

    def __init__(self):
        super(WrapAsYouTypeListener, self).__init__()
        self._is_running = False

    def on_modified(self, view):
        wrap_fixer = WrapFixer.instance(view)
        wrap_fixer.on_modified()

        if self._is_running:
            # Avoid recursively running a second wrap_as_you_type command
            # inside of an initial wrap_as_you_type command
            return
        self._is_running = True
        try:
            if (not view.settings().get('wrap_as_you_type_disabled') and
                    # Don't run the wrap_as_you_type command in response to an
                    # undo command (or a redo command other than redoing
                    # everything)
                    not view.command_history(1)[0]):

                last_command = view.command_history(0)[0]
                if (last_command not in ('swap_line_up', 'swap_line_down') and
                        # It is important to refrain from running the
                        # wrap_as_you_type command if there is no word wrap
                        # fixup to perform.  Otherwise, Sublime creates an undo
                        # entry for every single keystroke.
                        wrap_fixer.has_edit()):
                    view.run_command('wrap_as_you_type')
            wrap_fixer.on_post_modification()
        finally:
            self._is_running = False

    def on_selection_modified(self, view):
        WrapFixer.instance(view).on_selection_modified()

    def on_close(self, view):
        WrapFixer.clear_instance(view)
