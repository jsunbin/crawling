"""
====================================
 :mod:`instagram`
====================================

 Description
===========
 인스타그램
"""
# Authors
# ===========
#
# * Jeong Sunbin
#
# Change Log
# --------
#  * [2022/12/27]
#     - starting
################################################################################
import yaml
import traceback
import urllib.request
from urllib.parse import quote_plus
from alabs.common.util.vvlogger import get_logger
from alabslib.selenium import PySelenium


################################################################################
class Instagram(PySelenium):
    # ==========================================================================
    def __init__(self, yaml_f, keyword):
        self.keyword = keyword
        with open(yaml_f, encoding='utf-8') as f:
            self.conf = yaml.load(f, yaml.SafeLoader)
        self.logger = get_logger(self.conf['log'])
        PySelenium.__init__(self, **self.conf['params']['kwargs'], logger=self.logger)

    # ==========================================================================
    def login(self):
        # 로그인
        e = self.get_by_xpath('//input[@name="username"]')
        e.send_keys(self.conf['params']['account']['id'])

        e = self.get_by_xpath('//input[@name="password"]')
        e.send_keys(self.conf['params']['account']['password'])

        e = self.get_by_xpath('//button[@type="submit"]/div')
        self.safe_click(e)

        self.implicitly_wait(after_wait=3)

        # "로그인 정보를 저장하시겠어요?": 나중에하기
        e = self.get_by_xpath('//div[@class="_ac8f"]/button')
        self.safe_click(e)
        self.implicitly_wait(after_wait=1)

        # 알림설정: 하지않기
        self.switch_to_window()
        self.driver.switch_to.active_element
        e = self.get_by_xpath('//div[@role="dialog"]//button[2]')
        self.safe_click(e)
        self.switch_to_main_window()

    # ==========================================================================
    def search(self):
        search_url = self.conf['params']['search']['url'] + quote_plus(self.keyword)
        self.driver.get(search_url)
        self.implicitly_wait(after_wait=1)

        self.save_thumbnail()

    # ==========================================================================
    def save_thumbnail(self):
        # 인기 게시물 9개 이미지 저장
        e = self.get_by_xpath('//div[@class="_aaq8"]')
        e_a = e.find_elements_by_xpath('.//div[@class="_ac7v _aang"]//img')
        for i, a_tag in enumerate(e_a):
            img_url = a_tag.get_attribute('src')
            urllib.request.urlretrieve(img_url, 'test.jpg')
            print(img_url)

        # 최근 게시물: 갯수 max까지 img_url get
        cnt = 0
        img_url_list = []
        while cnt <= self.conf['params']['search']['max']:
            e = self.get_by_xpath('//article[@class="_aao7"]/div[2]')
            e_a = e.find_elements_by_xpath('.//div[@class="_ac7v _aang"]//img')
            for img_tag in e_a:
                img_url = img_tag.get_attribute('src')
                if img_url not in img_url_list:
                    img_url_list.append(img_url)
                    cnt += 1
            self.driver.execute_script(f"scrollBy(0,document.body.scrollHeight)")
            self.implicitly_wait(after_wait=1)

        # 최근 게시물: 갯수 max 까지 이미지 저장
        for e, img_url in enumerate(img_url_list):
            if e <= self.conf['params']['search']['max']:
                urllib.request.urlretrieve(img_url, 'test.jpg')

    # ==========================================================================
    def start(self):
        try:
            self.logger.info(f'Starting {self.__class__.__name__}...')
            self.login()
            self.search()
        except Exception as err:
            self.logger.error(traceback.format_exc())
            raise err
        finally:
            self.logger.info(f'End>>>>>>>>>>')


################################################################################
def do_start(**kwargs):
    with open(kwargs['config_f'], encoding='utf-8') as f:
        conf_yaml = yaml.load(f, yaml.SafeLoader)
        for i, keyword in enumerate(conf_yaml['params']['search']['keyword']):
            with Instagram(kwargs['config_f'], keyword) as ws:
                ws.start()


################################################################################
if __name__ == '__main__':
    _config_f = 'instagram.yaml'
    do_start(config_f=_config_f)
