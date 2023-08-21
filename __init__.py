from calibre.customize import InterfaceActionBase

class UnpackImagePlugin(InterfaceActionBase):
    name                    = _('Unpack Image')
    description             = _('Unpack Image')
    supported_platforms     = ['linux', 'windows']
    author                  = 'Ding Zicheng'
    version                 = (0, 2, 7)
    minimum_calibre_version = (2, 72, 0)
    actual_plugin           = 'calibre_plugins.unpack_image.ui:InterfacePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.unpack_image.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
