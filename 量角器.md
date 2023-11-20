目前已经实现显示一个量角器的功能了，但是不能改变大小，不能改变颜色，不能旋转角度



## 技术路线

使用matplotlib绘制量角器，然后使用pyqt显示绘制成功的量角器。



问题1：matplotlib绘制的量角器上下有很多空白位置

<img src="https://pic.ntimg.cn/file/20191023/27644471_094450046083_2.jpg" alt="全圆量角器设计图__传统文化_文化艺术_设计图库_昵图网nipic.com" style="zoom:67%;" />

<img src="https://ts1.cn.mm.bing.net/th/id/R-C.16d00ca2663aaf37294daf3c1d3aaafe?rik=ejDcaHusu4f7AQ&riu=http%3a%2f%2fpic36.photophoto.cn%2f20150715%2f1190119101309622_b.jpg&ehk=hXZQuDO%2fa0xrivii3PEUeh2F3g7hdJZNmMVl%2blUO3Nc%3d&risl=&pid=ImgRaw&r=0" alt="量角器_量角器工具_微信公众号文章" style="zoom:67%;" />

figsize = 11 11

dpi = 144

pixel = 11*14  = 1584

```
scales_coll = [2, 1, 1, 1, 1]   -->  4 2 2 2  -->  0.002525, 0.0012626
path_effects=[withStroke(linewidth=12, foreground='white')]  12 --> 24 --> 0.01515
fontsize=40 24 18  --> 80 48 36 -->0.05050  0.03030  0.02727 
```

15 15 

2160 * 0.

