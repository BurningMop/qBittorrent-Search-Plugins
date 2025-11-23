from datetime import datetime

import codecs

def save_search_results(engine: str, page: int, html: str):
    now = datetime.today().strftime('%Y%m%d-%H%M%S')
    log_file_name = f'./log/{engine}.page-{page}.{now}.html'
    text_file = codecs.open(log_file_name, "w", "utf-8")
    text_file.write(html)
