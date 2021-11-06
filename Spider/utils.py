import csv
import json
import random

from lxml import etree
from user_agent import generate_user_agent

# 免费代理ip的网站
# https://www.89ip.cn/index_16.html index_page.html
# http://www.kxdaili.com/dailiip/1/10.html page.html
# https://ip.ihuan.me/?page=b97827cc
from Spider.GetIp import GetIP

target_url = ''


class Util:

    @staticmethod
    def get_user_agent():
        """获取一个请求头"""
        user_agent = ''
        while 'AppleWebKit' not in user_agent:
            user_agent = generate_user_agent()
        return user_agent

    @staticmethod
    def write_data_csv(data: list) -> None:
        """数据的写入"""
        with open('Spider/ip.csv', mode='a+', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(data)

    @staticmethod
    def read_data_csv(path: str) -> list:
        """数据的读取"""
        with open(path, mode='r') as f:
            csv_read = csv.reader(f)
            return [line for line in csv_read]

    @staticmethod
    def get_ip(path):
        """获取文件中ip 如果文件中的ip数量小于2那么就增肌ip"""
        ips = Util.read_data_csv(path)
        if len(ips) < 2:  # 如果数量小于2 那么就进行抓取
            GetIP().run_f(10)
        t1 = random.choice(ips)[0]
        Util.change_data_csv(path, t1)
        t1 = t1.split(':')
        if ('不支持' in t1) and len(t1) != 3: # 爬取https页面使用的代理也要是https类型
            Util.get_ip(path)
        ip = 'https://%s:%s' % (t1[0], t1[1])
        return ip

    @staticmethod
    def is_contant(path, tarLine):
        """判断文件中是否有某个数据 如果有就返回False"""
        lines = Util.read_data_csv(path)
        with open(path, mode='w', newline='') as f:
            for i in lines:
                if tarLine == i:
                    return False
            return True

    @staticmethod
    def change_data_csv(path, tarLine) -> bool:
        """修改文件中的数据"""
        lines = Util.read_data_csv(path)
        with open(path, mode='w', newline='') as f:
            csv_writer = csv.writer(f)
            for i in lines:
                if tarLine != i:
                    csv_writer.writerow(i)

    @staticmethod
    def read_json(path):
        """读取json文件 我好像没用"""
        with open(path, mode='rb') as f:
            return json.load(f)

    @staticmethod
    def get_element(pageSource):
        """返回一个element对象 感觉同样也是多余"""
        if (type(pageSource) is str) and (len(pageSource) > 0):
            return etree.HTML(pageSource)
        raise Exception('pagesource is empty')


if __name__ == '__main__':
    # ips = Util.read_data_csv('./ip.csv')
    # ip = random.choice(ips)
    # Util.change_data_csv('./ip.csv', ip)
    print(type(Util.read_json('settings.json')))
