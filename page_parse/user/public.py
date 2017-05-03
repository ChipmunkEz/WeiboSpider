# -*-coding:utf-8 -*-
# 各类用户公有的模块
import re
import json
from bs4 import BeautifulSoup
from page_parse import status
from decorator.decorators import parse_decorator


def get_userid(html):
    return status.get_userid(html)


def get_username(html):
    return status.get_username(html)


def get_userdomain(html):
    return status.get_userdomain(html)


@parse_decorator(1)
def _get_header(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')
    cont = ''
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'pl.header.head.index' in script.string:
            all_info = m.group(1)
            cont = json.loads(all_info)['html']
    return cont


def get_verifytype(html):
    """
    :param html:
    :return: 0表示未认证，1表示个人认证，2表示企业认证
    """
    if 'icon_pf_approve_co' in html:
        return 2
    elif 'icon_pf_approve' in html:
        return 1
    else:
        return 0


@parse_decorator(1)
def get_verifyreason(html, verify_type):
    if verify_type == 1 or verify_type == 2:
        soup = BeautifulSoup(_get_header(html), 'html.parser')
        return soup.find(attrs={'class': 'pf_intro'})['title']
    else:
        return ''


@parse_decorator(1)
def get_headimg(html):
    soup = BeautifulSoup(_get_header(html), 'html.parser')
    try:
        headimg = soup.find(attrs={'class': 'photo_wrap'}).find(attrs={'class': 'photo'})['src']
    except AttributeError:
        headimg = ''
    return headimg


@parse_decorator(1)
def get_left(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')
    cont = ''
    l_id = ''
    # 这里先确定左边的标识
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'WB_frame_b' in script.string:
            all_info = m.group(1)
            cont = json.loads(all_info)['html']
            lsoup = BeautifulSoup(cont, 'html.parser')
            l_id = lsoup.find(attrs={'class': 'WB_frame_b'}).div['id']
    for script in scripts:
        m = pattern.search(script.string)
        if m and l_id in script.string:
            all_info = m.group(1)
            try:
                cont = json.loads(all_info)['html']
            except KeyError:
                return ''
    return cont


@parse_decorator(1)
def get_right(html):
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all('script')
    pattern = re.compile(r'FM.view\((.*)\)')
    cont = ''
    # 这里先确定右边的标识,企业用户可能会有两个r_id
    rids = []
    for script in scripts:
        m = pattern.search(script.string)
        if m and 'WB_frame_c' in script.string:
            all_info = m.group(1)
            cont = json.loads(all_info)['html']
            rsoup = BeautifulSoup(cont, 'html.parser')
            r_ids = rsoup.find(attrs={'class': 'WB_frame_c'}).find_all('div')
            for r in r_ids:
                rids.append(r['id'])
    for script in scripts:
        for r_id in rids:
            m = pattern.search(script.string)
            if m and r_id in script.string:
                all_info = m.group(1)
                try:
                    cont += json.loads(all_info)['html']
                except KeyError:
                    return ''
    return cont


@parse_decorator(0)
def get_level(html):
    pattern = '<span>Lv.(.*?)<\\\/span>'
    rs = re.search(pattern, html)
    if rs:
        return rs.group(1)
    else:
        return 0


@parse_decorator(2)
def get_fans_or_follows(html):
    """
    :param: 关注或者粉丝页面
    :return:urls表示获取的该页关注或者粉丝主页URL，cur_urls表示该用户所有能查看的页面URL,不包括当前页(一般只有五页)
    """
    if html == '':
        return list()

    pattern = re.compile(r'FM.view\((.*)\)')
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all('script')

    user_ids = list()
    for script in scripts:
        m = re.search(pattern, script.string)

        if m and 'pl.content.followTab.index' in script.string:
            all_info = m.group(1)
            cont = json.loads(all_info).get('html', '')
            soup = BeautifulSoup(cont, 'html.parser')
            follows = soup.find(attrs={'class': 'follow_box'}).find_all(attrs={'class': 'follow_item'})
            pattern = 'uid=(.*?)&'
            for follow in follows:
                m = re.search(pattern, str(follow))
                if m:
                    user_ids.append(m.group(1))
    return user_ids


def get_max_crawl_pages(html):
    if html == '':
        return 1

    pattern = re.compile(r'FM.view\((.*)\)')
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all('script')
    length = 1

    for script in scripts:
        m = re.search(pattern, script.string)

        if m and 'pl.content.followTab.index' in script.string:
            all_info = m.group(1)
            cont = json.loads(all_info).get('html', '')
            soup = BeautifulSoup(cont, 'html.parser')
            pattern = 'uid=(.*?)&'

            if 'pageList' in cont:
                urls2 = soup.find(attrs={'node-type': 'pageList'}).find_all(attrs={
                    'class': 'page S_txt1', 'bpfilter': 'page'})
                length += urls2
    return length
