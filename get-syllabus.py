#!/bin/python3
import sys
import os
from selenium.webdriver import Chrome, ChromeOptions


class SyllabusGetter():
    def __init__(self, username: str, password: str, socks_proxy_port: int = 1080) -> None:
        self.username = username
        self.password = password

        options = ChromeOptions()
        options.add_argument(f'--proxy-server=socks5://localhost:{socks_proxy_port}')

        self.chrome = Chrome(options=options)
        self.chrome.get('https://campusweb.office.uec.ac.jp/campusweb/')
        self.chrome.find_element_by_id('username').send_keys(username)
        self.chrome.find_element_by_id('password').send_keys(password)
        self.chrome.find_element_by_name('_eventId_proceed').click()

    def get_syllabus(self, subject_num: str):
        self.chrome.get('https://campusweb.office.uec.ac.jp/campusweb/campussquare.do?_flowId=SYW0001000-flow')
        self.chrome.find_element_by_id('jikanwaricd').send_keys(subject_num)
        self.chrome.find_element_by_css_selector('#jikanwariInputForm input[type=button]').click()
        return self.chrome.execute_script('return document.body.innerHTML;')

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.chrome.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser('syllabus getter cli')
    parser.add_argument('subject_nums', nargs='+')
    args = parser.parse_args()

    username, password = os.getenv('UEC_USERNAME'), os.getenv('UEC_PASSWORD')
    if not username or not password:
        print('Error: environmental valiable `UEC_USERNAME` or `UEC_PASSWORD` is not set', file=sys.stderr)
        exit(1)

    with SyllabusGetter(username, password) as sg:
        for subject_num in args.subject_nums:
            html = sg.get_syllabus(subject_num)
            path = f'{subject_num}.html'
            with open(path, 'wt', encoding='utf-8') as f:
                f.write(html)
