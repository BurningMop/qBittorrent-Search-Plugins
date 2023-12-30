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

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter


class xxxclubto(object):
    url = 'https://xxxclub.to'
    name = 'XXXClub'
    supported_categories = {
        'all': 'all',
        'pictures': '5',
    }

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        UL, LI, SPAN, A = ('ul', 'li', 'span', 'a')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
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
                torrent_page = retrieve_url(link)
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

    def search(self, what, cat='all'):
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        category = self.supported_categories[cat]
        page = 1

        while True:
            page_url = f'{self.url}/torrents/browse/{category}/{what}?page={page}' if category else f'{self.url}/torrents/browse/all/{what}?page={page}'
            retrievedHtml = retrieve_url(page_url)
            parser.feed(retrievedHtml)
            if 'title="Next Page">Next</a>' in retrievedHtml:
                break
            page += 1   
        parser.close()
