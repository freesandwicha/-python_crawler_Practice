#-*- coding = utf-8 -*-
# Worker : HAN XIA
# Motto : Practice makes perfect.
# Time : 23/1/2023 9:27 pm

from bs4 import BeautifulSoup     #Web parsing, data retrieval (2), and splitting the scraped data."
import re     # Regular expressions, text matching (3), and data extraction."
import urllib.request, urllib.error  # Specify URL, retrieve web page data (1）: Crawling a webpage by providing the URL)）
import xlwt  # Excel operations (4) - Saving data into Excel."
import sqlite3  #SQLite database operations (5) - Storing data into the database.

findLink = re.compile(r'<a href="(.*?)">') # ? means its possible don't have * (any character)
findImgScr = re.compile(r'<img.*src="(.*?)"', re.S) #".*" means there will be some data (as many characters as possible) between 'img' and 'src'. If '?' is used, it indicates that there may or may not be data present. 're.S' is used to ignore newline characters during the matching process.
findTitle = re.compile(r'<span class="title">(.*?)</span>')
findRating = re.compile(r'<span class="rating_num" property="v:average">(.*?)</span>') # It is possible to extract the content inside (.*?) separately, rather than the entire match in 'r'
findJudgeNumber = re.compile(r'<span>(\d*)人评价</span>') # \d* represents one or more digits, which is the number of people we are looking for. If it is just '\d', it will match a single digit."
findInq = re.compile(r'<span class="inq">(.*?)</span>')
findBd = re.compile(r'<p class="">(.*?)</p>', re.S)

#（1）爬取网页

def main():
    #Select the webpage to be crawled.
    baseurl = "https://movie.douban.com/top250?start="
    #Put the crawled webpage into a datalist.
    datalist = get_data(baseurl)
    #Generate an Excel file and store the retrieved data into that file.
    #savepath = "doubanTop250.xls"
    #saveData(datalist, savepath)
    print("Finished Python crawler")

    # save data into database
    dbpath = "Movie.db"
    saveData2DB(datalist, dbpath)
    print("Successfully save")

    #askURL("https://movie.douban.com/top250?start=")
    #Call the askURL method, which implements spoofing, and it will return the crawled data in the form of a string.


#Retrieve the data for easy access and return it as a list.
def get_data(baseurl):
    datalist = []
    for i in range(0, 10): #Get all the top 250 items, 25 items per request, for a total of 10 requests
        url = baseurl + str(i*25)
        html = askURL(url)
        #Save the retrieved webpage source code
        #Each time a webpage is crawled, data parsing will be performed right after to extract the relevant information.

    #（2）Parse the data one by one.
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all("div", class_="item"):  #Search for strings that meet the criteria and form a list.
            # print(item)
            data = []  # Save all the information of a movie
            item = str(item)

            link = re.findall(findLink, item)[0] #Then, search for links within the list
            # tips: findall: The first parameter must be a regular expression, and the second parameter must be a string
            #  findall will get a list    findall[0]will get the first element from list. Here, it's a link.
            data.append(link)
            imgSCR = re.findall(findImgScr,item)[0]
            data.append(imgSCR)
            #print(imgSCR)

            titles = re.findall(findTitle, item)
            if(len(titles) == 2):
                ctitle = titles[0]
                data.append(ctitle)   #Add Chinese name
                otitle = titles[1].replace("/", '').replace("\xa0", '')  #Remove irrelevant information.
                data.append(otitle)   #Add other name with different languages.
            else:
                data.append(titles[0])
                data.append(' ')   #When there is no foreign name available, leave the foreign name field empty.

            rating = re.findall(findRating, item)[0]
            data.append(rating)

            judge_number = re.findall(findJudgeNumber, item)[0]
            data.append(judge_number)

            inq = re.findall(findInq, item)
            if (len(inq) != 0):
                inq = inq[0].replace("。", " ")
                data.append(inq)
            else:
                data.append(" ")
                #Leave it blank if it's not available.

            bd = re.findall(findBd, item)[0]
            bd = re.sub("\xa0", " ", bd)   # replace "&nbsp;" to a blank
            bd = re.sub('<br(\s+)?/>(\s+)?'," ",bd)   #move <br/>
            bd = re.sub("\n", " ", bd)
            bd = re.sub("/", '', bd)   #replace / to a blank
            data.append(bd.strip())  #strip() removes leading or trailing spaces.
            datalist.append(data)    #Put the processed information of a movie into the datalist.

            # for span in soup.find_all("span",class_="title"):
        #     print(span)  #Crawl the data that matches the webpage attributes, and this way, we can find what we are looking for.
    # print(datalist)
    return datalist

#Retrieve the content of a specified URL webpage.

def askURL(url):
    head = {
       "user-agent":"Mozilla / 5.0(Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36(KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    }
    # The essence of spoofing is to inform the server what type of files we can accept.

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        #send information by urlopen ，get and save information by response
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        #Detect potential errors and query error codes and their reasons.
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e,"reaseon"):
            print(e.reason)
    return  html

#（3）save data into Excel
def saveData(datalist, savepath):
    print("save...")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # create the object of workbook
    sheet = book.add_sheet("MoveTop250", cell_overwrite_ok=True)
    col = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", "评分", "评价数", "概况", "相关信息")
    for i in range(0, 8):
        sheet.write(0, i, col[i])  #Write column headers.
    for i in range(0, 250):
        print("No.%d"%(i+1))
        data = datalist[i]
        for j in range(0,8):
            sheet.write(i+1,j,data[j])

    book.save(savepath)

#or (3)save data into a database
def saveData2DB(datalist, dbpath):
    init_db(dbpath)
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    for data in datalist:
        #datalist is consist of 250 lists
        #Assign each list in the datalist to the variable "data" one by one, so that each "data" represents a separate list.
        for index in range(len(data)):
            #The length of the data list, i.e., the number of elements in the list.
            #Extract each element from a "data" (which is itself a list) and assign them one by one to the variable "index."
            if index == 4 or index == 5:
                continue
            data[index] = '"'+data[index]+'"'
            #Add double quotes to each element to convert them into string format, which is used for database insertion.
            # However, not every character needs to be converted to a string.
            #In this way, convert the eight elements of a "data" (which is itself a list) into strings one by one.
            #After each conversion, execute the insertion statement and perform the save operation.

        sql = '''
            INSERT INTO movie250(
            info_link, pic_link, cname, ename, score, rated, instroduction, info)
            values(%s)'''%",".join(data)
        #Insert the eight converted elements from the first "data" into the database table.
        #Using ",".join(data) will concatenate the elements of the newly generated list into a single string, separated by commas.
        cursor.execute(sql)
        conn.commit()
    cursor.close()
    conn.close()

#Define the basic construction of the database.
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
    '''   #Create and initialize the database.
    conn = sqlite3.connect(dbpath) #If the database exists, connect to it; if it doesn't exist, create it.
    cursor = conn.cursor()
    cursor.execute(sql)   #execute   （Only for querying, there is no need for commit）
    conn.commit()    #Submit the modification command and persist it permanently.
    conn.close()


if __name__ == "__main__":
#Let code be more clear and easier to read the logic.
    main()
