try:
    from PyQt5.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy, QFileDialog,QLineEdit
except ImportError:
    from PyQt4.Qt import Qt, QDialog, QPushButton, QLabel, QDialogButtonBox, QGridLayout, QSizePolicy, QFileDialog,QLineEdit

import os
import shutil
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

        self.setWindowTitle(_('Convert fixed azw3/epub to pdf'))
        self.setWindowIcon(icon)

        self.l = QGridLayout()
        self.setLayout(self.l)

        self.image = QLabel()
        self.image.setPixmap(icon.pixmap(120, 120))

        self.unpack_image_button = QPushButton(_('转换成PDF\nConvert to pdf'), self)
        self.unpack_image_button.clicked.connect(self.on_button_unpack_image)
        self.unpack_image_button.setDefault(True)
        self.unpack_image_button.setToolTip(_('<qt>Start the unpack image process</qt>'))

        self.unpack_path_textbox = QLineEdit(self)
        self.unpack_path_textbox.setText(prefs['path'])
        self.unpack_path_button = QPushButton(_('Select path'), self)
        self.unpack_path_button.clicked.connect(self.select_path)

        self.unpack_warning = QLabel(self)
        # self.unpack_warning.setText('解包时会自动删除路径下的原有文件！\nThe original files in the path will be deleted automatically!')
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
        # newDir = f"{prefs['path']}/{title}"
        if not os.path.exists(prefs['path']):
            os.mkdir(prefs['path'])
        elif os.path.exists(newDir):
            shutil.rmtree(newDir)   # 先删除原有的文件(目录)

        # 生成原始路径
        if fmt == 'azw3':       # 处理 azw3 格式
            oldDir = tdir + '/images'
            # shutil.move(oldDir, newDir)       # 直接从temp目录生成PDF，因而这个移动操作就不要了

        elif fmt == 'epub':     # 处理 epub 格式
            oldDir = tdir + '/newImages'
            process_epub(tdir, oldDir)

            # 改成 根据html文件内容 修改图片，而不是直接复制文件夹
            # oldDir = tdir + '/OEBPS/Images'
            # if not os.path.exists(oldDir):
            #     oldDir = tdir + '/Images'       # 有的eoub格式，图片不在/OEBPS/Images/，而是直接在/Images/

            # if os.path.exists(tdir+'/cover.jpeg'):
            #     shutil.move(tdir+'/cover.jpeg', tdir+'/00000.jpeg')

            # # shutil.move(oldDir, newDir)       # 直接从temp目录生成PDF，因而这个移动操作就不要了
            # # if os.path.exists(tdir+'/cover.jpeg'):
            # #     shutil.move(tdir+'/cover.jpeg', newDir+'/00000.jpeg')

        if DEBUG: print(_(f'[epub] Moving images from \n {oldDir} \nto \n {newDir}'))

        # 将图片转成PDF
        convert_to_PDF(oldDir, newDir)

        return


    ###########################################################
    # 将图片转成PDF
    ###########################################################
    def convert_to_PDF(dir, pdfFilepath):

        from PIL import Image

        imagelist = os.listdir(dir)
        images = []
        for f in imagelist:
            filepath = f'{dir}/{f}'
            if os.path.getsize(filepath) >= 20000:
                images.append(Image.open(filepath)) # 打开图片文件

        images[0].save(pdfFilepath+'.PDF', "PDF" , quality=95, append_images=images[1:], subsampling=0,  save_all=True, title=title, author=authors, optimize=True)
        shutil.rmtree(dir)   # 删除TEMP图片目录


    ###########################################################
    # 处理epub文件
    # 1. 找到content.opf文件，解析<manifest>标签，获取所有内容文件的路径，并按顺序记下来，记录顺序号（index）。
    # 2. 根据获取到的每个文件，寻找该文件中的img标签，获取图片文件的路径。
    # 3. 根据获取到的图片文件路径，将该图片保存到newdir，同时将图片文件改为顺序号（index）。
    ###########################################################
    def process_epub(epubDir, newImageDir):
        from xml.etree import ElementTree as ET
        from bs4 import BeautifulSoup

        # 创建新目录
        os.makedirs(newImageDir, exist_ok=True)

        # 查找content.opf文件
        content_opf_path = None
        for root, dirs, files in os.walk(epubDir):
            if 'content.opf' in files:
                content_opf_path = os.path.join(root, 'content.opf')
                break

        if not content_opf_path:
            print("content.opf文件未找到")
            return

        # 解析content.opf文件
        tree = ET.parse(content_opf_path)
        root = tree.getroot()

        # 获取manifest标签
        manifest = root.find('.//{http://www.idpf.org/2007/opf}manifest')
        if manifest is None:
            print("manifest标签未找到")
            return

        # 获取所有内容文件的路径，并按顺序记录下来
        content_files = []
        for item in manifest.findall('{http://www.idpf.org/2007/opf}item'):
            href = item.get('href')
            if href.endswith('.xhtml') or href.endswith('.html'):
                content_files.append(href)

        # 处理每个内容文件
        for index, content_file in enumerate(content_files):
            content_file_path = os.path.join(os.path.dirname(content_opf_path), content_file)
            if not os.path.exists(content_file_path):
                print(f"内容文件{content_file}未找到")
                continue

            # 解析HTML文件
            with open(content_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            img_tags = soup.find_all('img')

            # 获取图片文件的路径
            for img_tag in img_tags:
                img_src = img_tag.get('src')
                if not img_src:
                    continue

                # 处理相对路径
                img_path = os.path.join(os.path.dirname(content_file_path), img_src)
                if not os.path.exists(img_path):
                    print(f"图片文件{img_src}未找到")
                    continue

                # 保存图片到新目录
                img_filename = f"{index}.png"  # 将图片文件名改为顺序号
                new_img_path = os.path.join(newImageDir, img_filename)
                shutil.copy(img_path, new_img_path)
                print(f"图片已保存到{new_img_path}")
                
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
