为了把纯图片的AZW3（也就是固定Layout的Kindle书）转成高质量的PDF而写的插件。
基本思路是，把AZW3中的图片无损拆解出来，然后手动调用老马的 FreePic2PDF 转成PDF。
本插件实现的功能就是把图片拆到指定目录下，并按照 title 字段命名各目录。
支持批量拆解。

PS: 老马的 FreePic2PDF 请自行下载运行。

目前已知的问题：
1. 某些AZW3文件的封面图片文件名序号会排在最后
2. 某些拆出来的图片中，最后一张总是低分辨率的封面图
3. 只支持AZW3和EPUB，不支持其他格式
4. title中包含非法字符如“: ? *”等时，处理会中断

顺便记录下 calibre 的调试方法：
calibre-customize -b "D:\Github\calibre-unpack-image"
calibre-debug -g

再记录下设置代理的方法：
首先开启 privoxy
然后设置环境变量
http_proxy = http://127.0.0.1:8118
https_proxy=http://127.0.0.1:8118

-----------------------

In order to pure images of AZW3 (that is, fixed Layout of the Kindle book) into a high-quality PDF and write the plug-in.
The basic idea is that the pictures in AZW3 losslessly disassembled, and then manually call the old horse FreePic2PDF to convert to PDF.
This plug-in to achieve the function is to split the picture to the specified directory, and in accordance with the title field named each directory.
Support batch disassembly.

Currently known issues.
1. some AZW3 files have the cover image file name serial number at the end
2. the last image in some disassembled images is always the low-resolution cover image
3. only AZW3 and EPUB are supported, other formats are not supported
4. The title contains illegal characters such as ": ? *" etc., the processing will be interrupted.


Translated with www.DeepL.com/Translator (free version)