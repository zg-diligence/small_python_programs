# -*- coding:utf-8 -*-
"""
  Copyright(c) 2018 Gang Zhang
  All rights reserved.
  Author: Gang Zhang
  Creation Date: 2018.5.4
  Last Modified: 2018.5.9

  Function:
    simulate the server
"""

import socket
import client
import threading
from util import *

proto = SR

def new_server_socket(server_port, client_port, path, protocol):
    # 设置网络连接为IPv4,传输层协议为udp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 传输完成后立即回收该端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 任意IP均可以访问
    s.bind(('', server_port))

    p = protocol(s)
    p.send_data(path, client_port)


if __name__ == '__main__':
    args = SERVER_PORT_EXTRA, proto, 'server_recv.txt'
    t = threading.Thread(target=client.new_client_socket, args=args)
    t.start()

    new_server_socket(SERVER_PORT, CLIENT_PORT, 'server_push.txt', proto)
