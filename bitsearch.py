# VERSION: 1.3_FIXED
# AUTHORS: BurningMop (burning.mop@yandex.com)

import math
import re
import time
import socket
from datetime import datetime
from html.parser import HTMLParser

# enforce a strict 15 second timout throughout.
socket.setdefaulttimeout(15)

from helpers import download_file, retrieve_url
from novaprinter import prettyPrinter

class bitsearch(object):
    url = 'https://bitsearch.to'
    name = 'Bit Search'
    supported_categories = {
        'all': 'all'
    }

    results_regex = r'Found\s+<span.+>\d+<\/span>'

    class MyHtmlParser(HTMLParser):

        def error(self, message):
            pass

        MAIN, DIV, SPAN, A = ('main', 'div', 'span', 'a')

        search_results_main_class_name = 'mx-auto'
        search_results_list_class_name = 'space-y-4'
        search_results_item_container_class_name = 'bg-white'
        search_results_item_class_name = 'items-start'
        search_results_torrent_info_class_name = 'flex-1'
        search_results_item_metadata_class_name = 'items-center'
        search_results_item_metadata_numbers_class_name = 'font-medium'
        search_results_item_download_class_name = 'space-y-2'
        search_results_item_mobile_download_class_name = 'sm:hidden'

        def __init__(self, url):
            HTMLParser.__init__(self)

            self.url = url
            self.row = {}

            self.column = 0
            self.metadata = 0
            self.results = 0

            self.insideMain = False
            self.insideSearchResultList = False
            self.insideSearchResultItemContainer = False
            self.insideSearchResultItem = False
            self.insideTorrentInfo = False
            self.insideName = False
            self.insideStats = False
            self.insideSwarm = False
            self.insideDownload = False
            self.insideMobileDownload = False
            self.shouldGetName = False
            self.shouldGetData = False

            self.cssClasses = []

        def handle_starttag(self, tag, attrs):
            params = dict(attrs)
            cssClasses = params.get('class', '')

            if tag == self.MAIN and self.search_results_main_class_name in cssClasses:
                self.insideMain = True
                return

            if self.insideMain and tag == self.DIV and self.search_results_list_class_name in cssClasses:
                self.insideSearchResultList = True
                return

            if self.insideSearchResultList and tag == self.DIV and self.search_results_item_container_class_name in cssClasses:
                self.insideSearchResultItemContainer = True
                self.row = {}  # clear memory/data upon entering
                return

            if self.insideSearchResultItemContainer and tag == self.DIV and self.search_results_item_class_name in cssClasses:
                self.insideSearchResultItem = True
                return

            if self.insideSearchResultItem and tag == self.DIV and self.search_results_torrent_info_class_name in cssClasses:
                self.insideTorrentInfo = True
                return

            if self.insideSearchResultItem and tag == self.DIV and self.search_results_item_metadata_class_name in cssClasses:
                if self.metadata == 0:
                    self.insideName = True
                    self.metadata = 1
                    return
                if self.metadata == 1:
                    self.insideName = False
                    self.insideStats = True
                    self.column = 0
                    self.metadata = 2
                    return
                if self.metadata == 2:
                    self.insideStats = False
                    self.insideSwarm = True
                    self.column = 0
                    self.metadata = 3
                    return

            if self.insideName and tag == self.A:
                self.shouldGetName = True
                href = params.get('href')
                link = f'{self.url}{href}'
                self.row['desc_link'] = link
                return

            if self.insideStats and tag == self.SPAN and len(cssClasses) == 0:
                self.column += 1
                self.shouldGetData = True
                return

            if self.insideSwarm and tag == self.SPAN and self.search_results_item_metadata_numbers_class_name in cssClasses:
                self.column += 1
                self.shouldGetData = True
                return

            if self.insideSearchResultItem and tag == self.DIV and self.search_results_item_download_class_name in cssClasses:
                self.insideDownload = True
                return

            if self.insideSearchResultItemContainer and tag == self.DIV and self.search_results_item_mobile_download_class_name in cssClasses:
                self.insideMobileDownload = True
                return

            if self.insideDownload and tag == self.A:
                href = params.get('href')
                if href.startswith('magnet'):
                    self.row['link'] = href
                return

        def handle_data(self, data):
            if self.shouldGetName:
                self.row['name'] = data.strip()
                self.shouldGetName = False
                return

            if self.insideStats and self.shouldGetData:
                if self.column == 2:
                    self.row['size'] = data.replace(' ', '')
                    self.shouldGetData = False
                    return
                if self.column == 3:
                    try:
                        self.row['pub_date'] = int(datetime.strptime(data.strip(), "%m/%d/%Y").timestamp())
                    except:
                        self.row['pub_date'] = int(time.time())
                    self.shouldGetData = False
                    return

            if self.insideSwarm and self.shouldGetData:
                if self.column == 1:
                    self.row['seeds'] = data
                    self.shouldGetData = False
                    return
                if self.column == 2:
                    self.row['leech'] = data
                    self.shouldGetData = False
                    return

        def handle_endtag(self, tag):
            if self.insideSwarm and tag == self.DIV:
                self.insideSwarm = False
                self.column = 0
                self.metadata = 0
                return

            if self.insideTorrentInfo and tag == self.DIV and not self.insideName and not self.insideStats and not self.insideSwarm:
                self.insideTorrentInfo = False
                return

            if self.insideDownload and tag == self.DIV:
                self.insideDownload = False
                return

            if self.insideMobileDownload and tag == self.DIV:
                self.insideMobileDownload = False
                return

            if (tag == self.DIV
                    and not self.insideDownload
                    and not self.insideTorrentInfo
                    and not self.insideMobileDownload
                    and self.insideSearchResultItem):
                self.insideSearchResultItem = False
                return

            if tag == self.DIV and not self.insideSearchResultItem and self.insideSearchResultItemContainer:
                self.insideSearchResultItemContainer = False
                self.row['engine_url'] = self.url
                if 'name' in self.row and 'link' in self.row:
                    prettyPrinter(self.row)
                self.row = {}  # final dictionary clearing to avoid memory leaks
                self.column = 0
                self.metadata = 0
                return

            if tag == self.DIV and not self.insideSearchResultItem and self.insideSearchResultList:
                self.insideSearchResultList = False
                return

            if tag == self.MAIN and self.insideMain:
                self.insideMain = False
                return

    def download_torrent(self, info):
        print(download_file(info))

    def search(self, what, cat='all'):
        parser = self.MyHtmlParser(self.url)
        what = what.replace('%20', '+')
        what = what.replace(' ', '+')
        page = 1

        try:
            page_url = f'{self.url}/search?q={what}&page={page}'
            retrievedHtml = retrieve_url(page_url)
            if not retrievedHtml:
                return
        except:
            return

        results_matches = re.finditer(self.results_regex, retrievedHtml, re.MULTILINE)
        results_array = [x.group() for x in results_matches]

        if len(results_array) > 0:
            results = int(re.search(r'\d+', results_array[0]).group(0))
            pages = math.ceil(results / 20)
        else:
            pages = 0

        page += 1

        if pages > 0:
            parser.feed(retrievedHtml)

            while page <= min(pages, 10):
                page_url = f'{self.url}/search?q={what}&page={page}'

                try:
                    retrievedHtml = retrieve_url(page_url)
                    if not retrievedHtml:
                        break  # stop if page returns empty
                    parser.feed(retrievedHtml)
                except:
                    break  # immediate exit on network error
                page += 1
                time.sleep(0.75)
        parser.close()
