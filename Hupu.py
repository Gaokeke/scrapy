# -*- coding: utf-8 -*-
''''' 
creat on 2017.4.15 
@author: gaokeke 
'''

import urllib2
from bs4 import BeautifulSoup
import logging

# 以下解决编码问题，与主题无关
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class Item(object):
    title = None  # 帖子标题
    firstAuthor = None  # 帖子原作者
    firstTime = None  # 帖子创建时间
    reNum = None  # 帖子回复浏览数量
    LastTime = None  # 帖子最后回复时间
    LastAuthor = None  # 帖子最后回复作者
    link = None  # 帖子链接


# 全局方法获取网页内容
def getResponseContent(url):
    try:
        response = urllib2.urlopen(url.encode('utf8'), timeout=20)
    except:
        logging.error(u'Python返回URL：{}数据失败'.format(url))
    else:
        logging.info(u'Python返回URL：{}数据成功'.format(url))
        return response.read()


class getHupuInfo(object):
    def __init__(self, url):
        self.url = url
        self.pageSum = 3  # 帖子页数做多100页
        self.urls = self.getUrls(self.pageSum)
        self.items = self.spider(self.urls)
        self.pipelines(self.items)

    def getUrls(self, pageSum):
        urls = []
        urls.append(self.url)
        for pn in range(1, pageSum):
            tempurl = self.url + '-' + str(pn + 1)
            urls.append(tempurl)
        logging.info(u'获取URLS成功！\n')
        return urls

    def spider(self, urls):
        items = []
        for url in urls:
            htmlContent = getResponseContent(url)
            soup = BeautifulSoup(htmlContent, 'lxml')
            tagtable = soup.find('table', attrs={'id': 'pl'})
            tagstr = tagtable.find_all('tr')

            flag = 0  # 跳过标题栏
            for tag in tagstr:
                if flag == 0:
                    flag += 1
                    continue
                else:
                    flag += 1
                    item = Item()
                    item.link = '/' + tag.get('mid') + '.html'  # 直接抓取mid属性作为帖子链接
                    item.title = tag.find('td', attrs={'class': 'p_title'}).find('a',
                                                                                 href=item.link).get_text()  # 通过item.link来确定标题
                    item.firstAuthor = tag.find('td', attrs={'class': 'p_author'}).a.get_text()
                    item.firstTime = tag.find('td', attrs={'class': 'p_author'}).get_text()
                    item.reNum = tag.find('td', attrs={'class': 'p_re'}).get_text()
                    item.LastAuthor = tag.find('td', attrs={'class': 'p_retime'}).a.get_text()
                    item.LastTime = tag.find('td', attrs={'class': 'p_retime'}).get_text()
                    items.append(item)
        logging.info(u'获取帖子成功')
        return items

    def pipelines(self, items):
        fileName = u'Hupu_bxj.txt'
        with open(fileName, 'w') as fp:
            for item in items:
                # fp.write('{}\t{}\t{}\t{}\t{}\t{}\n{}\n\n'.format(item.title,item.firstAuthor,item.firstTime,item.reNum,item.LastAuthor,item.LastTime,item.link))
                fp.write('{}\n '.format(item.title).encode('utf8'))  # 为了生词词云，这里只提取了题目
        logging.info(u'写入文本成功')

    def getpiclink(self):
        piclink = []
        for item in self.items:
            piclink.append(self.url[0:20] + item.link)
        logging.info(u'返回图片帖子链接成功')
        return piclink


class picInfo(object):
    def __init__(self, links):
        self.links = links
        self.imgurls = []
        self.spider()
        self.pipeline()

    def spider(self):

        if self.links == None:
            logging.error('无图片链接')
        else:
            for link in self.links:
                htmlContent = getResponseContent(link)
                soup = BeautifulSoup(htmlContent, 'lxml')
                tagDiv = soup.find('div', attrs={'id': 'tpc'})
                img = tagDiv.find('div', attrs={'class': 'quote-content'}).find_all('img')
                if img == None:
                    continue
                else:
                    for subimg in img:
                        # 解决图片未加载的情况
                        if subimg.get('data-original') == None:
                            imgurl = subimg.get('src')
                        else:
                            imgurl = subimg.get('data-original')
                        self.imgurls.append(imgurl)
        logging.info(u'获取图片链接成功')

    def pipeline(self):

        for i in range(len(self.imgurls)):
            # 根据链接后缀确定图片类型
            if self.imgurls[i][-3:] == 'png':
                imgname = str(i) + '.png'
            elif self.imgurls[i][-3:] == 'jpg':
                imgname = str(i) + '.jpg'
            elif self.imgurls[i][-4:] == 'jpeg':
                imgname = str(i) + '.jpeg'
            elif self.imgurls[i][-3:] == 'gif':
                imgname = str(i) + '.jpeg'
            else:
                continue
            img = getResponseContent(self.imgurls[i])

            with open(imgname, 'ab') as fp:
                fp.write(img)
        logging.info(u'写入图片成功')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    url = u'https://bbs.hupu.com/selfie'
    HUPU = getHupuInfo(url)
    picurls = HUPU.getpiclink()
    PIC = picInfo(picurls)