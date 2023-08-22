from calibre.customize import InterfaceActionBase

class UnpackImagePlugin(InterfaceActionBase):
    name                    = _('Convert to pdf')
    description             = _('Convert fixed azw3/epub to pdf')
    supported_platforms     = ['linux', 'windows']
    author                  = 'DZC'
    version                 = (0, 4, 1)
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
