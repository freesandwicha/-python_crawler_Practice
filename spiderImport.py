#-*- coding = utf-8 -*-
# Worker : HAN XIA
# Motto : Practice makes perfect.
# Time : 23/1/2023 9:27 pm

from bs4 import BeautifulSoup     #网页解析，获取数据 （2）拆分爬完的数据
import re     # 正则表达式，文字匹配  （3）进行数据的提炼
import urllib.request, urllib.error  # 制定URL，获取网页数据 （（1）给网页就能爬）
import xlwt  # 进行excel操作 （4）数据存入excel
import sqlite3  #进行SQLite数据库操作  （5）数据存入数据库

findLink = re.compile(r'<a href="(.*?)">') #?表示有可能会没有这个
findImgScr = re.compile(r'<img.*src="(.*?)"', re.S) #.*表示img 和src之间一定会有若干数据（字符尽可能的多) 如果？表示可能没有 re.S忽视换行符
findTitle = re.compile(r'<span class="title">(.*?)</span>')
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>') # 可以单独提取出(.*？）里的内容，而不是r里的全部
findJudgeNumber = re.compile(r'<span>(\d*)人评价</span>') #\d*表示一个或多个数字，也就是我们要找的人数 如果只是\d就会查找一个数字
findInq = re.compile(r'<span class="inq">(.*?)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)

#（1）爬取网页

def main():
    #选择要爬取的网页
    baseurl = "https://movie.douban.com/top250?start="
    #将爬取的网页放入datalist里
    datalist = get_data(baseurl)
    #生成excel文件，将获取对数据存入该文件中
    #savepath = "doubanTop250.xls"
    print("Finished Python crawler")
    dbpath = "Movie.db"
    #存入数据库
    #saveData(datalist, savepath)
    saveData2DB(datalist, dbpath)
    print("Successfully save")

    #askURL("https://movie.douban.com/top250?start=")
    #调用askURL方法， 该方法实现了伪装，会返回爬取后的string类型的数据


def get_data(baseurl):  #获取数据，方便调用，返回数据列表
    datalist = []
    for i in range(0, 10): #10次，每次25条，拿到所有的top250
        url = baseurl + str(i*25)
        html = askURL(url) #保存获取到的网页源码
        #注意爬到一个网页就要解析一次 解析数据也将放在此处

    #（2）逐一解析数据
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):  #查找符合要求的字符串，形成列表
            # print(item)
            data = []  # 保存一部电影的所有信息
            item = str(item)

            link = re.findall(findLink, item)[0] #再在列表里面找link
            # tips: findall所带的参数，第一个必须是正则表达式，第二个必须是string
            #  findall将会返回列表 findall[0]则返回的是列表里的第一个参数，这里就是链接啦！
            data.append(link)
            imgSCR = re.findall(findImgScr,item)[0]
            data.append(imgSCR)
            #print(imgSCR)

            titles = re.findall(findTitle, item)
            if(len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)   #添加中文名
                otitle = titles[1].replace("/", '').replace("\xa0", '')  #去掉无关的信息
                data.append(otitle)   #添加外国名
            else:
                data.append(titles[0])
                data.append(' ')   #当出现没有外国名时，外国名留空就行了

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judge_number = re.findall(findJudgeNumber, item)[0]
            data.append(judge_number)

            inq = re.findall(findInq, item)
            if (len(inq) != 0):
                inq = inq[0].replace("。", " ")
                data.append(inq)
            else:
                data.append(" ")     #留空，如果没有的话

            bd = re.findall(findBd, item)[0]
            bd = re.sub("\xa0", " ", bd)   # 把"&nbsp;"替换为空格
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)   #去掉<br/>
            bd = re.sub("\n", " ", bd)
            bd = re.sub("/", '', bd)   #再把/替换为空格
            data.append(bd.strip())  #strip()去掉前后的空格
            datalist.append(data)    #把处理好的一部电影的信息放入datalist

            # for span in soup.find_all("span",class_="title"):
        #     print(span)  # 爬取符合网页属性的数据 这样就能找到想要的东西。
    # print(datalist)
    return datalist

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
        # print(html)
    except urllib.error.URLError as e:
        #检测可能的错误，查询错误哦的代码和原因
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e,"reaseon"):
            print(e.reason)
    return  html

#（3）保存数据
def saveData(datalist, savepath):
    print("save...")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet("MoveTop250", cell_overwrite_ok=True)
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])  #写入列名
    for i in range(0, 250):
        print("No.%d"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])

    book.save(savepath)


def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    for data in datalist:
        #datalist是250个list 组成
        #把datalist中的每个list依次赋值给data, 也就是一个data就是一个list
        for index in range(len(data)):
            #表示data列表的长度，也就是列表中的元素个数
            #把一个data(本身是list）中的每一个元素提取出来依次赋值给index
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
            #把每一个元素都添加”“来转换为string语句，用于数据库的插入，但并不是每个字符都需要转为string
            #这样先把一个data（本身是list）中的八个元素都分别转换为string
            #每转换一次，执行下插入语句，并执行保存

        sql = '''
            INSERT INTO movie250(
            info_link, pic_link, cname, ename, score, rated, instroduction, info)
            values(%s)'''%",".join(data)
        #把转换的第一个data的八个元素插入数据表中
        #使用 ",".join(data) 将生成的新列表中的元素以逗号分隔拼接成一个字符串。
        cursor.execute(sql)
        conn.commit()
        #保存完毕这一个sql语句，就取执行for data in datalist语句，接着是第二个data中的每个元素的转换和保存
    cursor.close()
    conn.close()


def init_db(dbpath):
    sql = '''
        CREATE TABLE movie250
            (id integer primary key autoincrement, 
            info_link text,
            pic_link text,
            cname varchar,
            ename varchar,
            score numeric,
            rated numeric,
            instroduction text,
            info text )
    '''   #创建并初始化数据库
    #	当"文本数据"被插入到亲缘性为NUMERIC的字段中时，如果转换操作不会导致数据信息丢失以及完全可逆，
    #	那么SQLite就会将该 "文本数据" 转换为INTEGER或REAL类型的数据，如果转换失败，SQLite仍会以TEXT方式存储该数据
    #	对于亲缘类型为INTEGER的字段，其规则等同于NUMERIC，唯一差别是在执行CAST表达式时。
    conn = sqlite3.connect(dbpath) #如果数据库存在就连接，不存在就创建
    cursor = conn.cursor()
    cursor.execute(sql)   #执行   （只是查询的话，就不需要commit的了）
    conn.commit()    #提交修改命令并永久化
    conn.close()


if __name__ == "__main__":
#Let code be more clear and easier to read the logic.
#只有当文件被直接执行时，才运行该代码块下的代码。

    main()
#刚刚没有调用main方法。
