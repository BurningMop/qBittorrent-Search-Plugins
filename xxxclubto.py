# VERSION: 1.2
# AUTHORS: BurningMop (burning.mop@yandex.com)

# LICENSING INFORMATION
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import re
from html.parser import HTMLParser
import time
import threading
import urllib.error
import urllib.parse
import urllib.request
from helpers import download_file, htmlentitydecode
from novaprinter import prettyPrinter

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Referer': 'https://xxxclub.to'
}

def retrieve_url(url, customHeaders=headers):
    """ Return the content of the url page as a string """
    req = urllib.request.Request(url, headers=customHeaders)
    try:
        response = urllib.request.urlopen(req)
    except urllib.error.URLError as errno:
        print(" ".join(("Connection error:", str(errno.reason))))
        return ""
    dat = response.read()
    # Check if it is gzipped
    if dat[:2] == b'\x1f\x8b':
        # Data is gzip encoded, decode it
        compressedstream = io.BytesIO(dat)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        extracted_data = gzipper.read()
        dat = extracted_data
    info = response.info()
    charset = 'utf-8'
    try:
        ignore, charset = info['Content-Type'].split('charset=')
    except Exception:
        pass
    dat = dat.decode(charset, 'replace')
    dat = htmlentitydecode(dat)
    # return dat.encode('utf-8', 'replace')
    return dat

class xxxclubto(object):
    url = 'https://xxxclub.to'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Referer': url
    }    
    name = 'XXXClub'
    supported_categories = {
        'all': 'All',
        'pictures': '5',
    }

    container_regex = r'<div.*?class=".*?browsetableinside.*?".*?>(?s:.)*?<\/div>'
    items_regex = r'<li.*?>(?s:.)*?<\/li>'

    has_results = True

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        UL, LI, SPAN, A = ('ul', 'li', 'span', 'a')
    
        def __init__(self, url, headers):
            HTMLParser.__init__(self)
            self.url = url
            self.headers = headers
            self.headers['Referer'] = url
            self.row = {}
            self.column = 0
            self.foundResults = False
            self.foundTable = False
            self.insideRow = False
            self.insideCell = False
            self.insideNameLink = False
            self.foundTableHeading = False
            self.foundRowCatlabe = False
            self.magnet_regex = r'href="magnet:.*"'
    
        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            if 'browsetableinside' in params.get('class', ''):
                self.foundResults = True
                return
            if self.foundResults and tag == self.UL:
                self.foundTable = True
                return
            if self.foundTable and tag == self.LI:
                self.insideRow = True
                return
            if self.insideRow and self.foundTableHeading and tag == self.SPAN:
                classList = params.get('class', None)
                if self.foundRowCatlabe:
                    self.insideCell = True
                    self.column += 1
                if 'catlabe' == classList:
                    self.foundRowCatlabe = True 
                return
            if self.insideRow and self.foundTableHeading and self.column == 1 and tag == self.A:
                self.insideNameLink = True
                href = params.get('href')
                link = f'{self.url}{href}'
                self.row['desc_link'] = link
                self.row['link'] = link
                torrent_page = retrieve_url(link, self.headers)
                matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                magnet_urls = [x.group() for x in matches]
                self.row['link'] = magnet_urls[0].split('"')[1]
                return
    
        def handle_data(self, data):
            if self.insideCell and self.foundRowCatlabe:
                if self.column == 1 and self.insideNameLink:
                    self.row['name'] = data
                if self.column == 3:
                    size = data.replace(',', '')
                    self.row['size'] = size
                if self.column == 4:
                    self.row['seeds'] = data
                if self.column == 5:
                    self.row['leech'] = data
            return
    
        def handle_endtag(self, tag):
            if self.insideCell and self.insideNameLink and tag == self.A:
                self.insideNameLink = False
            if self.insideCell and tag == self.SPAN:
                self.insideCell = False
            if self.insideRow and tag == self.LI:
                if not self.foundTableHeading:
                    self.foundTableHeading = True
                else:
                    self.row['engine_url'] = self.url
                    prettyPrinter(self.row)
                    self.insideRow = False
                    self.foundRowCatlabe = False
                    self.column = 0
                    self.row = {}
                return

    def download_torrent(self, info):
        print(download_file(info))

    def getPageUrl(self, what, category, page):
        return f'{self.url}/torrents/browse/{category}/{what}?page={page}'

    def hasResults(self, html):
        container_matches = re.finditer(self.container_regex, html, re.MULTILINE)
        container = [x.group() for x in container_matches]

        if len(container) > 0:
            containerHtml = container[0]
            items_matches = re.finditer(self.items_regex, containerHtml, re.MULTILINE)
            items = [x.group() for x in items_matches]
            self.has_results = len(items) > 1
        else:
            self.has_results = False

    def threaded_search(self, page, what, cat):
        page_url = self.getPageUrl(what, cat, page)
        self.headers['Referer'] = page_url
        retrievedHtml = retrieve_url(page_url, self.headers)
        self.hasResults(retrievedHtml)
        parser = self.MyHtmlParser(self.url, self.headers)
        if self.has_results:
            parser.feed(retrievedHtml)
            parser.close()           

    def search(self, what, cat='all'):
        parser = self.MyHtmlParser(self.url, self.headers)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        category = self.supported_categories[cat]
        page = 1

        threads = []
        while self.has_results:
            t = threading.Thread(args=(page, what, category), target=self.threaded_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)
    
            page += 1

        for t in threads:
            t.join()
