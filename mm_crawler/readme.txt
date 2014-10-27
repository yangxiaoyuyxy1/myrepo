本程序编写调试的python版本为: python 3.3.0
环境为: windows 7
需要安装的第三方库: beautifulsoap(解析网页并提取新url和图片)

代码文件:
WebFetch.py: 网页抓取及相关标签提取类
mylog.py: 日志类
DomainSuffix.py :域名后缀解析加载类
domain_suffixes.txt : 存储提取顶级域名时的域名后缀范围。
mm_crawler_log.log : 程序运行过程中生成的日志文件

实现思路:

1.关键数据结构:
url_queue: 待抓取的url队列，固定大小。
url_dict:  全局url去重字典,兼判断url是否已经被抓取。
img_url_dict: 全局图片url去重字典,兼判断图片是否已经被下载。
crawl_thread函数功能:网页抓取解析，获取新网页url和获取图片链接并下载图片。
get_url_thread函数功能: 每隔一定周期从url_dict中获取未抓取的url放入url_queue中。

2.crawl_thread线程的工作流程:
    网页抓取线程crawl_thread每一次从url_queue中取得本次待抓取的一个url,抓取完网页之后,解析当前html并将新获取到的url通过url_dict的get方法判断url是否存在来去重,不存在的直接存入url_dict,并设置其对应的value,url_dict的key为url,value为0表示当前url未抓取，value为1表示url已经抓取(外链和一些非网页url直接设置为1)。当前从队列中获取的url对应的value要被设置为1,表示已经抓取过。
    当前网页url抓取并解析完成之后，开始解析网页并获取图片，将图片链接依次解析并去重后，开始下载未重复的图片。

3.多个crawl_thread线程的工作流程:
    每个线程互斥地从url_queue中获取待抓取的url,获取到待抓取url后，后续处理流程一样。各个线程对url_dict的操作和对图片的下载都是互斥的。

4.get_url_thread获取未抓取url线程工作流程:
    get_url_thread线程每隔固定的时间遍历url_dict，将对应于value为0的未抓取url放进url_queue中，如此循环,当超过一个较长的时间都没有找到新的url时，表示本站抓取完成。

5.外链判断:
   提取当前url的顶级域名和初始设置的url的顶级域名进行比对，不相等则为外链，图片链接未判断，外链在url_dict中直接设置为1,后续不抓取.

6.其它非html文本网页的链接判断:
   诸如视频avi,pdf等链接通过url后缀匹配进行简单判断，并在url_dict中直接设置为1,后续不抓取.

7.非美女图片的过滤: 通过url路径的字符串匹配来过滤掉部分其它图片.

8.js代码中的图片:  在测试过程中发现有些页面显示的图片为js设置的，因此设置了部分正则表达式来提取js中的图片链接。

9.如果下次要爬其他的美女网站，这个程序如何尽可能利于复用?
  可以直接复用，只需将start_url设置为新的网站主页即可，此项可加入参数中






