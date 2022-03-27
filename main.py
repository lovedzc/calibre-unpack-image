try:
    from PyQt5.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy
except ImportError:
    from PyQt4.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy

# Main dialog of the plugin
class UnpackImageDialog(QDialog):

    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.icon = icon
        self.gui = gui
        self.do_user_config = do_user_config

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle(_('Unpack Image'))
        self.setWindowIcon(icon)

        self.l = QGridLayout()
        self.setLayout(self.l)

        self.image = QLabel()
        self.image.setPixmap(icon.pixmap(120, 120))
        self.l.addWidget(self.image, 1, 1, 4, 1, Qt.AlignVCenter)

        self.unpack_image_button = QPushButton(_('Unpack Image'), self)
        self.unpack_image_button.clicked.connect(self.on_button_unpack_image)
        self.unpack_image_button.setDefault(True)
        self.unpack_image_button.setToolTip(_('<qt>Start the unpack image process</qt>'))
        self.l.addWidget(self.unpack_image_button, 1, 2, Qt.AlignVCenter)

        self.l.setColumnStretch(1, 1)
        self.l.setColumnStretch(2, 10)
        self.l.setRowStretch(1, 1)
        self.l.setRowStretch(2, 1)
        self.l.setRowStretch(3, 10)
        self.l.setRowStretch(4, 1)
        self.l.setRowStretch(5, 1)
        self.l.setRowStretch(6, 1)
        self.l.setRowMinimumHeight(1, 1)
        self.l.setRowMinimumHeight(2, 1)
        self.l.setRowMinimumHeight(3, 1)
        self.l.setRowMinimumHeight(4, 1)
        self.l.setRowMinimumHeight(5, 1)
        self.l.setRowMinimumHeight(6, 1)

        self.adjustSize()

        # Update the info now and every time the selection or the data changes
        self.gui.library_view.model().dataChanged.connect(self.update_info)
        self.gui.library_view.selectionModel().selectionChanged.connect(self.update_info)
        self.update_info()

    def on_button_unpack_image(self):
        from calibre.gui2 import error_dialog
        from calibre.constants import DEBUG
        from calibre.gui2.dialogs.message_box import MessageBox

        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            return error_dialog(self.gui, 'Cannot update metadata','No books selected', show=True)

        # Map the rows to book ids
        ids = list(map(self.gui.library_view.model().id, rows))
        if DEBUG: print(ids)	#TEST
        db = self.db.new_api
        for book_id in ids:
            mi = self.db.get_metadata(book_id, index_is_id=True, get_cover=False)
            title = mi.get('title')
            if DEBUG: print('title = ' + title)     #TEST

            fmts = self.db.formats(book_id, index_is_id=True)
            fmts = fmts.lower().split(',')

            if 'azw3' not in fmts: 
                return error_dialog(self.gui, 'Cannot unpack','No azw3 format', show=True)

            self.unpack_image(book_id, title, 'azw3')

        MessageBox(MessageBox.INFO, _('搞定'), _("图片拆在 D:/TEST/ ")).exec_()
        return

    def unpack_image(self, book_id, title, fmt):
        from calibre.constants import DEBUG
        from calibre.ptempfile import PersistentTemporaryDirectory
        from calibre.ebooks.tweak import get_tools
        # from calibre.ebooks.oeb.base import OEBBook
        # from calibre.ebooks.oeb.reader import OEBReader
        # from calibre.utils.logging import default_log
        # from calibre_plugins.prince_pdf.dummy_preprocessor import dummy_preprocessor

        book_file = self.db.format(book_id, fmt, index_is_id=True, as_path=True)
        if DEBUG: print(_('Unpacking book...'))
        tdir = PersistentTemporaryDirectory('_unpack')
        exploder = get_tools(fmt)[0]
        if (exploder == None): return (None, None)
        opf = exploder(book_file, tdir)
        
        import shutil
        oldDir = tdir + '/images'
        newDir = f'D:/TEST/{title}'
        shutil.move(oldDir, newDir)
		
        return


    def update_info(self):
        self.db = self.gui.current_db
        # Get selected rows
        rows = self.gui.library_view.selectionModel().selectedRows()
        if not rows or len(rows) == 0:
            self.info.setText(_('<b>No books selected</b>'))
            self.info.setAlignment(Qt.AlignCenter)
            self.suggestion.setText(_('Select one single book'))
            self.selected = None
            self.convert_to_PDF_button.setEnabled(False)
