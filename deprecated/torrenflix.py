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

from html.parser import HTMLParser
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes
class torrenflix(object):
    url = 'https://www.torrenflix.com/'
    headers = {
        'Referer': url
    }
    name = 'Torrentflix'
    supported_categories = {
        'all': 'all'
    }

    class SearchResultData:
        torrents = {}

        def __init__(self):
            self.name = ''
            self.desc_link = ''

        def set_name(self, name):
            self.name = name

        def set_desc_link(self, link):
            self.desc_link = link

        def add_torrent_link(self, server, language, quality, link):
            self.torrents["|".join(filter(None, (server, language, quality)))] = link

        def print_rows(self):
            for key in sorted(self.torrents.keys()):
                row = {
                    'link': self.torrents[key],
                    'name': f'{self.name} [{key}]',
                    'size': 0,
                    'seeds': -1,
                    'leech': -1,
                    'engine_url': 'https://www.torrenflix.com/',
                    'desc_link': self.desc_link
                }
                prettyPrinter(row)
            self.torrents = {}
            self.name = ''
            self.desc_link = ''

    class TorrentPageParser(HTMLParser):
        DIV, TABLE, TBODY, TR, TD, SPAN, A = ('div', 'table', 'tbody', 'tr', 'td', 'span', 'a')

        insideDownloadLinks = False
        insideTable = False
        insideTbody = False
        insideRow = False
        insideColumn = False
        shouldParseData = True
        columnNumber = 0
        server = ''
        quality = ''
        language = ''
        torrent_link = ''

        def error(self, message):
            pass

        def __init__(self, search_result):
            HTMLParser.__init__(self)
            self.search_result = search_result
            self.init_values()

        def init_values(self):
            self.insideDownloadLinks = False
            self.insideTable = False
            self.insideTbody = False
            self.insideRow = False
            self.insideColumn = False
            self.shouldParseData = True
            self.columnNumber = 0
            self.server = ''
            self.quality = ''
            self.language = ''
            self.torrent_link = ''

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            css_classes = params.get('class', '')

            if tag == self.DIV and 'download-links' in css_classes:
                self.insideDownloadLinks = True
                return

            if self.insideDownloadLinks and tag == self.TABLE:
                self.insideTable = True
                return

            if self.insideTable and tag == self.TBODY:
                self.insideTbody = True
                return

            if self.insideTbody and tag == self.TR:
                self.insideRow = True
                return

            if self.insideRow and tag == self.TD:
                self.insideColumn = True
                self.columnNumber += 1
                return

            if self.insideColumn and self.columnNumber == 1 and tag == self.SPAN:
                self.shouldParseData = False
                return

            if self.insideColumn and self.columnNumber == 4 and tag == self.A:
                self.torrent_link = params.get('href')
                return

        def handle_data(self, data):
            if self.insideColumn:
                if self.columnNumber == 1 and self.shouldParseData:
                    self.server = data.strip()
                if self.columnNumber == 2:
                    self.language = data.strip()
                if self.columnNumber == 3:
                    self.quality = data.strip()
                return

        def handle_endtag(self, tag):
            if self.insideColumn and tag == self.SPAN:
                if self.columnNumber == 1:
                    self.shouldParseData = True
                return

            if self.insideColumn and tag == self.TD:
                self.insideColumn = False
                if self.columnNumber == 1:
                    self.shouldParseData = True
                return

            if self.insideRow and tag == self.TR:
                self.search_result.add_torrent_link(self.server, self.language, self.quality, self.torrent_link)
                self.insideRow = False
                self.columnNumber = 0
                self.tags = ''
                self.server = ''
                self.torrent_link = ''
                return

            if self.insideTbody and tag == self.TBODY:
                self.insideTbody = False
                return

            if self.insideTable and tag == self.TABLE:
                self.insideTable = False
                return

            if self.insideDownloadLinks and tag == self.DIV:
                self.init_values()
                return

    class MyHtmlParser(HTMLParser):
        def error(self, message):
            pass
    
        MAIN, UL, LI, H, A = ('main', 'ul', 'li', 'h2', 'a')
    
        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.headers = {
                'Referer': url
            }

            self.rows = torrenflix.SearchResultData()
            self.insideMain = False
            self.insidePostList = False
            self.insidePost = False
            self.shouldGetTitle = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            css_classes = params.get('class', '')

            if tag == self.MAIN:
                self.insideMain = True
                return

            if self.insideMain and tag == self.UL and 'post-lst' in css_classes:
                self.insidePostList = True
                return

            if self.insidePostList and tag == self.LI:
                self.insidePost = True
                return

            if self.insidePost and tag == self.H:
                self.shouldGetTitle = True
                return

            if self.insidePost and tag == self.A and 'lnk-blk' in css_classes:
                self.rows.set_desc_link(params.get('href'))
                return

        def handle_data(self, data):
            if self.shouldGetTitle:
                self.rows.set_name(data)
                return

        def handle_endtag(self, tag):
            if self.shouldGetTitle and tag == self.H:
                self.shouldGetTitle = False
                return

            if self.insidePost and tag == self.LI:
                self.insidePost = False
                details_html = retrieve_url(self.rows.desc_link, self.headers)
                parser = torrenflix.TorrentPageParser(self.rows)
                parser.feed(details_html)
                parser.close()

                self.rows.print_rows()
                return

            if self.insidePostList and tag == self.UL:
                self.insidePostList = False
                return

            if self.insideMain and tag == self.MAIN:
                self.insideMain = False
                return

    def download_torrent(self, info):
        print(download_file(info))

    def get_page_url(self, what):
        return f'{self.url}?s={what}'

    def search(self, what, cat='all'):
        what = what.replace('%20', '+')
        retrieved_html = retrieve_url(self.get_page_url(what), self.headers)
        parser = self.MyHtmlParser(self.url)
        parser.feed(retrieved_html)
        parser.close()