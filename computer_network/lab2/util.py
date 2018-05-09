# -*- coding:utf-8 -*-
"""
  Copyright(c) 2018 Gang Zhang
  All rights reserved.
  Author: Gang Zhang
  Creation Date: 2018.5.4
  Last Modified: 2018.5.9

  Function:
    GBN protocol ans protocol
"""

import select
from random import random

DEBUG = True

HOST = '127.0.0.1'
SERVER_PORT = 8888
CLIENT_PORT = 8889
SERVER_PORT_EXTRA = 5003
CLIENT_PORT_EXTRA = 5004

BUFFER_SIZE = 2048    # socket接受字符数
SDN_WINDOW_LENGTH = 5 # 发送窗口大小
ACC_WINDOW_LENGTH = 3 # 接受窗口大小
SEQ_LENGTH = 10       # 总内存大小
MAX_CNT = 3           # 超时上限

END_MARK = 'All is over!' # 通信结束标志

class Data(object):
    """
    数据包/分组
    """

    def __init__(self, msg, seq_num=0, state=0):
        self.msg = msg      # 消息内容
        self.state = state  # 消息状态
        self.seq_num = str(seq_num % SEQ_LENGTH) # 窗口序列号

    def __str__(self):
        return self.seq_num + ' ' + self.msg

class GBN(object):
    """
    基于GBN协议的CS数据传输实现
    """

    def __init__(self, sock):
        self.sock = sock

    def send_data(self, path, port):
        """
        作为客户端发送数据
        :param path: 数据文件路径
        :param port: 服务器端口
        :return: None
        """

        with open(path, 'r') as fr:
            src_data = fr.read().strip().split('\n')

        data_window = []
        file_end_flag = False
        send_END_MARK = False
        counter, seq_num = 0, 0

        while True:
            # 向发送窗口添加数据
            while len(data_window) < SDN_WINDOW_LENGTH and not file_end_flag:
                if src_data:
                    line_data = src_data.pop(0)
                    data_window.append(Data(line_data, seq_num))
                    seq_num += 1
                else:
                    file_end_flag = True
                    if DEBUG: print('data read finished!')
                    break

            # 所有数据发送完毕,向服务器发送关闭连接请求
            if not data_window and not send_END_MARK:
                self.sock.sendto(str(END_MARK), (HOST, port))
                if DEBUG: print('client send END_MARK!')
                send_END_MARK = True

            # 继续发送数据
            for data in data_window:
                if not data.state:
                    self.sock.sendto(str(data), (HOST, port))
                    if DEBUG: print('client send %s' % data)
                    data.state = 1

            # 检测时否收到ACK或者关闭确认信息
            readable, writeable, errors = select.select([self.sock, ], [], [], 1)
            base_move_flag = False
            if len(readable):
                msg, address = self.sock.recvfrom(BUFFER_SIZE)

                # 收到服务器关闭确认消息
                if msg == END_MARK:
                    self.sock.close()
                    if DEBUG: print('client already close!')
                    return

                # 滑动窗口,重启计时器
                if DEBUG: print("client recv ACK " + msg)
                for pos, data in enumerate(data_window):
                    if msg == data.seq_num:
                        if DEBUG: print('client send_base move to %s' % ((int(msg)+1)%SEQ_LENGTH))
                        data_window = data_window[pos+1:]
                        base_move_flag = True
                        counter = 0  # 计时器重启
                        break

            # 窗口未移动,计时器加1
            if not base_move_flag:
                counter += 1

            # 超时事件
            if counter > MAX_CNT:
                if DEBUG: print('client recv ACK timeout!')
                for data in data_window:
                    data.state = 0

    def recv_data(self, des_path):
        """
        作为服务器接收数据,回复ACK确认消息
        :return: None
        """

        des_fw = open(des_path, 'w')

        last_ack = SEQ_LENGTH - 1
        while True:
            readable, writeable, errors = select.select([self.sock, ], [], [], 1)
            if len(readable) > 0:
                msg, address = self.sock.recvfrom(BUFFER_SIZE)

                # 收到客户端的关闭连接请求
                if msg == END_MARK:
                    if DEBUG: print('server recv END_MARK!')
                    self.sock.sendto(END_MARK, address)
                    self.sock.close()
                    return

                ack = int(msg.split()[0])
                if last_ack == (ack - 1) % SEQ_LENGTH:
                    # 模拟数据丢包,丢包率20%
                    if random() > 0.2:
                        des_fw.write(msg + '\n')
                        if DEBUG: print('server recv %s' % msg)
                    else:
                        if DEBUG: print('server do not recv %s' % msg)
                        continue

                    # 模拟ACK丢包,丢包率20%
                    last_ack = ack
                    if random() < 0.2:
                        if DEBUG: print('server send ACK %d but lost' % ack)
                        continue

                    # 回复ACK确认消息
                    if DEBUG: print('server send ACK %s' % str(ack))
                    self.sock.sendto(str(ack), address)
                else:
                    # 收到非期望数据包,重发上一次的ACK确认消息
                    if DEBUG: print('server resend ACK %s' % str(last_ack))
                    self.sock.sendto(str(last_ack), address)

class SR(object):
    def __init__(self, sock):
        self.sock = sock

    def send_data(self, path, port):
        """
        作为客户端发送数据
        :param path: 数据文件路径
        :param port: 服务器端口
        :return: None
        """

        with open(path, 'r') as fr:
            src_data = fr.read().strip().split('\n')

        seq_num = 0
        data_window = []
        counter = [0 for _ in range(SEQ_LENGTH)]
        file_end_flag = False
        send_END_MARK = False

        while True:
            # 向发送窗口添加数据
            while len(data_window) < SDN_WINDOW_LENGTH and not file_end_flag:
                if src_data:
                    line_data = src_data.pop(0)
                    data_window.append(Data(line_data, seq_num))
                    seq_num += 1
                else:
                    file_end_flag = True
                    if DEBUG: print('data read finished!')
                    break

            # 所有数据发送完毕,向服务器发送关闭连接请求
            if not data_window and not send_END_MARK:
                self.sock.sendto(str(END_MARK), (HOST, port))
                if DEBUG: print('client send END_MARK!')
                send_END_MARK = True

            # 继续发送数据
            for data in data_window:
                if not data.state:
                    self.sock.sendto(str(data), (HOST, port))
                    if DEBUG: print('client send %s' % data)
                    data.state = 1
                    counter[int(data.seq_num)] = 0

            # 检测时否收到ACK或者关闭确认信息
            readable, writeable, errors = select.select([self.sock, ], [], [], 1)
            if len(readable) > 0:
                msg, address = self.sock.recvfrom(BUFFER_SIZE)

                # 收到服务器关闭确认消息
                if msg == END_MARK:
                    self.sock.close()
                    if DEBUG: print('client already close!')
                    return

                # 确认ACK消息
                if DEBUG: print("client recv ACK " + msg)
                for data in data_window:
                    if msg == data.seq_num:
                        data.state = 2
                        break

                # 滑动窗口
                while data_window and data_window[0].state == 2:
                    if DEBUG: print('client send_base move to %d' % (int(data_window[0].seq_num) + 1))
                    data_window.pop(0)

            for data in data_window:
                if data.state == 1:
                    if counter[int(data.seq_num)] == MAX_CNT:
                        if DEBUG: print('client data %s ACK timeout' % data.seq_num)
                        counter[int(data.seq_num)] = 0
                        self.sock.sendto(str(data), (HOST, port))
                        if DEBUG: print('client resend %s' % data)
                    else:
                        counter[int(data.seq_num)] += 1

    def recv_data(self, des_path):
        """
        作为服务器接收数据,回复ACK确认消息
        :param des_path: file path to write recv data
        :return: None
        """

        des_fw = open(des_path, 'w')
        recv_data_base = 0
        expected_recv_base = 0
        data_window = [Data('', state=0) for _ in range(SEQ_LENGTH)]

        all_recv_data = [] # 记录接受的所有数据, 需要更好的解决方案
        while True:
            readable, writeable, errors = select.select([self.sock, ], [], [], 1)
            if len(readable) > 0:
                msg, address = self.sock.recvfrom(BUFFER_SIZE)

                # 收到客户端的关闭连接请求
                if msg == END_MARK:
                    if DEBUG: print('server recv END_MARK!')
                    self.sock.sendto(END_MARK, address)
                    self.sock.close()
                    des_fw.close()
                    return

                ack = int(msg.split()[0])
                dist = (ack - expected_recv_base) % SEQ_LENGTH

                # 超出接受窗口范围
                if dist >= ACC_WINDOW_LENGTH:
                    if msg.split()[1] in all_recv_data: # unfixed bug
                        if DEBUG: print('server send ACK %s' % str(ack))
                        self.sock.sendto(str(ack), address)
                    continue

                # 模拟数据丢包
                if random() > 0.2:
                    # if DEBUG: print('dist', ack, expected_recv_base, dist)
                    if DEBUG: print('server recv %s' % msg)
                    des_pos = (recv_data_base + dist) % SEQ_LENGTH
                    data_window[des_pos] = Data(msg.split()[1], state=1)
                else:
                    if DEBUG: print('server do not recv %s' % msg)
                    continue

                # 模拟ACK丢失
                if random() < 0.2:
                    if DEBUG: print('server send ACK %d but lost' % ack)
                    continue

                # 回复ACK确认消息
                if DEBUG: print('server send ACK %s' % str(ack))
                self.sock.sendto(str(ack), address)

                # 滑动窗口
                if ack == expected_recv_base:
                    while data_window[recv_data_base].state == 1:
                        des_fw.write(data_window[recv_data_base].msg + '\n')
                        all_recv_data.append(data_window[recv_data_base].msg)
                        data_window[recv_data_base] = Data('', state=0)
                        recv_data_base = (recv_data_base + 1) % SEQ_LENGTH
                        expected_recv_base = (expected_recv_base+1) % SEQ_LENGTH
                        if DEBUG: print('server recv_data_base move to %d' % recv_data_base)
                        if DEBUG: print('server expected_recv_base move to %d' % expected_recv_base)
