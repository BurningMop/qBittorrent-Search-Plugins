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

class calidadtorrent(object):
    url = 'https://calidadtorrent.com'
    headers = {
        'Referer': url
    }
    name = 'CalidadTorrent'
    supported_categories = {
        'all': 'all'
    }

    no_results_regex = r'<p.*?>No se ha encontrado ning[uú]n resultado.</p>'

    class SearchResultsParser(HTMLParser):
        def error(self, message):
            pass

        DIV, A = ('div', 'a')

        expected_x_data = "{ showDetail: true }"
        torrent_link_regex = r'\/torrents\/.+?\.torrent'
        title_regex = r'<h1.*?>.*?</h1>'

        count = 0

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.headers = {
                'Referer': url
            }

            self.insideResultList = False
            self.insideResultContainer = False
            self.insideResult = False
            self.insideLink = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            css_classes = params.get('class', '')
            x_data = params.get('x-data')

            if tag == self.DIV and 'result-list' in css_classes:
                self.insideResultList = True
                return

            if self.insideResultList and tag == self.DIV and x_data == self.expected_x_data:
                self.insideResultContainer = True
                return

            if self.insideResultContainer and tag == self.DIV and 'relative' in css_classes:
                self.insideResult = True
                return

            if self.insideResult and tag == self.A:
                self.count += 1
                self.insideLink = True
                href = params.get('href')
                retrieved_html = retrieve_url(href, self.headers)

                link_matches = re.finditer(self.torrent_link_regex, retrieved_html, re.MULTILINE)
                title_matches = re.finditer(self.title_regex, retrieved_html, re.MULTILINE)

                torrent_link = [x.group() for x in link_matches]
                title = [x.group() for x in title_matches]

                row = {
                    'link': f'{calidadtorrent.url}{torrent_link[0]}',
                    'name': re.sub(r'</h1>', '',re.sub(r'<h1.+?>', '', title[0])),
                    'size': 0,
                    'seeds': -1,
                    'leech': -1,
                    'engine_url': calidadtorrent.url,
                    'desc_link': href
                }
                prettyPrinter(row)
                return

        def handle_endtag(self, tag):
            if self.insideLink and tag == self.A:
                self.insideLink = False
                return

            if not self.insideLink and self.insideResult and tag == self.DIV:
                self.insideResult = False
                return

            if not self.insideResult and self.insideResultContainer and tag == self.DIV:
                self.insideResultContainer = False
                return

            if not self.insideResultContainer and self.insideResultList and tag == self.DIV:
                self.insideResultList = False
                return

    def download_torrent(self, info):
        print(download_file(info))

    def get_search_url(self, what, page):
        return f'{self.url}/buscar/page/{page}?q={what}'

    def has_results(self, html):
        no_results_matches = re.finditer(self.no_results_regex, html, re.MULTILINE)
        no_results = [x.group() for x in no_results_matches]
        return len(no_results) == 0

    def search(self, what, cat):
        should_continue = True
        what = what.replace('%20', '+')
        page = 1

        while should_continue:
            retrieved_html = retrieve_url(self.get_search_url(what,page), self.headers)

            if self.has_results(retrieved_html):
                parser = self.SearchResultsParser(self.url)
                parser.feed(retrieved_html)
                parser.close()

                page += 1
            else:
                should_continue = False
