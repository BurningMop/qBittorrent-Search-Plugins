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

class pornrips(object):
    url = "https://pornrips.to"
    name = "PornRips.To"
    supported_categories = {"all": "all"}

    next_page_regex = r"next page-numbers"
    pagination_regex = r"posts-pagination-wrapper wrapper-with-padding"
    nothing_found_regex = r"Nothing Found"

    class MyHtmlParser(HTMLParser):
        def error(self, message):
            pass

        SEC, ART, HEA, H2, A, DIV, P, STRONG = ("section", "article", "header", "h2", "a", "div", "p", "strong")

        def __init__(self, url, referer):
            HTMLParser.__init__(self)

            self.headers = {
                'Referer': referer
            }

            self.url = url
            self.row = {}
            self.rows = []

            self.insideResults = False
            self.insideResult = False
            self.insideWrapper = False
            self.insideHeader = False
            self.insideTitle = False
            self.insideMetadata = False

            self.shouldParseName = False
            self.shouldSkipTorrent = False

            self.wrapperExcerptContentClass = "wrapper-excerpt-content"

            self.torrent_regex = r'https:\/\/.+?\.torrent'
            self.size_regex = r'\d+ [MB|MiB]'

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get("class", "")
            elementId = params.get("id", "")

            if tag == self.SEC and elementId == "primary":
                self.insideResults = True
                return

            if tag == self.ART and self.insideResults:
                self.insideResult = True
                return

            if tag == self.DIV and self.wrapperExcerptContentClass in cssClasses and self.insideResult:
                self.insideWrapper = True
                return

            if tag == self.HEA and self.insideWrapper:
                self.insideHeader = True
                return

            if tag == self.H2 and self.insideHeader:
                self.insideTitle = True
                return

            if tag == self.A and self.insideTitle:
                self.shouldParseName = True
                href = params.get('href')
                self.row['desc_link'] = href

                torrent_page = retrieve_url(href, self.headers)
                matches = re.finditer(self.torrent_regex, torrent_page, re.MULTILINE)
                torrent_urls = [x.group() for x in matches]
                if(len(torrent_urls) > 0):
                    self.row['link'] = torrent_urls[0]
                else:
                    self.shouldSkipTorrent = True
                return

            if tag == self.P and self.insideWrapper:
                self.insideMetadata = True
                return

        def handle_data(self, data):
            if self.shouldParseName:
                self.row['name'] = data
                self.shouldParseName = False
                return

            if self.insideMetadata:
                size_matches = re.finditer(self.size_regex, data, re.MULTILINE)
                size = [x.group() for x in size_matches]
                if len(size) > 0:
                    self.row['size'] = size[0]
                return

        def handle_endtag(self, tag):
            if tag == self.A and self.shouldParseName:
                self.shouldParseName = False
                return

            if tag == self.H2 and self.insideTitle:
                self.insideTitle = False
                return

            if tag == self.HEA and self.insideHeader:
                self.insideHeader = False
                return

            if tag == self.P and self.insideMetadata:
                self.insideMetadata = False
                return

            if tag == self.ART and self.insideResult:
                self.row['seeds'] = -1
                self.row['leech'] = -1
                self.row['engine_url'] = self.url
                self.insideResult = True

                if not self.shouldSkipTorrent:
                    prettyPrinter(self.row)

                self.insideResult = False
                self.insideWrapper = False
                self.insideHeader = False
                self.insideTitle = False
                self.insideMetadata = False

                self.shouldParseName = False
                self.shouldSkipTorrent = False
                return

            if tag == self.SEC and self.insideResults:
                self.insideResults = False
                return

    def download_torrent(self, info):
        return
        # print(download_file(info))

    def get_page_url(self, page, what):
        return f"{self.url}/page/{page}/?s={what}"

    def search(self, what, cat="all"):
        what = what.replace("%20", "+")
        page = 1

        retrieved_html = retrieve_url(self.get_page_url(page, what))

        has_results = (len([x.group() for x in re.finditer(
            self.nothing_found_regex, retrieved_html, re.MULTILINE
        )]) == 0)

        if has_results:
            parser = self.MyHtmlParser(self.url, self.get_page_url(page, what))
            parser.feed(retrieved_html)
            parser.close()

            has_next_page = len([x.group() for x in re.finditer(
                self.next_page_regex, retrieved_html, re.MULTILINE
            )]) > 0

            while has_next_page:
                page += 1

                retrieved_html = retrieve_url(self.get_page_url(page, what))

                parser.feed(retrieved_html)
                parser = self.MyHtmlParser(self.url, self.get_page_url(page, what))
                parser.close()

                has_next_page = len([x.group() for x in re.finditer(
                    self.next_page_regex, retrieved_html, re.MULTILINE
                )]) > 0


