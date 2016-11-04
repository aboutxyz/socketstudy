#coding:utf-8

# TCP客户端:
# 1 创建套接字，连接远端地址
       # # socket.socket(socket.AF_INET,socket.SOCK_STREAM) , s.connect()
# 2 连接后发送数据和接收数据          # s.sendall(), s.recv()
    # send  python2是支持str, python3用的是bytes
# 3 传输完毕后，关闭套接字          #s.close()

import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5550))
s.send('success')

def sendThreadFunc():
    while True:
        try:
            # data = raw_input(u'please input your message: ')
            data = raw_input()
            s.send(data)
            print data
        except:
            pass


def recvThreadFunc():            
    while True:
        try:
            recvdata = s.recv(1024)
            print recvdata
        except:
            pass
            
            
            
th1 = threading.Thread(target=sendThreadFunc)
th2 = threading.Thread(target=recvThreadFunc)
threads = [th1, th2]

for t in threads :
    t.setDaemon(True)
    t.start()
t.join()