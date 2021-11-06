import json
import sys

import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from lxml import etree

from Spider.Spider import JdSpider
from Spider.utils import Util
from app import Ui_SpiderQt


# 这个是窗口主类
class Main(QMainWindow):

    def __init__(self):
        self.thread_ = Thread_() #多线程类 如果是单线程的时候那么这个线程是负责窗口绘制的 ，但是爬虫执行和文件写入也要一个线程 所有用的是多线程
        self.thread_.spider_msg_.connect(self.set_spider_msg) #绑定
        self.proxy_ip = False # 这个变量估计没用 没有来得及用
        self.app = QApplication(sys.argv)
        super().__init__()
        self.ui = Ui_SpiderQt() # 这个是导入UI文件
        self.ui.setupUi(self) # 导入UI文件
        # 初始化
        self.init_ui()

    def init_ui(self):

        # 初始化多线程
        # 选中状态
        self.ui.SpiderSleep3.setChecked(True)  # 设置默认选中
        self.ui.SpiderContent_1.setChecked(True)  # 设置默认选中
        self.ui.SpiderContent_2.setChecked(True)  # 设置默认选中
        self.ui.SpiderContent_3.setChecked(True)  # 设置默认选中

        # 绑定事件
        self.ui.b_CheckURL.clicked.connect(self.check_url_sleep_content)
        self.ui.b_SearchURL.clicked.connect(self.search_url)
        self.ui.b_ProxyCheck.clicked.connect(self.check_proxy_ip)
        self.ui.b_SpiderStart.clicked.connect(self.spider_url)

        # 设置按钮是否可用
        # self.ui.b_ProxyCheck.setEnabled(False)
        # self.ui.b_SearchURL.setEnabled(False)
        # self.ui.b_SpidertStop.setEnabled(False)
        # self.ui.b_SpiderStart.setEnabled(False)

        self.show() #展示窗口

    # 获取搜索内容
    def input_url(self):
        return self.ui.JdUrlInput.toPlainText()

    def get_sleep(self):
        """获取睡眠时间"""
        if self.ui.SpiderSleep1.isChecked():
            return 3
        elif self.ui.SpiderSleep2.isChecked():
            return 5
        elif self.ui.SpiderSleep3.isChecked():
            return 7

    def get_content(self):
        """获取需要爬取的内容"""
        content = 0
        if self.ui.SpiderContent_1.isChecked():
            content += 3
        if self.ui.SpiderContent_2.isChecked():
            content += 5
        if self.ui.SpiderContent_3.isChecked():
            content += 7
        return content

    def search_url(self):
        """搜索按钮绑定的时间 其实也就是访问页面 并且展示前面4条数据的 本来是直接想引用写好的那几个模块(spider文件里的，具体忘了)但是总是报我引用错误"""
        show_msg = ''
        print(self.input_url())
        res = requests.get(self.input_url(), headers={'user-agent': Util.get_user_agent()})
        if res.status_code != 200:
            self.ui.OutputLabel.setText('搜索失败,请确认你的Url。你最好可以自己访问下url')
            return
        html = etree.HTML(res.text)
        goods_list = html.xpath('//div[contains(@class,\'p-name\')]/a/@title')
        good_list = [i for i in goods_list if len(i) > 0]
        if len(good_list) < 5:
            self.ui.OutputLabel.setText('搜索失败,请确认你的Url。你最好可以自己访问下url')
            return
        else:
            for i in good_list[0:4]:
                show_msg += i + '\n---------------------------------\n'
            show_msg += '因为内容受限,只会展示前4条数据' + '\n---------------------------------\n'
            self.ui.OutputLabel.setText(show_msg)
            return

    def check_proxy_ip(self):
        """检查是否可以使用代理ip 判断代理ip'文件中是不是有下载下来的代理ip 如果有那么就可以用 感觉写的有问题"""
        ips = Util.read_data_csv('./Spider/ip.csv')
        if len(ips) > 0:
            self.ui.OutputLabel.setText('检查通过,以下爬取过程中将使用代理爬取内容')
            self.proxy_ip = True
        else:
            self.ui.OutputLabel.setText('检查不通过,以下爬取过程中将不使用代理爬取内容')

    def spider_url(self):
        """
        爬虫代码调用 代码是写在多线程中 这里只是点击时调用（绑定了爬取按钮）

        最后4行就是点击爬取后禁用一些按钮 防止重复点击重复调用代码
        """
        self.thread_.get_param(url=self.input_url())
        self.thread_.start()

        self.ui.b_SpiderStart.setEnabled(False)  # 启动后设置不可以被点击
        self.ui.b_ProxyCheck.setEnabled(False)
        self.ui.b_SearchURL.setEnabled(False)
        self.ui.b_SpidertStop.setEnabled(False)

    def set_spider_msg(self, msg):
        """设置展示的信息 就是那个输入框"""
        self.ui.OutputLabel.setText(msg)

    def check_url_sleep_content(self):
        """检查是否有睡眠时间和需要爬取内容是否被选中 如果没选中就意味着没有爬取目标 那么就不给用户爬取 感觉radiobutton好像是不用判断的 不过写了应该也没关系"""
        url = self.input_url()
        sleep = self.get_sleep()
        content = self.get_content()
        if ('https://' in url) and (sleep > 0) and (content > 0):
            self.ui.OutputLabel.setText('检查通过,请执行操作,如若使用代理，请进行检查代理是否可用')
            self.ui.b_ProxyCheck.setEnabled(True)
            self.ui.b_SearchURL.setEnabled(True)
            self.ui.b_SpiderStart.setEnabled(True)
        else:
            self.ui.OutputLabel.setText('检查不通过,请重新检查输入项')


class Thread_(QThread):
    """这个就是多线程代码 具体的https://www.bilibili.com/video/BV1Kb4y1f71x?from=search&seid=12460506969173287053&spm_id_from=333.337.0.0看这个学习"""
    spider_msg_ = pyqtSignal(str)

    def __init__(self):
        super(Thread_, self).__init__()
        self.spider_msg = ''
        self.url = ''

    def spider_run(self):
        """在线程函数中写爬虫执行的逻辑代码"""
        start = 1

        res = JdSpider(self.url, start_=start,
                       end=100).run()
        for content in res:
            self.spider_msg = content.get('title')[0] + '\n' + self.spider_msg
            self.spider_msg_.emit(self.spider_msg)
            with open('data.json', 'a+', encoding='utf-8') as f:
                line = json.dumps(content, ensure_ascii=False)
                f.write(line)
                f.write('\n')

    def get_param(self, url):
        self.url = url

    def run(self):
        self.spider_run()
        self.spider_msg_.emit(self.spider_msg)


if __name__ == '__main__':
    main = Main()
    sys.exit(main.app.exec_())
