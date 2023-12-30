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
from novaprinter import prettyPrinter, anySizeToBytes


class traht(object):
    url = 'https://traht.org'
    name = 'Traht'
    supported_categories = {
        'all': 'all'
    }
    
    pagination_regex = r'<div class="paginator_pages">.*?<\/div>'

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

            self.releaseTableFound = False
            self.insideResultTbody = False
            self.insideRow = False
            self.insideCell = False

            self.shouldGetName = False
            self.shouldParseLink = True
            self.shouldGetSize = False
            self.shouldGetPeers = False
            self.shouldGetSeeds = False
            self.shouldGetLeechs = False
    
        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')
            elementId = params.get('id', '')

            if elementId == 'releases-table':
                self.releaseTableFound = True
                return

            if self.releaseTableFound and elementId == 'highlighted' and tag == self.TBODY:
                self.insideResultTbody = True
                return

            if self.insideResultTbody and tag == self.TR:
                self.insideRow = True
                self.column = 0
                return

            if self.insideRow and tag == self.TD:
                self.column += 1
                self.insideCell = True
                if self.column == 5:
                    self.shouldGetSize = True

                if self.column == 6:
                    self.shouldGetPeers = True

                if self.column == 7:
                    self.shouldGetPeers = False
                    self.shouldGetSeeds = False
                    self.shouldGetLeechs = False

                return                

            if self.insideCell and self.column == 2 and tag == self.B:
                self.shouldGetName = True
                return

            if self.insideCell and self.column == 2 and tag == self.A:
                href = params.get('href')
                link = f'{self.url}/{href}'
                self.row['desc_link'] = link
                return

            if self.insideCell and self.column == 3 and tag == self.A and self.shouldParseLink:
                self.shouldParseLink = False
                href = params.get('href')
                link = f'{self.url}/{href}&ok='
                self.row['link'] = link
                return

            if self.column == 6 and tag == self.B and self.shouldGetSeeds:
                if not self.shouldGetSeeds:
                    self.shouldGetLeechs = True
                return    

        def handle_data(self, data):
            if self.shouldGetName:
                self.row['name'] = data
                self.shouldGetName = False

            if self.shouldGetSize:
                self.row['size'] = data.replace(',', '.')
                self.shouldGetSize = False

            if self.shouldGetPeers:
                if "|" in data:
                    peers = data.strip().split("|")
                    if len(peers[1]) > 0:
                        self.row['seeds']  = peers[0] if peers[0].isnumeric() else -1
                        self.row['leech']  = peers[1] if peers[1].isnumeric() else -1
                    else:
                        self.row['seeds']  = peers[0] if peers[0].isnumeric() else -1
                        self.shouldGetLeechs = True
                else:
                    self.row['seeds']  = data if data.isnumeric() else -1
                    self.row['leech']  = -1
                    self.shouldGetLeechs = True
                self.shouldGetPeers = False                    
                return

            if self.shouldGetSeeds:    
                self.row['seeds']  = data if data.isnumeric() else -1
                self.shouldGetSeeds = False

            if self.shouldGetLeechs:    
                if not data == '|':
                    self.row['leech']  = data if data.isnumeric() else -1
                    self.shouldGetLeechs = False                

        def handle_endtag(self, tag):
            if self.insideCell and tag == self.TD:
                self.insideCell = False

            if self.insideRow and tag == self.TR:
                self.row['engine_url'] = self.url
                prettyPrinter(self.row)
                self.column = 0
                self.row = {}
                self.insideRow = False
                self.shouldParseLink = True

            if self.insideResultTbody and tag == self.TBODY:
                self.insideResultTbody = False

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        page = 1

        page_url = f'{self.url}/browse.php?search={what}&page={page}'
        retrievedHtml = retrieve_url(page_url)
        pagination_matches = re.finditer(self.pagination_regex, retrievedHtml, re.MULTILINE)
        pagination_pages = [x.group() for x in pagination_matches]
        if len(pagination_pages) > 0:
            lastPage = int(pagination_pages[0].replace('<div class="paginator_pages">', '').replace('</div>', '').split(' ')[3])
        else:
            lastPage = 0
        page += 1

        if lastPage > 0:
            parser.feed(retrievedHtml)

            while page <= lastPage:
                page_url = f'{self.url}/browse.php?search={what}&page={page}'
                retrievedHtml = retrieve_url(page_url)
                parser.feed(retrievedHtml)
                page += 1   
        parser.close()
