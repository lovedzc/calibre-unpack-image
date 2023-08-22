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

        self.setWindowTitle(_('解包图片 Unpack Image'))
        self.setWindowIcon(icon)

        self.l = QGridLayout()
        self.setLayout(self.l)

        self.image = QLabel()
        self.image.setPixmap(icon.pixmap(120, 120))

        self.unpack_image_button = QPushButton(_('解包图片\nUnpack Image'), self)
        self.unpack_image_button.clicked.connect(self.on_button_unpack_image)
        self.unpack_image_button.setDefault(True)
        self.unpack_image_button.setToolTip(_('<qt>Start the unpack image process</qt>'))

        self.unpack_path_textbox = QLineEdit(self)
        self.unpack_path_textbox.setText(prefs['path'])
        self.unpack_path_button = QPushButton(_('Select path'), self)
        self.unpack_path_button.clicked.connect(self.select_path)

        self.unpack_warning = QLabel(self)
        self.unpack_warning.setText('解包时会自动删除路径下的原有文件！\nThe original files in the path will be deleted automatically!')
        self.unpack_warning.setStyleSheet('color:red')

        self.l.addWidget(self.image, 1, 1, 4, 1, Qt.AlignVCenter)
        self.l.addWidget(self.unpack_image_button, 1, 2, 1, 1, Qt.AlignVCenter)
        self.l.addWidget(self.unpack_warning, 1, 3, 1, 2, Qt.AlignVCenter)
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
            if path != '':
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
                import traceback
                error_dialog(self.gui, _('Failed to magnify fonts'), _(
                    'Failed to magnify fonts, click "Show details" for more info'),
                    det_msg=traceback.format_exc(), show=True)

        MessageBox(MessageBox.INFO, _('OK'), _("Images are unpacked successfully.")).exec_()
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

        prefs['path'] = self.unpack_path_textbox.text()     # 输出路径，以路径框中的最终内容为准，这是为了处理用户手动修改路径框的内容
        
        import shutil
        import os
        import re

        title = re.sub('[\/:*?"<>|]','_',title)         # 替换非法字符
        authors = re.sub('[\/:*?"<>|]','_',authors)     # 替换非法字符

        newDir = f"{prefs['path']}/{title} - {authors}"
        if not os.path.exists(prefs['path']):
            os.mkdir(prefs['path'])
        elif os.path.exists(newDir):
            shutil.rmtree(newDir)   # 先删除原有的文件(目录)

        # 生成原始路径
        if fmt == 'azw3':       # 处理 azw3 格式
            oldDir = tdir + '/images'
            if DEBUG: print(_(f'[azw3] Moving images from \n {oldDir} \nto \n {newDir}'))
            shutil.move(oldDir, newDir)

        elif fmt == 'epub':     # 处理 epub 格式
            oldDir = tdir + '/OEBPS/Images'
            if not os.path.exists(oldDir):
                oldDir = tdir + '/Images'       # 有的eoub格式，图片不在/OEBPS/Images/，而是直接在/Images/

            if DEBUG: print(_(f'[epub] Moving images from \n {oldDir} \nto \n {newDir}'))
            shutil.move(oldDir, newDir)
            if os.path.exists(tdir+'/cover.jpeg'):
                shutil.move(tdir+'/cover.jpeg', newDir+'/00000.jpeg')

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
