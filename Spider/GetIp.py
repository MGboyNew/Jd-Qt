import random
import re

import requests
from user_agent import generate_user_agent

# from Spider.utils import Util


class GetIP:
    def __init__(self):
        pass

    def get_user_agent(self):
        """获取一个请求头"""
        user_agent = ''
        while 'AppleWebKit' not in user_agent:
            user_agent = generate_user_agent()
        return user_agent

    def spider(self, url):
        response = requests.get(url=url, headers={'user-agent': self.get_user_agent()})
        if response.status_code != 200:
            raise RuntimeError()
        return response.text

    def parse_proxy_ips(self, page): 
        # 解析那个网页 使用正则的
        target_ele = None
        table_ele = re.compile(r'<table.*?>(.*?)</table>', re.I | re.S).search(page)  #先找到表格  然后再去找ip 端口和类型(http or https)
        if table_ele is not None:
            target_ele = table_ele.group()
        if target_ele is not None:
            proxy_ips = re.compile(
                r'<tr.*?><td>*?>.*?(\d+.\d+.\d+.\d+).*?</td>.*?<td.*?>.*?(\d+).*?</td>.*?<td>.*?</td>.*?<td.*?>.*?</td>.*?<td.*?>(.*?)</td>',
                re.I | re.S).findall(
                target_ele) # re.I和re.S 是修饰符 你可以去搜下
            if len(proxy_ips) > 0:
                return proxy_ips

    def parse_next_page(self, page):
        """这个是爬取代理ip的网页翻页"""
        target_ele = None
        next_ul = re.compile(r'<ul class="pagination">(.*?)</ul>', re.I | re.S).search(page)
        if next_ul is not None:
            target_ele = next_ul.group()
        if target_ele is not None:
            next_href = re.compile(r'<a.*?href="(.*?)".*?>', re.I | re.S).findall(target_ele)
            if len(next_href) > 1:
                return next_href[1]

    # 一个while 还有一个for 主要柑橘一个用于控制抓取代理的页数(数量) 这里写的太冗余了
    def run_w(self):  # while
        _next = random.choice(Util.read_json('../settings.json').get('proxy_url'))
        while _next != '':
            # 爬取页面
            _page = self.spider(_next)
            # 解析出页面中所有的IP
            proxy_ips = self.parse_proxy_ips(_page)

            # 获取下一页
            __next = self.parse_next_page(_page)
            if __next:
                _next = re.sub(r'page=(.*?)', 'page=%s' % __next, _next)
            else:
                _next = ''

            for ip in proxy_ips:  # 写入数据
                if Util.is_contant('./ip_used.csv', ip):
                    Util.write_data_csv([':'.join(ip)])

    def run_f(self, page_num):  # for
        _next = random.choice(Util.read_json('../settings.json').get('proxy_url'))
        for i in range(page_num):
            # 爬取页面
            _page = self.spider(_next)
            # 解析出页面中所有的IP
            proxy_ips = self.parse_proxy_ips(_page)
            # 获取下一页
            __next = self.parse_next_page(_page)
            if __next:
                _next = 'https://ip.ihuan.me/%s' % __next
            else:
                _next = ''

            for ip in proxy_ips:  # 写入数据
                if Util.is_contant('./ip_used.csv', ip):
                    Util.write_data_csv([':'.join(ip)])


if __name__ == '__main__':
    GetIP().run_f(2)
