from __future__ import (unicode_literals, division, absolute_import, print_function)

__license__   = 'GPL v3'
__copyright__ = '2013, 2014, 2017, Jellby <jellby@yahoo.com>'
__docformat__ = 'restructuredtext en'

from calibre.gui2.actions import InterfaceAction
from calibre_plugins.unpack_image.main import UnpackImageDialog

load_translations()

class InterfacePlugin(InterfaceAction):

    name = _('unpack image')
    action_spec = (_('unpack image'), None, _('Run the Unpack Image Plugin'), (None))

    def genesis(self):
        icon = get_icons('images/icon.png')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        try:
          self.d.show()
        except:
          self.d = UnpackImageDialog(self.gui, self.qaction.icon(), do_user_config)
          self.d.show()

    def apply_settings(self):
        from calibre_plugins.prince_pdf.config import prefs
        prefs
