# -*- coding:utf-8 -*-
"""
  Copyright(c) 2018 Gang Zhang
  All rights reserved.
  Author: Gang Zhang
  Creation Date: 2018.5.4
  Last Modified: 2018.5.9

  Function:
    simulate the client
"""

import socket
import server
import threading
from util import *

proto = SR

def new_client_socket(client_port, protocol, des_path):
    # 设置网络连接为IPv4,传输层协议为udp
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 传输完成后立即回收端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # 设置任意IP均可以访问
    s.bind(('', client_port))

    p = protocol(s)
    p.recv_data(des_path)


if __name__ == '__main__':
    args = CLIENT_PORT_EXTRA, SERVER_PORT_EXTRA, 'client_push.txt', proto
    t = threading.Thread(target=server.new_server_socket, args=args)
    t.start()

    new_client_socket(CLIENT_PORT, proto, 'client_recv.txt')
