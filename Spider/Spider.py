
"""
==========================
这个里面主要就是run中的代码

"""
import json
import re
import time
from urllib.parse import urljoin

import requests
import urllib3
from lxml import etree

from Spider.utils import Util


class JdSpider:

    def __init__(self, url, start_=1, end=1):
        self.url = url  # base url
        self.start = start_  # 爬虫从第多少页开始爬取
        self.end = end  # 爬虫怕渠道多少一共爬取多少页
        self.countChange = 0
        self.ip = None # 代理ip 通过类属性切换ip

    def changeIp(self):
        """用于修改ip """
        self.ip = Util.get_ip('./Spider/ip.csv')
        return {'title': ['--------修改Ip为(%s) --- 累计修改了(%d)ip -----' % (self.ip, self.countChange)]}

    def run(self):
        # self.ip = Util.get_ip('./Spider/ip.csv') # 如果想要一开始使用代理ip 那么就在爬虫开始前 就修改成员属性中的ip
        for i in range(self.start - 1, self.end + 1):
            url = re.sub(r'&page=(\d*)', '&page=%d' % (i * 2 + 1), self.url)  # 从首页中获取接口
            temp_data = JdSpider.__param1(self.__spider_goods(url))  # 每一个详情页的数据(价格和链接) 大概是60条
            for temp in temp_data:  # 循环60条数据 因为其中有链接
                goods_detail_url = urljoin('https://item.jd.com/9.html', temp.get('link')[0])  # 组装url
                JdSpider.__cleaning(temp)  # 清洗下数据

                while True: # 无限循环 只有通过就会break 循环才会结束 没有break就是一直切换ip重复爬取 知道爬取完毕
                    time.sleep(1)
                    try:
                        # 请求详情页
                        resp_detail = self.__spider_goods(goods_detail_url, self.ip)

                        # 请求评论
                        product_href = f"https://club.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98&productId=%s&score=0&sortType=5&page=0&pageSize=10" % \
                                       re.compile(r'\d+').findall(goods_detail_url)[0]  # 评论所在url

                        comment_detail = self.__spider_goods(product_href, self.ip)

                        temp['detail_msg'] = JdSpider.__param2(resp_detail)

                        temp['comment_msg'] = JdSpider.__param3(comment_detail)

                        yield temp

                        break

                    except Exception as e:
                        self.countChange += 1
                        yield self.changeIp()

    def __spider_goods(self, url, proxy=None):
        # 解决“Max retries exceeded with url”问题
        s = requests.session()
        s.keep_alive = False  # 关闭多余链接

        urllib3.disable_warnings()

        # 这个是我临时加上来的 实际上是不用cookie的 因为如果使用代理ip 再用cookie感觉会多余，你自己考虑 如果不考虑就直接删除就好了 记得还要删除请求头中的
        cookie = '__jdu=1509510835; areaId=18; ipLoc-djd=18-1488-29447-0; shshshfpa=f82351dc-d49f-bb5e-24d0-731cfbc567f1-1634649982; shshshfpb=qAyHFhtSk0EXqXllxTXfmSA%3D%3D; user-key=6116764f-e55f-4753-8f1d-b17c3b50293e; unpl=V2_ZzNtbUdUFBwlWxVRexkIUmIBR14SU0sSdAlGVS5ODA1gURIOclRCFnUURlVnGl0UZwYZXUpcQRZFCEdkeBBVAWMDE1VGZxBFLV0CFSNGF1wjU00zQwBBQHcJFF0uSgwDYgcaDhFTQEJ2XBVQL0oMDDdRFAhyZ0AVRQhHZHsdXQ1jAxNUQFNzJXI4dmRyHl4AYQYiXHJWc1chVERQexhbACoDFlxKU0MUfApCZHopXw%3d%3d; __jdv=122270672|baidu|-|organic|not set|1634733348541; pinId=34QgwLnLluQM4WAiAdge2bV9-x-f3wj7; pin=jd_76b846a59ad33; unick=jd_76b846a59ad33; _tp=zfrH%2F6XzrOZj12dYrBRt3Oq4krb0ll1wT2aRvfLzVCs%3D; _pst=jd_76b846a59ad33; TrackID=1nry8MOh55EVK1XBR8USQjghFjv0jc6C_mLTwJyJmXGdZNA6l4tOPwedtBHnscNsX62dVt4-DNhJpTVg3kQBqgFBUf8SE9FZ4hW08SqtKLck; ceshi3.com=000; shshshfp=f4426f1fb164992c10bdb8e1b0720704; __jda=122270672.16348230731641318356069.1634823073.1635331775.1635334682.17; __jdc=122270672; thor=F07BF2923D02E3206442572A9D819E4832923620F0DCE2BD129CF4B807057E7A7353288CA7A2CAF5001777C8F7A7CE26314C34D3627FC4B21FAA9996A8AFFA261F67AB92FDD840C923C72324F08A61DA9055D3EF4DF8EDEEEBB19BB5CAB78C750AA4F0F835B4DB4F990FA1B7DEA9BA1FE2A8DBF96F14DC53939B642B91D8150618F1BAF5C511B754A1E0636C13955A5A7C19A86FB252D59E651E59090CCF5CE5; 3AB9D23F7A4B3C9B=ABWQTLTA6JMRYWEBXQVIDATMDOOTW32JTYI4QSC4LZSLRTWHMDGMZPMVII3XL7LV2R2ACVUYASULTZRSFCC3N7RUOE; token=b7183ecea96217e4e46795491e8a922b,3,908519; __tk=d96a5444c71365c835b8c16198cfc861,3,908519; shshshsID=311ea216935918f7c1b9acfa41ffefb4_6_1635335084682; __jdb=122270672.8.16348230731641318356069|17.1635334682; ip_cityCode=1482'

        resp = requests.get(url=url, headers={'User-Agent': Util.get_user_agent(), 'cookie': cookie},
                            proxies={'https': proxy,
                                     'http': proxy},
                            timeout=5, verify=False)
        if resp.status_code == 200 and len(resp.text) > 500:
            return resp.text
        else:
            raise RuntimeError('Request Error')

    @staticmethod
    def __param1(pageSource):
        """解析搜索到的商品 解析了价格 链接 和名字"""
        html = etree.HTML(pageSource)
        lis = html.xpath('//ul[contains(@class,\'gl-warp\')]/li')
        return [{'price': li.xpath('.//div[@class=\'p-price\']')[0].xpath('string(.)'),
                 'link': li.xpath('.//div[@class=\'p-img\']/a/@href'),
                 'title': li.xpath('.//div[contains(@class,\'p-name\')]/a/@title')} for li in lis]

    @staticmethod
    def __param2(pageSource):
        """解析抓取的商品的信息"""
        html = etree.HTML(pageSource)
        detail_msg = html.xpath('//ul[contains(@class,\'parameter2\')]')
        if len(detail_msg) == 0:
            raise RuntimeError('ip可能被封 无法获取数据')
        detail_msg = [j for j in [i.replace(' ', '') for i in detail_msg[0].xpath('string(.)').split('\n')] if
                      len(j) != 0]
        return detail_msg

    @staticmethod
    def __param3(pageSource):
        """解析评论"""
        items_ = {}
        productCommentSummary = re.findall(r'"productCommentSummary":(.*?),"productAttr":null}\);',
                                           pageSource)  # 从网页源码中提取目标数据
        productShowImageRes = re.findall('"imageListCount":(.*?),', pageSource)  # 提取目标数据
        if len(productShowImageRes) > 0:
            items_['晒图'] = productShowImageRes[0]
        if len(productCommentSummary) > 0:
            product_data = json.loads(productCommentSummary[0])
            items_['所有评论'] = product_data.get('commentCountStr') or 0
            items_['视频晒单'] = product_data.get('videoCountStr') or 0
            items_['追评'] = product_data.get('afterCountStr') or 0
            items_['好评'] = product_data.get('goodCountStr') or 0
            items_['中评'] = product_data.get('generalCountStr') or 0
            items_['差评'] = product_data.get('poorCountStr') or 0
        if items_ == {}:
            raise RuntimeError('评论被封')
        return items_

    @staticmethod
    def __cleaning(dict_: dict):
        """数据清洗"""
        dict_['price'] = dict_.get('price').replace('\t', '').replace('\n', '')
        return dict_


if __name__ == '__main__':

    start = 1

    res = JdSpider('https://search.jd.com/Search?keyword=%E6%B0%94%E6%B3%A1%E6%B0%B4&page=1&click=1', start_=start,
                   end=100).run()

    for content in res:
        print(content.get('title'))
        # with open('data.json', 'a+', encoding='utf-8') as f:
        #     line = json.dumps(content, ensure_ascii=False)
        #     f.write(line)
        #     f.write('\n')
