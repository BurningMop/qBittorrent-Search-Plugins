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
import xml.etree.ElementTree as ET

from html.parser import HTMLParser
import time
import threading
from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter, anySizeToBytes


class esmeraldatorrent(object):
    url = 'https://esmeraldatorrent.com/'
    headers = {
        'Referer': url
    }
    name = 'EsmeraldaTorrent'
    supported_categories = {
        'all': 'all'
    }
    
    results_regex = r'<p.+?>Se han encontrado.+?<b>\d+</b>.+?resultados.+?</p>'

    class MyHtmlParser(HTMLParser):
        magnet_regex = r'href=["\'].+?\.torrent["\']'
        size_regex = r'<p.+?><b.+?>Tamaño:</b>.+?</p>'

        def error(self, message):
            pass
    
        DIV, P, A, SPAN = ('div', 'p', 'a', 'span')
    
        def __init__(self, url):
            HTMLParser.__init__(self)

            self.url = url
            self.headers = {
                'Referer': url
            }
            self.row = {}

            self.column = 0

            self.insideBuscadorDiv = False
            self.insideCardDiv = False
            self.insideCardBodyDiv = False
            self.insideResult = False
            self.insideResultSpan = False
            self.insideLink = False
            self.insideType = False
            self.insideBadge = False

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')
            elementId = params.get('id', '')

            if tag == self.DIV and elementId == 'buscador':
                self.insideBuscadorDiv = True
                return

            if self.insideBuscadorDiv and 'card' in cssClasses and 'card-body' not in cssClasses:
                self.insideCardDiv = True
                return

            if self.insideCardDiv and 'card-body' in cssClasses:
                self.insideCardBodyDiv = True
                return

            if self.insideCardBodyDiv and tag == self.P and len(cssClasses) == 0:
                self.insideResult = True
                return

            if self.insideResult and not self.insideResultSpan and tag == self.SPAN:
                self.insideResultSpan = True
                return

            if self.insideResultSpan and tag == self.A:
                self.insideLink = True
                href = params.get('href')
                link = f'{self.url}{href}'
                self.row['desc_link'] = link
                self.row['link'] = link
                torrent_page = retrieve_url(link, self.headers)
                matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                magnet_urls = [x.group() for x in matches]
                self.row['link'] = "https:" + magnet_urls[0].split("'")[1]
                matches = re.finditer(self.size_regex, torrent_page, re.MULTILINE)
                size = [x.group() for x in matches]
                sizeEl = re.sub(r'<b.+?>Tamaño:</b>', '', size[0])
                root = ET.fromstring(sizeEl)
                self.row['size'] = root.text.replace(',', '.')
                self.row['seeds'] = -1
                self.row['leech'] = -1
                return

            if self.insideResultSpan and tag == self.SPAN and len(cssClasses) == 0:
                self.insideType = True
                return

            if self.insideResultSpan and tag == self.SPAN and 'badge' in cssClasses:
                self.insideBadge = True
                return

        def handle_data(self, data):
            if self.insideLink:
                self.row['name'] = data
                return

            if self.insideType:
                self.row['name'] += f" ({data})"
                return

            if self.insideBadge:
                self.row['name'] += f" [{data}]"
                return

        def handle_endtag(self, tag):
            if self.insideBadge and tag == self.SPAN:
                self.insideBadge = False
                return

            if self.insideType and tag == self.SPAN:
                self.insideType = False
                return

            if self.insideLink and tag == self.A:
                self.insideLink = False
                return

            if self.insideResultSpan and not self.insideBadge and not self.insideType and tag == self.SPAN:
                self.insideResultSpan = False
                return

            if self.insideResult and tag == self.P:
                self.row['engine_url'] = self.url
                prettyPrinter(self.row)
                self.column = 0
                self.row = {}
                self.insideResult = False
                self.insideResultSpan = False
                return

            if self.insideCardBodyDiv and tag == self.DIV:
                self.insideCardBodyDiv = False
                return

            if self.insideCardDiv and self.insideCardBodyDiv is False and tag == self.DIV:
                self.insideCardDiv = False
                return

            if self.insideBuscadorDiv and self.insideCardDiv is False and tag == self.DIV:
                self.insideBuscadorDiv = False
                return

    def download_torrent(self, info):
        print(download_file(info))

    def get_page_url(self, what, page):
        return f'{self.url}/buscar/{what}/page/{page}'

    def threaded_search(self, page, what):
        page_url = self.get_page_url(what, page)
        self.headers['Referer'] = page_url
        retrieved_html = retrieve_url(page_url, self.headers)
        parser = self.MyHtmlParser(self.url)
        parser.feed(retrieved_html)
        parser.close()

    def search(self, what, cat='all'):
        page = 1
        retrieved_html = retrieve_url(self.get_page_url(what, page), self.headers)
        matches = re.finditer(self.results_regex, retrieved_html, re.MULTILINE)
        results_el = [x.group() for x in matches]
        root = ET.fromstring(results_el[0])
        results = root[0].text
        pages = math.ceil(int(results) / 10)

        parser = self.MyHtmlParser(self.url)
        parser.feed(retrieved_html)
        parser.close()

        page += 1

        threads = []
        while page <= pages:
            t = threading.Thread(args=(page, what), target=self.threaded_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)

            page += 1

        for t in threads:
            t.join()

