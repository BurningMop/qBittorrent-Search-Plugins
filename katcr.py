# VERSION: 1.0
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
import xml.etree.ElementTree as ET
import time
import threading
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes

class katcr(object):
    url = 'https://katcr.to'
    name = 'Kickass Torrents'
    supported_categories = {
        'all':'All',
        'anime':'anime',
        'games':'games',
        'movies':'movies',
        'music':'music',
        'software':'apps',
        'tv': 'tv'
        }
    
    pagination_regex = r'<div.*?class=".*?pages.*?">.*<\/div>'
    has_next_page = True

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        TABLE, TR, TD, DIV, A = ('table', 'tr', 'td', 'div', 'a')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.magnet_regex = r'href=["\']magnet:.+?["\']'

            self.url = url
            self.row = {}
            self.column = 0

            self.foundTable = False
            self.insideRow = False
            self.insideCell = False
            self.insideNameCell = False

            self.shouldParseName = False
            self.shouldGetCategory = False
            self.shouldGetSize = False
            self.shouldGetSeeds = False
            self.shouldGetLeechs = False


        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')
            elementId = params.get('id', '')

            if tag == self.TABLE and 'frontPageWidget' in cssClasses:
                self.foundTable = True

            if self.foundTable and tag == self.TR and not 'firstr' in cssClasses:
                self.insideRow = True

            if self.insideRow and tag == self.TD:
                self.column += 1
                self.insideCell = True

                if self.column == 2:
                    self.shouldGetSize = True

                if self.column == 5:
                    self.shouldGetSeeds = True

                if self.column == 6:
                    self.shouldGetLeechs = True                  

            if self.insideCell and tag == self.DIV and 'torrentname' in cssClasses:
                self.insideNameCell = True

            if self.insideNameCell and tag == self.A and 'cellMainLink' in cssClasses:
                self.shouldParseName = False
                self.row['name'] = ''
                href = params.get('href')
                link = f'{self.url}/{href}'
                self.row['desc_link'] = link

                torrent_page = retrieve_url(link)
                matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                magnet_urls = [x.group() for x in matches]
                self.row['link'] = magnet_urls[0].split('"')[1]                

        def handle_data(self, data):
            if self.shouldParseName:
                self.row['name'] += data

            if self.shouldGetSize:
                self.row['size'] = data
                self.shouldGetSize = False

            if self.shouldGetSeeds:    
                self.row['seeds']  = data
                self.shouldGetSeeds = False

            if self.shouldGetLeechs:    
                self.row['leech']  = data
                self.shouldGetLeechs = False

        def handle_endtag(self, tag):
            if tag == self.A and self.shouldParseName:
                self.shouldParseName = False

            if tag == self.DIV and self.insideNameCell:
                self.insideNameCell = False

            if tag == self.TD:
                self.insideCell = False

            if tag == self.TR and self.insideRow:
                self.row['engine_url'] = self.url
                prettyPrinter(self.row)
                self.column = 0
                self.row = {}
                self.insideRow = False


    def download_torrent(self, info):
        print(download_file(info))

    def getPageUrl(self, what, cat, page):
        if cat == 'All':
            return f'{self.url}/search/{what}/{page}/'
        else:
            return f'{self.url}/search/{what}/category/{cat}/{page}/'
        

    def threaded_search(self, page, what, cat):
        parser = self.MyHtmlParser(self.url)
        page_url = self.getPageUrl(what, cat, page)
        retrievedHtml = retrieve_url(page_url)
        parser.feed(retrievedHtml)
        parser.close()

    def getLastPage(self, html):
        pagination_matches = re.finditer(self.pagination_regex, html, re.MULTILINE)
        pages = [x.group() for x in pagination_matches]
        lastPage = 0

        if len(pages) > 0:
            pagesHtml = pages[0].replace('</ul>','')
            with open('katcr.pages.html', 'w') as writer:
                writer.write(pagesHtml)    
                    
            root = ET.fromstring(pagesHtml)
            for child in root:
                if child.text.isnumeric():
                    if int(child.text) > lastPage:
                        lastPage = int(child.text)
        return lastPage

    def search(self, what, cat = 'all'):
        search_category = self.supported_categories[cat]
        page = 1

        page_url = self.getPageUrl(what, search_category, page)
        retrievedHtml = retrieve_url(page_url)
        lastPage = self.getLastPage(retrievedHtml)

        parser = self.MyHtmlParser(self.url)
        parser.feed(retrievedHtml)
        parser.close()

        page += 1

        threads = []
        while page <= lastPage:
            t = threading.Thread(args=(page, what, search_category), target=self.threaded_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)

            page += 1

        for t in threads:
            t.join()
