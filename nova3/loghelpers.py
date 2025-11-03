from datetime import datetime


def save_search_results(engine: str, page: int, html: str):
    now = datetime.today().strftime('%Y%m%d-%H%M%S')
    log_file_name = f'./log/{engine}.page-{page}.{now}.html'
    with open(log_file_name, "w") as text_file:
        text_file.write(html)
