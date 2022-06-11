try:
    from PyQt5.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy, QFileDialog,QLineEdit
except ImportError:
    from PyQt4.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy, QFileDialog,QLineEdit

from calibre.utils.config import JSONConfig

prefs = JSONConfig('plugins/unpack_image')
prefs.defaults['path'] = 'C:\\TEMP'

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

        self.unpack_image_button = QPushButton(_('Unpack Image'), self)
        self.unpack_image_button.clicked.connect(self.on_button_unpack_image)
        self.unpack_image_button.setDefault(True)
        self.unpack_image_button.setToolTip(_('<qt>Start the unpack image process</qt>'))

        self.unpack_path_textbox = QLineEdit(self)
        self.unpack_path_textbox.setText(prefs['path'])
        self.unpack_path_button = QPushButton(_('Dir'), self)
        self.unpack_path_button.clicked.connect(self.select_path)

        self.l.addWidget(self.image, 1, 1, 4, 1, Qt.AlignVCenter)
        self.l.addWidget(self.unpack_image_button, 1, 2, 1, 1, Qt.AlignVCenter)
        self.l.addWidget(self.unpack_path_textbox, 3, 2, 1, 2, Qt.AlignVCenter)
        self.l.addWidget(self.unpack_path_button, 3, 4, Qt.AlignVCenter)

        self.l.setColumnStretch(1, 1)
        self.l.setColumnStretch(2, 1)
        self.l.setColumnStretch(3, 10)
        self.l.setColumnStretch(4, 1)
        self.l.setColumnMinimumWidth(3, 200)
        self.adjustSize()

        # Update the info now and every time the selection or the data changes
        self.gui.library_view.model().dataChanged.connect(self.update_info)
        self.gui.library_view.selectionModel().selectionChanged.connect(self.update_info)
        self.update_info()

    def select_path(self):
            path = QFileDialog.getExistingDirectory(None,"Select unpack dir", self.unpack_path_textbox.text())  # 起始路径
            self.unpack_path_textbox.setText(path)
            prefs['path'] = path 

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
            authors = mi.get('authors')
            if DEBUG: print('authors = ' + authors[0])     #TEST

            fmts = self.db.formats(book_id, index_is_id=True)
            fmts = fmts.lower().split(',')

            if not list(set(['azw3','epub']) & set(fmts)):
                return error_dialog(self.gui, 'Cannot unpack','No azw3/epub format', show=True)

            try:
                self.unpack_image(book_id, title, authors[0], fmts[0])
                print("Unpacked : " + title)
            except:
                print('')
                print('--- ERROR --- ' + title)
                MessageBox(MessageBox.INFO, _('Error'), title).exec_()

        MessageBox(MessageBox.INFO, _('OK'), _("It's all settled!")).exec_()
        return

    def unpack_image(self, book_id, title, authors, fmt):
        from calibre.constants import DEBUG
        from calibre.ptempfile import PersistentTemporaryDirectory
        from calibre.ebooks.tweak import get_tools
        # from calibre.ebooks.oeb.base import OEBBook
        # from calibre.ebooks.oeb.reader import OEBReader
        # from calibre.utils.logging import default_log
        # from calibre_plugins.prince_pdf.dummy_preprocessor import dummy_preprocessor

        book_file = self.db.format(book_id, fmt, index_is_id=True, as_path=True)
        tdir = PersistentTemporaryDirectory('_unpack')
        if DEBUG: print(_(f'Unpacking book to {tdir}...'))
        exploder = get_tools(fmt)[0]
        if (exploder == None): return (None, None)
        opf = exploder(book_file, tdir)
        
        import shutil
        import os
        # 生成目的路径
        newDir = f'D:/TEST/{title} - {authors}'
        # 生成原始路径
        if fmt == 'azw3':
            oldDir = tdir + '/images'
        elif fmt == 'epub':
            oldDir = tdir + '/OEBPS/Images'
            if not os.path.exists(oldDir):
                oldDir = tdir + '/Images'       # 有的eoub格式，图片不在/OEBPS/Images/，而是直接在/Images/
                shutil.move(oldDir, newDir)
                shutil.move(tdir+'/cover.jpeg', newDir+'/00000.jpeg')   # 并且此时封面图固定为/cover.jpeg
                return   # 这种epub格式，在本分支内全部处理完成，因而退出

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
