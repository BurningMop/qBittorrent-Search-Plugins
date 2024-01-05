# VERSION: 1.02
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
import json
import time
import threading
import urllib.request
from html.parser import HTMLParser

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter


class mypornclub(object):
    url = "https://myporn.club"
    name = "MyPorn Club"
    supported_categories = {"all": "all"}

    pagination_regex = r"<div>Page\s\d\sof\s\d+</div>"

    class MyHtmlParser(HTMLParser):
        def error(self, message):
            pass

        DIV, A, SPAN, I, B = ("div", "a", "span", "i", "b")

        def __init__(self, url):
            HTMLParser.__init__(self)
            self.url = url
            self.row = {}
            self.rows = []

            self.foundResults = False
            self.insideRow = False
            self.insideTorrentData = False
            self.insideTorrentName = False
            self.insideMetaData = False
            self.insideLabelCell = False
            self.insideSizeCell = False
            self.insideSeedCell = False
            self.insideLeechCell = False
            self.shouldAddBrackets = False
            self.shouldAddName = False
            self.web_seed = False
            self.magnet_regex = r'href=["\']magnet:.+?["\']'
            self.has_web_regex = (
                r"(//sxyprn.com/post/[\da-f]*\.html)[^>]*[>]\[[lL][iI][Nn][Kk][Ss]\s*\+"
            )

        def check_for_web_seed(self, web_page_url):
            id = web_page_url.split("/")[-1].split(".")[0]
            page = retrieve_url(web_page_url)
            match = re.search(r'data-vnfo=(["\'])(?P<data>{.+?})\1', page)
            if match:
                num = 0
                data1 = json.loads(match.group("data"))
                parts = data1[id].split("/")
                for c in parts[6] + parts[7]:
                    if c.isnumeric():
                        num += int(c)

                parts[5] = str(int(parts[5]) - num)
                parts[1] += "8"
                first_url = "https://sxyprn.com" + "/".join(parts)
                final_url = first_url
                user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"
                headers = {"User-Agent": user_agent}
                req = urllib.request.Request(url=first_url, headers=headers)
                with urllib.request.urlopen(req) as rf:
                    final_url = rf.url

                return "&ws=" + final_url
            else:
                return None

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get("class", "")
            if "torrents_list" in cssClasses:
                self.foundResults = True
                return

            if (
                self.foundResults
                and "torrent_element" in cssClasses
                and tag == self.DIV
            ):
                self.insideRow = True
                if (
                    self.insideRow
                    and "torrent_element_text_div" in cssClasses
                    and tag == self.DIV
                ):
                    self.insideTorrentData = True

                if (
                    self.insideRow
                    and "torrent_element_info" in cssClasses
                    and tag == self.DIV
                ):
                    self.insideMetaData = True
                return

            if (
                self.insideTorrentData
                and "torrent_element_text_span" in cssClasses
                and tag == self.SPAN
            ):
                self.row["name"] = ""
                self.insideTorrentName = True
                self.shouldAddName = True

            if self.insideTorrentName and tag == self.B:
                self.shouldAddBrackets = True

            if self.insideTorrentName and tag == self.I:
                self.shouldAddBrackets = False
                self.shouldAddName = False

            if (
                self.insideTorrentData
                and tag == self.A
                and "uploader_tel" not in cssClasses
            ):
                href = params.get("href")
                link = f"{self.url}{href}"
                self.row["desc_link"] = link
                torrent_page = retrieve_url(link)
                matches = re.finditer(self.magnet_regex, torrent_page, re.MULTILINE)
                magnet_urls = [x.group() for x in matches]
                self.row["link"] = magnet_urls[0].replace("'", '"').split('"')[1]

                _has_page = re.finditer(self.has_web_regex, torrent_page, re.MULTILINE)
                has_page = ["https:" + x.group(1) for x in _has_page]
                if has_page:
                    self.web_seed = self.check_for_web_seed(has_page[0])
                    if self.web_seed:
                        self.row["link"] = self.row["link"] + self.web_seed

                return

            if self.insideMetaData and "teis" in cssClasses:
                self.insideLabelCell = True

        def handle_data(self, data):
            if self.insideRow:
                if self.insideTorrentData and self.insideTorrentName:
                    if self.shouldAddBrackets:
                        self.row["name"] += f"[{data}]".strip()
                        self.shouldAddBrackets = False
                        return
                    if self.shouldAddName:
                        self.row["name"] += f" {data}".strip()
                        return

                if self.insideMetaData:
                    if self.insideSizeCell:
                        size = data.replace(",", ".")
                        self.row["size"] = size
                        self.insideSizeCell = False
                        self.insideLabelCell = False

                    if self.insideSeedCell:
                        self.row["seeds"] = data
                        self.insideSeedCell = False
                        self.insideLabelCell = False

                    if self.insideLeechCell:
                        self.row["leech"] = data
                        self.insideLeechCell = False
                        self.insideLabelCell = False

                    if self.insideLabelCell:
                        if data == "[size]:":
                            self.insideSizeCell = True
                        if data == "[seeders]:":
                            self.insideSeedCell = True
                        if data == "[leechers]:":
                            self.insideLeechCell = True

        def handle_endtag(self, tag):
            if self.insideRow and tag == self.DIV:
                if self.insideTorrentData and tag == self.DIV:
                    self.insideTorrentData = False
                    self.insideTorrentName = False
                    return

                if self.insideMetaData and tag == self.DIV:
                    self.insideMetaData = False
                    return

                self.row["engine_url"] = self.url

                if self.web_seed:
                    self.row["name"] = "💥 " + self.row["name"]

                prettyPrinter(self.row)
                self.row = {}
                self.insideRow = False

    def download_torrent(self, info):
        print(download_file(info))

    def do_search(self, page, what):
        parser = self.MyHtmlParser(self.url)
        page_url = f"{self.url}/s/{what}/seeders/{page}"
        retrievedHtml = retrieve_url(page_url)
        parser.feed(retrievedHtml)
        parser.close()

    def search(self, what, cat="all"):
        parser = self.MyHtmlParser(self.url)
        what = what.replace("%20", "-")
        what = what.replace(" ", "-")
        page = 1

        page_url = f"{self.url}/s/{what}/seeders/{page}"
        retrievedHtml = retrieve_url(page_url)
        pagination_matches = re.finditer(
            self.pagination_regex, retrievedHtml, re.MULTILINE
        )
        pagination_pages = [x.group() for x in pagination_matches]
        lastPage = int(
            pagination_pages[0]
            .replace("<div>", "")
            .replace("</div>", "")
            .split(" ")[-1]
        )
        page += 1
        parser.feed(retrievedHtml)
        parser.close()

        threads = []
        while page <= lastPage:
            t = threading.Thread(args=(page, what), target=self.do_search)
            t.start()
            time.sleep(0.5)
            threads.append(t)
            page += 1

        for t in threads:
            t.join()
