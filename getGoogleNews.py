from datetime import timedelta
from datetime import datetime
import time
import requests
import feedparser
from goose3 import Goose
from bs4 import BeautifulSoup
from selenium import webdriver
import os

# Get links from google news
def getDateAndLinks(keyword, t1, t2):
    url = 'https://news.google.com/rss/search?q=' + keyword + \
        '+after:' + t1 + '+before:' + t2 + '&ceid=US:en&hl=en-US&gl=US'
    text = getData(url)
    datas = feedparser.parse(text).entries
    links = []
    driver = webdriver.Chrome()
    for data in datas:
        date = data.published
        driver.get(data.link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        linkTag = soup.find('a')
        if linkTag == None:
            continue
        links.append([date, linkTag.text])
    driver.quit()
    return links

# Get data from link
def getData(link):
    try:
        response = requests.get(link)
        return response.text
    except:
        return getData(link)

# Get article from link
def getArticle(link, g):
    try:
        article = g.extract(url=link)
        return article.cleaned_text
    except:
        return ""

# Get news from keyword and term
def saveNews(keyword, tS1, tS2, path, save=True):
    g = Goose({'browser_user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2)',
              'parser_class': 'soup', 'strict': False})
    t1 = datetime.strptime(tS1, "%Y-%m-%d")
    t2 = datetime.strptime(tS2, "%Y-%m-%d")
    linkList = []
    while t1 <= t2:
        timeStr1 = t1.strftime("%Y-%m-%d")
        timeStr2 = (t1 + timedelta(days=1)).strftime("%Y-%m-%d")
        print(t1, timeStr1)
        links = getDateAndLinks(keyword, timeStr1, timeStr2)
        for link in links:
            linkList.append(link)
        t1 += timedelta(days=2)
    with open(path + 'header.txt', 'r', encoding='UTF-8') as headerFile:
        index = int(headerFile.readline())
    file_list = os.listdir(path)
    for file in file_list:
        name = file.split('.')[0]
        if not name.isnumeric():
            continue
        else:
            nameNum = int(name)
        if index <= nameNum:
            os.remove(path+file)
    for link in linkList:
        index += 1
        article = getArticle(link[1], g)
        if article == "" or article == None or article == "Please enable JS and disable any ad blocker" or article == "Keep me logged in from this computer." or article.startswith("Access to this page has been denied because we believe you are using automation tools to browse the website."):
            continue
        with open(path + str(index) + '.txt', 'w', encoding='UTF-8') as outfile:
            outfile.write(str(link[0]) + "\n\n" + article)
    if save:
        with open(path + 'header.txt', 'w', encoding='UTF-8') as headerFile:
            headerFile.write(str(index+1) + '\n')

# Parse time from string
#   ex) "Tue, 02 Apr 2024 13:07:16 GMT"
#         -> time.struct_time(tm_year=2024, tm_mon=4, tm_mday=2, tm_hour=13, tm_min=7, tm_sec=16, tm_wday=1, tm_yday=93, tm_isdst=-1)
#   ref) https://docs.python.org/ko/3/library/datetime.html#strftime-strptime-behavior


def parseTime(timeStr):
    timeObj = time.strptime(timeStr, "%a, %d %b %Y %H:%M:%S %Z")
    return timeObj

if __name__ == "__main__":
    saveNews('AVGO', "2024-05-14", "2024-05-15", "./test_AVGO/")
#False -> 시장열릴때/저장안함 / True -> 시장닫힐때/저장함
# saveNews('ASML', "2024-04-05", "2024-04-05", "./test_ASML/")

# # ---------------
# # | 파일로 저장하기 |
# # ---------------
# # getDateAndLinks 로 구글 뉴스에서 키워드와 기간을 입력받아 해당 기사들의 링크를 반환
# g = Goose({'browser_user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2)', 'parser_class':'soup', 'strict': False})
# links = getDateAndLinks('TSLA', 1)

# # getArticle 로 링크를 입력받아 해당 기사의 본문을 ./articles/ 폴더 안에 파일로 저장
# for index in range(len(links)):
#   with open('./articles/' + str(index+1) + '.txt', 'w') as outfile:
#     outfile.write(getArticle(links[index][1], g))

# # ----------------
# # | 리스트로 저장하기 |
# # ----------------
# articles = getNews('TSLA', 1)
# # print(articles)
# print(len(articles))


# -----------------
# | 파일로 저장하기 2 |
# -----------------
# saveNews('TSLA', "2024-03-05", "2024-04-04", "./test3/")



# # -----------------
# # | 파일로 저장하기 3 |
# # -----------------
# articles = getNews('TSLA')
# for index in range(len(articles)):
#     with open('./test2/' + str(index+1) + '.txt', 'w') as outfile:
#         outfile.write(articles[index])
