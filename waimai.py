from selenium import webdriver
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import string
import zipfile
import os
import pymysql
import random
import math
import base64

# 代理服务器
proxyHost = "http-dyn.abuyun.com"
proxyPort = "9020"

# 代理隧道验证信息 使用自己的
proxyUser = "H85VGZS80R80AP5D"
proxyPass = "37AAA4DCAF5E1F5F"


def create_proxy_auth_extension(proxy_host, proxy_port,
                                proxy_username, proxy_password,
                                scheme='http', plugin_path=None):
    if plugin_path is None:
        plugin_path = os.getcwd() + r'/{}_{}@http-dyn.abuyun.com_9020.zip'.format(proxy_username, proxy_password)

    manifest_json = """
       {
           "version": "1.0.0",
           "manifest_version": 2,
           "name": "Abuyun Proxy",
           "permissions": [
               "proxy",
               "tabs",
               "unlimitedStorage",
               "storage",
               "<all_urls>",
               "webRequest",
               "webRequestBlocking"
           ],
           "background": {
               "scripts": ["background.js"]
           },
           "minimum_chrome_version":"22.0.0"
       }
       """
    # print("sadadaasda")

    background_js = string.Template(
        """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
            }
          };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )

    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    # print("bbbbbb")

    return plugin_path


#创建插件代理,如果文件已经创建,就不必再创建了
# proxy_auth_plugin_path = create_proxy_auth_extension(
#     proxy_host=proxyHost,
#     proxy_port=proxyPort,
#     proxy_username=proxyUser,
#     proxy_password=proxyPass)
# print("cccccccc")
#百度坐标转高德
def bd_decrypt(bd_lng, bd_lat):
    print(bd_lng)
    print(bd_lat)
    # 百度坐标转换高德
    X_PI = math.pi * 3000.0 / 180.0
    x = bd_lng - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * X_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * X_PI)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return {'lon': str(round(gg_lng,5)), 'lat': str(round(gg_lat,6))}


option = webdriver.ChromeOptions()
# 不显示UI界面,会报错
# option.add_argument('-headless')

prefs = {
    'profile.default_content_setting_values': {
        'images': 2
    }
}
#不加载图片
option.add_experimental_option('prefs', prefs)
#option.add_argument("--start-maximized")
# 设置中文
option.add_argument('lang=zh_CN.UTF-8')
default_header = [
        {'User-Agent': 'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'},
        {'User-Agent': 'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'},
        {'User-Agent': 'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0;'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE6.0;WindowsNT5.1)'},
        {'User-Agent': 'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1'},
        {'User-Agent': 'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1'},
        {'User-Agent': 'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11'},
        {'User-Agent': 'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11'},
        {'User-Agent': 'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)'},
        {'User-Agent': 'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)'}
    ]

header_now = random.choice(default_header)
option.add_argument('User-Agent='+header_now['User-Agent'])

# option.add_extension(proxy_auth_plugin_path)
#H8S586W474G3005D
#F516EB80A1F0EC9F
option.add_extension('./H85VGZS80R80AP5D_37AAA4DCAF5E1F5F@http-dyn.abuyun.com_9020.zip')
browser = webdriver.Chrome(options=option)
try:
    # 只能以美团为入口 【因为他会设置一些Cookie】为了方便就不在复杂的弄了
    browser.get('https://www.meituan.com/')
    #browser.get('https://waimai.meituan.com/new/waimaiIndex/?stay=1')
    #39.917356,116.51777
    #百度的坐标
    de_lonlat = bd_decrypt(116.393654,39.8673)
    post_url = 'https://waimai.meituan.com/geo/geohash?lat={lat}&lng={lon}&addr=未知&from=m'.format(**de_lonlat)
    print(post_url)
    browser.get(post_url)
    current = browser.current_url
    if str(browser.current_url).find('home') >= 0:
        print('poilist---------')
        # 循环页面的商家列表
        poilist = browser.find_element(By.CLASS_NAME, 'list')
        db = pymysql.connect("rm-2ze53x25prbr5p80f0o.mysql.rds.aliyuncs.com", "spiderdev", "spiderdev", "spider_datadb")
        for one_shop in poilist.find_elements(By.CLASS_NAME, 'rest-li'):
            try:
                current_shop_detail = one_shop.find_element_by_tag_name('a').click()
                time.sleep(3)
                browser.switch_to.window(browser.window_handles[1])
                time.sleep(3)
                shop_name = browser.find_element(By.CLASS_NAME, 'details').find_element(By.CLASS_NAME,'na').find_element_by_tag_name('a').text
                address = browser.find_element(By.CLASS_NAME, 'details').find_element(By.CLASS_NAME, 'rest-info-down-wrap').find_element(By.CLASS_NAME, 'rest-info-thirdpart').find_element(By.CLASS_NAME, 'poi-detail-right').get_attribute('textContent')
                telphone = browser.find_element(By.CLASS_NAME, 'details').find_element(By.CLASS_NAME, 'rest-info-down-wrap').find_element(By.CLASS_NAME, 'telephone').find_element(By.CLASS_NAME, 'poi-detail-right').get_attribute('textContent')
                print('店名:' + shop_name)
                print('地址:' + address)
                print('联系方式:' + telphone)
                tmp_data = {}
                tmp_data['all_phone'] = str(telphone)
                phone = telphone.split("/")
                tmp_data['phone'] = str(phone[0])
                tmp_data['shop_name'] = str(shop_name)
                tmp_data['address'] = str(address)
                tmp_data['created_at'] = str(time.time()).split('.')[0]
                cursor = db.cursor()
                sql_insert = "INSERT INTO waimai_meituan(shop_name,phone,all_phone,address,created_at) VALUES ('{shop_name}', '{phone}','{all_phone}','{address}','{created_at}')".format(**tmp_data)
                print(sql_insert)
                res = cursor.execute(sql_insert)
                print(res)
                cursor.close()
                #db.close()
                time.sleep(2)
                #关闭当前选项卡
                browser.close()
                browser.switch_to.window(browser.window_handles[0])
            except:
               browser.close()
               browser.switch_to.window(browser.window_handles[0])
               continue
    #将选项卡切回到主页面
    print(browser.current_window_handle)
    print(browser.current_url)
    #查看下一页
    browser.find_element(By.ID, 'loading').find_element(By.CLASS_NAME, 'isloading').click()
finally:
    #browser.quit()
    pass

