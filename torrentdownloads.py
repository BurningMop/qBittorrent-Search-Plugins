# VERSION: 1.1
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
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes

class torrentdownloads(object):
    url = 'https://torrentdownloads.pro'
    name = 'Torrent Downloads'
    supported_categories = {
        'all':'0',
        'anime':'1',
        'books': '2',
        'games':'3',
        'movies':'4',
        'music':'5',
        'software':'7',
        'tv': '8'
        }
    
    next_page_regex = r'<a.*?>>><\/a>'
    has_next_page = True

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        DIV, P, A, SPAN, B = ('div', 'p', 'a', 'span', 'b')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.magnet_regex = r'href=["\']magnet:.+?["\']'

            self.url = url
            self.row = {}
            self.column = 0

            self.foundContainer = False
            self.insideRow = False
            self.insideCell = False
            self.insideNameCell = False

            self.shouldParseName = False
            self.shouldGetCategory = False
            self.shouldGetSize = False
            self.shouldGetSeeds = False
            self.shouldGetLeechs = False

            self.alreadyParseName = False
            self.alreadyParsesLink = False
            self.shouldSkipResult = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')

            if 'inner_container' in cssClasses:
                self.foundContainer = True

            if 'grey_bar3' in cssClasses and tag == self.DIV:
                self.insideRow = True

            if self.insideRow and tag == self.SPAN and not self.shouldSkipResult:
                self.column += 1
                self.insideCell = True

            if self.insideRow and tag == self.P:
                self.insideNameCell = True

            if self.insideCell:
                if self.column == 2:
                    self.shouldGetLeechs = True

                if self.column == 3:
                    self.shouldGetSeeds = True

                if self.column == 4:
                    self.shouldGetSize = True

            if self.insideNameCell and tag == self.A:
                self.shouldParseName = True
                href = params.get('href')
                if href.startswith("/torrent/"):
                    link = f'{self.url}/{href}'
                    self.row['desc_link'] = link

                    torrent_page = retrieve_url(link)
                    matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                    magnet_urls = [x.group() for x in matches]
                    self.row['link'] = magnet_urls[0].split('"')[1]
                else:
                    self.shouldSkipResult = True
                    
            if self.insideNameCell and tag == self.B:
                self.shouldSkipResult = True

        def handle_data(self, data):
            if self.shouldParseName:
                self.row['name'] = data
                self.shouldParseName = False

            if self.shouldGetSize:
                size = data.replace('&nbsp;', '').replace('\xa0', ' ')
                self.row['size'] = size
                self.shouldGetSize = False

            if self.shouldGetSeeds:    
                self.row['seeds']  = data
                self.shouldGetSeeds = False

            if self.shouldGetLeechs:    
                self.row['leech']  = data
                self.shouldGetLeechs = False

        def handle_endtag(self, tag):
            if tag == self.SPAN or tag == self.P:
                self.insideCell = False

            if tag == self.P:
                self.insideNameCell = False

            if tag == self.DIV and self.insideRow:
                self.row['engine_url'] = self.url
                if not self.shouldSkipResult:
                    prettyPrinter(self.row)
                self.column = 0
                self.row = {}
                self.insideRow = False
                self.shouldSkipResult = False


    def download_torrent(self, info):
        print(download_file(info))

    def getPageUrl(self, what, cat, page):
        return f'{self.url}/search/?new=1&s_cat={cat}&search={what}&page={page}'

    def threaded_search(self, page, what, cat):
        parser = self.MyHtmlParser(self.url)
        page_url = self.getPageUrl(what, cat, page)
        retrievedHtml = retrieve_url(page_url)
        next_page_matches = re.finditer(self.next_page_regex, retrievedHtml, re.MULTILINE)
        next_page = [x.group() for x in next_page_matches]
        if len(next_page) == 0:
            self.has_next_page = False
        parser.feed(retrievedHtml)
        parser.close()            

    def search(self, what, cat = 'all'):
        page = 1
        search_category = self.supported_categories[cat]
        what = what.replace("%20", "+")
        what = what.replace(" ", "+")

        threads = []
        while self.has_next_page:
            t = threading.Thread(args=(page, what, search_category), target=self.threaded_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)
    
            page += 1

        for t in threads:
            t.join()
