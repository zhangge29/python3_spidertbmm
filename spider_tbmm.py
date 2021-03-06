# -*-coding:utf-8-*-
import random
import os
import time
from urllib import request, parse
import json
import re
import ssl
import requests


class spider_tbmm:
    def __init__(self):
        self.url = 'https://mm.taobao.com/tstar/search/tstar_model.do?_input_charset=utf-8'

    # 先打开首页，获取基本信息【分页是post实现的】
    def get_basicinfo_list(self, startuserid=0):

        for pageindex in range(1, 1400):  # 看淘宝mm有多少页这个值就多少
            data = {'viewFlag': 'A',
                    'sortType': 'default',
                    'searchRegion': 'city:',
                    'currentPage': pageindex,  # 分页
                    'pageSize': '100'  # 100
                    }
            header = {'Host': 'mm.taobao.com',
                      'Origin': 'https://mm.taobao.com',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.',
                      'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                      'Accept': 'application/json, text/javascript, */*; q=0.01',
                      'X-Requested-With': 'XMLHttpRequest',
                      'Referer': 'https://mm.taobao.com/search_tstar_model.htm?spm=5679.126488.640745.2.69891757XQaub1',
                      'Accept-Encoding': 'gzip, deflate, br',
                      'Accept-Language': 'zh-CN,zh;q=0.8'}
            url = self.url

            # urllib搞不定了，返回内容一直有解码问题,还是用requests
            # req = request.Request(url, parse.urlencode(data).encode('UTF-8'), header)  # 构造request
            # response = request.urlopen(req).read().decode('UTF-8','ignore')
            # print(response)

            # 直接用requests库就不会有那么多编码问题，还能知道编码
            response = requests.post(url, data=data, headers=header, verify=False)
            # print(response.encoding)
            # print(response.text)

            basic_info = json.loads(response.text)['data']['searchDOList']
            for i in basic_info[startuserid:len(basic_info)]:
                print('姓名：{0},userid：{1}'.format(i['realName'], i['userId']))
            # return basic_info[startuserid:len(basic_info)]

    # 获取每个用户所有相册id
    def get_album_list(self, userid):
        album_url = 'https://mm.taobao.com/self/album/open_album_list.htm?_charset=utf-8&user_id%20={}'.format(userid)
        req = request.Request(album_url)
        response = request.urlopen(req).read().decode('gbk')

        # print(response)
        # 特殊字符记得转义
        pattern = 'a class="mm\-first" href="//mm\.taobao\.com/self/album_photo\.htm\?user_id={0}&album_id=(.*?)&album_flag=0'.format(
            userid)
        albums = re.findall(pattern, response)
        # for i in albums[::2]:
        #     print(i)
        return albums[::2]  # 这里返回的相册信息是重复的所以去重

    # 获取所有每个照片id，picid
    def get_album_erverpicid_list(self, userid, albumid):
        album_detail_url = 'https://mm.taobao.com/album/json/get_album_photo_list.htm?user_id={}&album_id={}'.format(
            userid, albumid)
        response = request.urlopen(album_detail_url).read().decode('gbk', 'ignore')

        # print(response)
        # pattern = r'href="//mm.taobao.com/self/album_photo.htm?user_id=(.*)&album_id=(.*)"'
        # print(re.findall(pattern, response))
        # for i in json.loads(response)['picList']:
        #     print(i['userId'] + '-' + i['albumId'] + '-' + i['picId'])

        picids = []
        for i in json.loads(response)['picList']:
            # print(i['picId'])
            picids.append(i['picId'])
        # print(detailurl)
        return picids
        # return json.loads(response)['picList']

    # 获取每张照片的真实url
    def get_alum_bigpic_url(self, userid, picid):
        picurl = 'https://mm.taobao.com/album/json/get_photo_data.htm?_input_charset=utf-8'
        data = {'album_user_id': userid,
                'pic_id': picid,
                'album_id': '',
                '_tb_token_': '3373b115eccce',
                'is_edit': 'True'
                }
        header = {'User-Agent':
                      'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25',
                  'Host': 'mm.taobao.com',
                  'X-Requested-With': 'XMLHttpRequest',
                  'Origin': 'https://mm.taobao.com',
                  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'  # 经过fiddler测试这个必须加,其他几个非必须
                  }

        ssl._create_default_https_context = ssl._create_unverified_context  # 取消ssl验证
        req = request.Request(picurl, parse.urlencode(data).encode('gbk'), headers=header)
        response = request.urlopen(req).read().decode('gbk', 'ignore')
        # print(response)
        # print(json.loads(response)['photo_url'][2:])

        realurl = 'http:' + json.loads(response)['photo_url']
        print(realurl)
        return realurl

    # 启动爬虫
    def spider_start(self, startuserid=0):
        print('爬虫已启动')
        cla = spider_tbmm()
        for i in cla.get_basicinfo_list(startuserid):
            try:
                index = 0
                # 以mm姓名为依据，创建文件夹
                rootpath = "D:\\淘宝mm\\{}\\".format(i['realName'])
                cla.mkdir(rootpath)
                # 创建基本信息
                print('发现一个mm,姓名:{},身高:{},体重:{}KG'.format(i['realName'], i['height'], i['weight']))
                mminfo = '姓名：{name}\n城市：{city}\n身高：{height}\n体重：{weight}KG'.format(name=i['realName'], city=i['city'],
                                                                                   height=i['height'],
                                                                                   weight=i['weight'])
                cla.save_mmbasic_info(rootpath + '{}简介.txt'.format(i['realName']), mminfo)
                # 找到当前mm的所有相册
                for j in cla.get_album_list(i['userId']):
                    try:
                        # 找到相册里面的每张图片的真实地址
                        for m in cla.get_album_erverpicid_list(i['userId'], j):
                            pic_real_url = ''
                            try:
                                pic_real_url = cla.get_alum_bigpic_url(i['userId'], m)  # 获取到了图片的真实地址开始保存
                                print('找到了{}的一张照片，正在保存哦'.format(i['realName']))
                                picpath = (rootpath + '{}{}.jpg').format(i['realName'], index)
                                cla.save_img(pic_real_url, picpath)
                                index += 1
                            except BaseException as e:
                                print('当前{}的一张照片保存失败，相册id为：{}，照片id：{},照片地址为{}. 错误原因{}'
                                      .format(i['realName'], j, m, pic_real_url, e))
                                continue
                    except BaseException as e:
                        print('当前{}的相册获取失败，相册id为{}. 错误原因{}'.format(i['realName'], j, e))
                        time.sleep(random.randint(3, 6))  # 爬完一个相册之后等待3-6秒再爬，防止反爬虫
                        print('正在线程等待几秒钟')
                        continue
            except BaseException as e:
                print('当前{}的基本信息获取失败. 错误原因{}'.format(i['realName'], e))
                continue

    # 创建目录
    def mkdir(self, dirpath):
        '''

        :param dirpath: 目录路径
        :return:
        '''
        path = dirpath.strip()
        if (os.path.exists(path)):
            # print('文件夹{}已存在'.format(dirpath))
            pass
        else:
            os.makedirs(path)

    # 保存个人简介
    def save_mmbasic_info(self, txtpath, mminfo):
        '''

        :param txtpath: 要保存的简介路径
        :param mminfo: mm描述信息
        :return:
        '''
        print(txtpath)
        with open(txtpath, 'w') as f:  # txtpath不支持多级目录
            f.write(mminfo)

    # 保存图片
    def save_img(self, picurl, filepath):
        p = request.urlopen(picurl)
        data = p.read()
        with open(filepath, 'wb') as f:
            f.write(data)

# spider_tbmm().get_basicinfo_list(0) # 单独运行可以获取所有模特基本信息（用的分页）
# spider_tbmm().get_album_list(176817195)
# spider_tbmm().get_album_erverpicid_list(176817195,10000962815)
# spider_tbmm().get_alum_bigpic_url(176817195, 10003453420)

# spider_tbmm().spider_start(0) # 启动爬虫
