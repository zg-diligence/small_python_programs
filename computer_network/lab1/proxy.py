# -*- coding: utf-8 -*-

"""
  Copyright(c) 2018 Gang Zhang
  All rights reserved.
  Author: Gang Zhang
  Creation Date: 2018.4.28
  Last Modified: 2018.4.28

  Function:
    1.http/https 代理服务器
    2.网站过滤/用户过滤
    3.钓鱼

"""

import socket
import select
import threading
import sys

SITE_FILTER = True
ADDR_FILTER = False

BUFFER_SIZE = 8192
HTTPVER = "HTTP/1.1"
VERSION = "Python Proxy/0.0.1"


def isFishedWeb(url):
    """
    判断是否需要钓鱼
    :param url:
    :return:
    """

    fishweb = "www.163.com"
    return True if url.find(fishweb) != -1 else False


def isFilterWeb(target_url, addr):
    """
    判断是否需要用户过滤或网站过滤
    :param target_url: 目的网站
    :param addr: 用户ip
    :return:
    """

    if ADDR_FILTER:
        fiter_addr_list = ['127.0.0.1']
        for item in fiter_addr_list:
            if item == addr:
                return True

    if SITE_FILTER:
        fiter_web_list = ['gzhang.org']
        for web in fiter_web_list:
            if target_url.find(web) != -1:
                return True
    return False


def get_fish_site():
    """
    获取钓鱼网站的内容
    :return:
    """

    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect(('www.sina.com.cn', 80))
    soc.send(b'GET / HTTP/1.1\r\nHost: www.sina.com.cn\r\nConnection: close\r\n\r\n')

    buffer = []
    while True:
        data = soc.recv(1024)
        if data:
            buffer.append(data)
        else:
            break
    data = b''.join(buffer)

    soc.close()
    _, html = data.split(b'\r\n\r\n', 1)
    return html


class ConnectionHander(object):
    def __init__(self, connection, address, timeout):
        self.target = None
        self.client = connection
        self.client_data = ''
        self.timeout = timeout
        self.address = address
        self.run()

    def run(self):
        self.method, self.path, self.protocol = self.get_header()
        # print(self.method, self.path, self.protocol)
        if self.method == "CONNECT":
            self.https_method()
        elif self.method in ('OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE'):
            if not isFilterWeb(self.path, self.address[0]):
                if not isFishedWeb(self.path):
                    self.http_method()
                else:
                    self.client.send(get_fish_site())
            self.client.close()

    def get_header(self):
        """
        获取请求头
        :return:
        """

        while True:
            self.client_data += self.client.recv(BUFFER_SIZE)
            pos = self.client_data.find('\n')
            if pos != -1:
                break

        data = self.client_data[:pos + 1].split()
        self.client_data = self.client_data[pos + 1:]
        return data

    def connect_target(self, host):
        """
        连接目的服务器
        :param host:
        :return:
        """

        pos = host.find(':')
        port = int(host[pos + 1:]) if pos != -1 else 80
        host = host[:pos] if pos != -1 else host

        try:
            (soc_family, _, _, _, addr) = socket.getaddrinfo(host, port)[0]
            self.target = socket.socket(soc_family)
            self.target.connect(addr)
        except socket.gaierror:
            print('Error! The url is %s' % self.path)
            sys.exit(1)

    def http_method(self):
        """
        http请求处理
        :return:
        """

        self.path = self.path[7:]
        index = self.path.find('/')
        host, path = self.path[:index], self.path[index:]
        self.connect_target(host)
        self.target.send('%s %s %s\n' % (self.method, path, self.protocol) + self.client_data)
        self.client_data = ''
        self.read_write()

    def https_method(self):
        """
        https请求处理
        :return:
        """

        self.connect_target(self.path)
        self.client.send(HTTPVER + ' 200 Connection established\nProxy-agent: %s\n\n' % VERSION)
        self.client_data = ''
        self.read_write()

    def read_write(self):
        """
        监视客户端和服务器端变化,传送数据
        :return:
        """

        sockets = [self.client, self.target]

        count = 0
        while True:
            count += 1

            # readable, writeable, error
            recv, _, error = select.select(sockets, [], sockets, 3)
            if error:
                break

            if recv:
                for soc in recv:
                    data = soc.recv(BUFFER_SIZE)
                    out = self.target if soc is self.client else self.client
                    if data:
                        out.send(data)
                        count = 0

            if count == self.timeout:
                break

        self.client.close()
        self.target.close()


if __name__ == '__main__':
    host, port, IPv6, timeout = 'localhost', 8194, False, 20
    soc_type = socket.AF_INET6 if IPv6 else socket.AF_INET

    soc = socket.socket(soc_type)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 释放端口
    soc.bind((host, port))
    print("Start monitoring on %s:%d." % (host, port))

    soc.listen(10)
    while True:
        kargs = soc.accept() + (timeout,)
        t = threading.Thread(target=ConnectionHander, args=kargs)
        t.start()
