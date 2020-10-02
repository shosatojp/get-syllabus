#!/bin/python3
import htmlmin
import sys
import os
from selenium.webdriver import Chrome, ChromeOptions
import shutil
import time


class SyllabusGetter():
    def __init__(self, username: str, password: str, socks_proxy_port: int = 1080) -> None:
        self.username = username
        self.password = password

        options = ChromeOptions()
        options.add_argument(f'--proxy-server=socks5://localhost:{socks_proxy_port}')
        options.add_experimental_option('prefs', {
            "download.default_directory": os.path.abspath('.'),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        })

        self.chrome = Chrome(options=options)
        self.chrome.get('https://campusweb.office.uec.ac.jp/campusweb/')
        self.chrome.find_element_by_id('username').send_keys(username)
        self.chrome.find_element_by_id('password').send_keys(password)
        self.chrome.find_element_by_name('_eventId_proceed').click()

    def get_syllabus(self, subject_num: str, pdf=False):
        self.chrome.get('https://campusweb.office.uec.ac.jp/campusweb/campussquare.do?_flowId=SYW0001000-flow')
        self.chrome.find_element_by_id('jikanwaricd').send_keys(subject_num)
        self.chrome.find_element_by_css_selector('#jikanwariInputForm input[type=button]').click()
        if pdf:
            self.chrome.find_element_by_css_selector('input[value="PDF出力"]').click()
            default_name = 'syllabusPdfList.pdf'
            if os.path.exists(default_name):
                os.remove(default_name)
            time.sleep(1)
            shutil.move(default_name, f'{subject_num}.pdf')
        html = self.chrome.execute_script('return document.body.innerHTML;')
        return htmlmin.minify(html, remove_empty_space=True)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.chrome.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser('syllabus getter cli')
    parser.add_argument('subject_nums', nargs='+')
    parser.add_argument('--pdf', action='store_true', default=False)
    parser.add_argument('--pattern', type=str, default='{NUM}.html')
    args = parser.parse_args()

    username, password = os.getenv('UEC_USERNAME'), os.getenv('UEC_PASSWORD')
    if not username or not password:
        print('Error: environmental valiable `UEC_USERNAME` or `UEC_PASSWORD` is not set', file=sys.stderr)
        exit(1)

    with SyllabusGetter(username, password) as sg:
        for subject_num in args.subject_nums:
            html = sg.get_syllabus(subject_num)
            path = args.pattern.replace('{NUM}',subject_num)
            with open(path, 'wt', encoding='utf-8') as f:
                f.write(html)
