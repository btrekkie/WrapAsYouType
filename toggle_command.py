import sys

import sublime_plugin

if sys.version_info[0] >= 3:
    from .util import Util
else:
    from util import Util


class ToggleWrapAsYouTypeCommand(sublime_plugin.TextCommand):
    """A command that toggles WrapAsYouType.

    A command that inverts the "wrap_as_you_type_disabled" setting in
    the current tab.  This toggles whether WrapAsYouType operates in the
    current tab.
    """

    def run(self, edit):
        view = self.view
        settings = view.settings()
        if settings.get('wrap_as_you_type_disabled'):
            settings.erase('wrap_as_you_type_disabled')
            Util.status_message(view.window(), 'WrapAsYouType enabled')
        else:
            settings.set('wrap_as_you_type_disabled', True)
            Util.status_message(view.window(), 'WrapAsYouType disabled')
