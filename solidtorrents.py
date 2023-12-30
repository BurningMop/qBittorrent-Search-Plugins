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

import math
import re
from html.parser import HTMLParser

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes


class solidtorrents(object):
    url = 'https://solidtorrents.to'
    name = 'Solid Torrents'
    supported_categories = {
        'all': 'all'
    }
    
    results_regex = r'<b>\d+<\/b>'

    class MyHtmlParser(HTMLParser):
    
        def error(self, message):
            pass
    
        LI, DIV, H5, A = ('li', 'div', 'h5', 'a')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.magnet_regex = r'href=["\']magnet:.+?["\']'

            self.url = url
            self.row = {}

            self.column = 0

            self.insideSearchResult = False
            self.insideInfoDiv = False
            self.insideName = False
            self.shouldGetName = False
            self.insideStatsDiv = False
            self.insideStatsColumn = False
            self.insideLinksDiv = False
    
        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')
            elementId = params.get('id', '')

            if tag == self.LI and 'search-result' in cssClasses:
                self.insideSearchResult = True
                return

            if self.insideSearchResult and tag == self.DIV and 'info' in cssClasses:
                self.insideInfoDiv = True
                return

            if self.insideInfoDiv and tag == self.H5:
                self.insideName = True
                return

            if self.insideName and tag == self.A:
                self.shouldGetName = True
                href = params.get('href')
                link = f'{self.url}{href}'
                self.row['desc_link'] = link
                return

            if self.insideSearchResult and tag == self.DIV and 'stats' in cssClasses:
                self.insideStatsDiv = True
                return

            if self.insideStatsDiv and tag == self.DIV:
                self.insideStatsColumn = True
                self.column += 1
                return

            if self.insideSearchResult and tag == self.DIV and 'links' in cssClasses:
                self.insideLinksDiv = True
                return

            if self.insideLinksDiv and tag == self.A and 'dl-magnet' in cssClasses:
                href = params.get('href')
                self.row['link'] = href
                self.insideLinksDiv = False
                return                

        def handle_data(self, data):
            if self.shouldGetName:
                self.row['name'] = data.strip()
                self.shouldGetName = False
                return

            if self.insideStatsDiv:
                if not data.rstrip() == '':                  
                    if self.column == 2:
                        self.row['size'] = data.replace(' ', '')
                    if self.column == 3: 
                        self.row['seeds'] = data
                    if self.column == 4: 
                        self.row['leech'] = data
                return

        def handle_endtag(self, tag):
            if tag == self.H5 and self.insideName:
                self.insideName = False
                return

            if self.insideStatsDiv and not self.insideStatsColumn:
                self.insideStatsDiv = False
                self.insideInfoDiv = False
                return

            if self.insideStatsColumn and tag == self.DIV:
                self.insideStatsColumn = False
                return

            if tag == self.LI and self.insideSearchResult:
                self.row['engine_url'] = self.url
                print(self.row)
                prettyPrinter(self.row)
                self.insideSearchResult = False
                self.column = 0
                return

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        page = 1

        page_url = f'{self.url}/search?q={what}&page={page}'
        retrievedHtml = retrieve_url(page_url)
        results_matches = re.finditer(self.results_regex, retrievedHtml, re.MULTILINE)
        results_array = [x.group() for x in results_matches]
 
        if len(results_array) > 0:
            results = int(results_array[0].replace('<b>', '').replace('</b>', ''))
            pages = math.ceil(results / 20)
        else:
            pages = 0

        page += 1

        if pages > 0:
            parser.feed(retrievedHtml)

            while page <= pages:
                page_url = f'{self.url}/search?q={what}&page={page}'
                retrievedHtml = retrieve_url(page_url)
                parser.feed(retrievedHtml)
                page += 1
        parser.close()
