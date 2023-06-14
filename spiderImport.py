#-*- coding = utf-8 -*-
# Worker : HAN XIA
# Motto : Practice makes perfect.
# Time : 23/1/2023 9:27 pm

from bs4 import BeautifulSoup     #网页解析，获取数据 （2）拆分爬完的数据
import re     # 正则表达式，文字匹配  （3）进行数据的提炼
import urllib.request, urllib.error  # 制定URL，获取网页数据 （（1）给网页就能爬）
import xlwt  # 进行excel操作 （4）数据存入excel
import sqlite3  #进行SQLite数据库操作  （5）数据存入数据库



#（1）爬取网页

def main():
    #选择要爬取的网页
    baseurl = "https://movie.douban.com/top250?start="
    #将爬取的网页放入datalist里
    datalist = getData(baseurl)
    #生成excel文件，将获取对数据存入该文件中
    # savepath = ".\\doubanTop250.xls"
    # saveDate(savepath)

    askURL("https://movie.douban.com/top250?start=")
    #调用askURL方法， 该方法实现了伪装，会返回爬取后的string类型的数据



def getData(baseurl):  #获取数据，方便调用，返回数据列表
    datalist = []
    for i in range(0, 10): #10次，每次25条，拿到所有的top250
        url = baseurl + str(i*25)
        html = askURL(url) #保存获取到的网页源码
        #注意爬到一个网页就要解析一次 解析数据也将放在此处

    #（2）逐一解析数据
    return  datalist

#得到指定一个URL的网页内容
def askURL(url):
    head = {
       "user-agent":"Mozilla / 5.0(Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
#伪装的本质是告诉服务器我们可以接受什么样的文件

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        #发消息用的是urlopen ，得到的消息保存为response
        html = response.read().decode("utf-8")
        print(html)
    except urllib.error.URLError as e :
        #检测可能的错误，查询错误哦的代码和原因
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e,"reaseon"):
            print(e.reason)
    return  html

#（3）保存数据
def saveDate(savepath):
    pass

if __name__ == "__main__":
#Let code be more clear and easier to read the logic.
#只有当文件被直接执行时，才运行该代码块下的代码。

    main();
#刚刚没有调用main方法。
