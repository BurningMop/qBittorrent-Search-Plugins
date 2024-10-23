# VERSION: 1.3
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


class therarbg(object):
    url = 'https://therarbg.com'
    name = 'The RarBg'
    supported_categories = {
        'all':'All', 
        'movies':'Movies', 
        'tv': 'TV', 
        'music':'Music', 
        'games':'Games', 
        'anime':'Anime', 
        'software':'Apps'
        }
    
    next_page_regex = r'<a.*?>»<\/a>'
    title_regex = r'<title>Search for.*<\/title>'
    has_next_page = True

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        DIV, TABLE, TBODY, TR, TD, A, SPAN, I, B = ('div', 'table', 'tbody', 'tr', 'td', 'a', 'span', 'i', 'b')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.magnet_regex = r'href=["\']magnet:.+?["\']'

            self.url = url
            self.row = {}
            self.column = 0

            self.foundTable = False
            self.foundTableTbody = False
            self.insideRow = False
            self.insideCell = False

            self.shouldParseName = False
            self.shouldGetCategory = False
            self.shouldGetSize = False
            self.shouldGetSeeds = False
            self.shouldGetLeechs = False

            self.alreadyParseName = False
            self.alreadyParsesLink = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')
            elementId = params.get('id', '')

            if tag == self.TABLE:
                self.foundTable = True

            if tag == self.TBODY and self.foundTable:
                self.foundTableTbody = True

            if tag == self.TR and self.foundTableTbody:
                self.column = 0
                self.insideRow = True

            if tag == self.TD and self.insideRow:
                self.column += 1
                self.insideCell = True

            if self.insideCell:
                if self.column == 2 and tag == self.A and not self.alreadyParseName :
                    self.shouldParseName = True
                    href = params.get('href')
                    link = f'{self.url}/{href}'
                    self.row['desc_link'] = link

                    torrent_page = retrieve_url(link)
                    matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                    magnet_urls = [x.group() for x in matches]
                    self.row['link'] = magnet_urls[0].split('"')[1]

                if self.column == 3 and tag == self.A:
                    self.shouldGetCategory = True                 

                if self.column == 6:
                    self.shouldGetSize = True

                if self.column == 7:
                    self.shouldGetSeeds = True

                if self.column == 8:
                    self.shouldGetLeechs = True                    

        def handle_data(self, data):
            if self.shouldParseName:
                self.row['name'] = data
                self.shouldParseName = False
                self.alreadyParseName = True

            if self.shouldGetCategory:
                self.row['name'] += f' ({data.strip()})'
                self.shouldGetCategory = False

            if self.shouldGetSize:
                self.row['size'] = data.replace(',', '.').replace('\xa0', ' ')
                self.shouldGetSize = False

            if self.shouldGetSeeds:    
                self.row['seeds']  = data
                self.shouldGetSeeds = False

            if self.shouldGetLeechs:    
                self.row['leech']  = data
                self.shouldGetLeechs = False

        def handle_endtag(self, tag):
            if tag == self.TD:
                self.insideCell = False

            if tag == self.TR and self.foundTableTbody:
                self.row['engine_url'] = self.url
                prettyPrinter(self.row)
                self.column = 0
                self.row = {}
                self.insideRow = False
                self.alreadyParseName = False


    def download_torrent(self, info):
        print(download_file(info))

    def getPageUrl(self, what, cat, page):
        if not cat == 'All':
            return f'{self.url}/get-posts/order:-se:category:{cat}:keywords:{what}/?page={page}'
        else:
            return f'{self.url}/get-posts/order:-se:keywords:{what}/?page={page}'

    def threaded_search(self, page, what, cat):
        page_url = self.getPageUrl(what, cat, page)
        retrievedHtml = retrieve_url(page_url)
        next_page_matches = re.finditer(self.next_page_regex, retrievedHtml, re.MULTILINE)
        title_matches = re.finditer(self.title_regex, retrievedHtml, re.MULTILINE)
        is_result_page = [x.group() for x in title_matches]
        next_page = [x.group() for x in next_page_matches]
        if len(next_page) == 0:
            self.has_next_page = False
        if is_result_page:
            parser = self.MyHtmlParser(self.url)
            parser.feed(retrievedHtml)
            parser.close()

    def search(self, what, cat = 'all'):
        page = 1
        search_category = self.supported_categories[cat]

        threads = []
        while self.has_next_page:
            t = threading.Thread(args=(page, what, search_category), target=self.threaded_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)
    
            page += 1

        for t in threads:
            t.join()
