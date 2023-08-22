为了把纯图片的AZW3（也就是固定Layout的Kindle书）转成高质量的PDF而写的插件。
基本思路是，把AZW3中的图片无损拆解出来，然后手动调用老马的 FreePic2PDF 转成PDF。
本插件实现的功能就是把图片拆到指定目录下，并以"title - author"的形式命名目录。
本插件支持批量拆解。

PS: 老马的 FreePic2PDF 请在下述网站下载：
    https://www.cnblogs.com/stronghorse/

目前已知的问题：
1. AZW3文件解压的图片，会多出一张低分辨率的封面
2. 只支持AZW3和EPUB，不支持其他格式

顺便记录下 calibre 的调试方法：
calibre-customize -b "D:\Github\calibre-unpack-image"
calibre-debug -g

再记录下设置代理的方法：
首先开启 privoxy
然后设置环境变量
http_proxy = http://127.0.0.1:8118
https_proxy=http://127.0.0.1:8118

-----------------------

In order to pure picture AZW3 (that is, fixed Layout of the Kindle book) into a high-quality PDF and write a plug-in.
The basic idea is to break down the images in AZW3 losslessly, and then manually call the old horse's FreePic2PDF to PDF.
The function of this plug-in is to disassemble the picture to the specified directory, and "title - author" in the form of a named directory.
This plugin supports batch disassembly.

PS: Please download Old Ma's FreePic2PDF from the following website:
    https://www.cnblogs.com/stronghorse/

Currently known problems:
1. AZW3 file decompression of images, there will be an additional low-resolution cover.
2. only supports AZW3 and EPUB, does not support other formats.

Translated with www.DeepL.com/Translator (free version)