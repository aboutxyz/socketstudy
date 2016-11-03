#coding:utf-8

# TCP客户端:
# 1 创建套接字，连接远端地址
       # # socket.socket(socket.AF_INET,socket.SOCK_STREAM) , s.connect()
# 2 连接后发送数据和接收数据          # s.sendall(), s.recv()
# 3 传输完毕后，关闭套接字          #s.close()

import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5550))

while 1:
    try:
        data = raw_input('test:')
        s.send(data)
        print data
    except:
        pass
