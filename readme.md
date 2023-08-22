这是为了把纯图片的AZW3（也就是固定Layout的Kindle书）转成高质量的PDF而写的插件。
基本思路是，把AZW3中的图片无损拆解出来，然后用PIL的Image库转成PDF。
本插件支持批量拆解。

目前已知的问题：
1. 只支持AZW3和EPUB，不支持其他格式
2. PIL的Image库会对图像做处理，导致PDF文件尺寸变大
3. "Unpack image"这个名字有点名不副实了…
4. 尚未实现PDF文件自动加入calibre库

顺便记录下 calibre 的调试方法：
calibre-customize -b "D:\Github\calibre-unpack-image"
calibre-debug -g

再记录下设置代理的方法：
首先开启 privoxy
然后设置环境变量
http_proxy = http://127.0.0.1:8118
https_proxy=http://127.0.0.1:8118

-----------------------

This is a plug-in written to convert pure image AZW3 (that is, fixed Layout Kindle books) into high-quality PDF.
The basic idea is to lossless disassemble the images in AZW3, and then use PIL's Image library to PDF.
This plug-in supports batch disassembly.

Currently known issues:
1. only supports AZW3 and EPUB, does not support other formats
2. PIL's Image library will do image processing, resulting in larger PDF file size
3. "Unpack image" is a bit of a misnomer...

Translated with www.DeepL.com/Translator (free version)
