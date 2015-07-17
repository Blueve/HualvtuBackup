__author__ = 'Blueve'
import sys
import requests
from bs4 import BeautifulSoup


class Task(object):
    HEADER = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': '',
        'Referer': 'http://www.hualvtu.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36',
    }

    def __init__(self, album_url):
        self.album_url = album_url
        self.session = requests.session()
        self.__set_header(album_url)
        self.result = []

    def run(self):
        """
        Excute current task.
        :return: Photo's url and description
        """
        print('Getting all metadatas from: ' + self.album_url)
        self.__parser()
        print('Downloading...')
        self.__downloader()
        return self.result

    def __set_header(self, url):
        """
        Set HTTP request header.
        :return: None
        """
        self.HEADER['Host'] = url.split('/')[2]
        self.session.headers.update(self.HEADER)

    def __parser(self):
        """
        Get the page source and find all photo's url and description.
        :return: None
        """
        response = self.session.get(self.album_url)
        soup = BeautifulSoup(response.content)
        articles = soup.find_all('div', class_='quark-article')
        item = []
        for article in articles:
            item.append(article['photo'])
            item.append(article.find_all('div', class_='articleContent-text')[0].get_text())
            self.result.append(item)
            item = []

    def __downloader(self):
        """
        Read self.result list, download all photos by url.
        :return: None
        """
        done_count = 0
        all_count = len(self.result)
        done_bar = ''
        space_bar = ' ' * 20
        sys.stdout.write("\r[%s]\t%d%%\t(%d/%d)" % (done_bar + space_bar, 0, 0, all_count))
        for item in self.result:
            # Update header
            self.__set_header(item[0])
            # Set storage location
            filename = item[0].split('/')[-1]
            # Send download request and write image data to file
            response = self.session.get(item[0], stream=True)
            with open(filename, 'wb') as f:
                for chunk in response.iter_content():
                    f.write(chunk)
            done_count += 1
            # Update progress bar
            done_bar = '#' * int(done_count * 20 / all_count)
            space_bar = ' ' * (20 - len(done_bar))
            sys.stdout.write("\r[%s]\t%d%%\t(%d/%d)" %
                             (done_bar + space_bar,
                              done_count * 100 / all_count,
                              done_count, all_count))