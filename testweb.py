#coding:utf-8

# TCP服务端：
# 1 创建套接字，绑定套接字到本地IP与端口
   # # socket.socket(socket.AF_INET,socket.SOCK_STREAM) , s.bind()
# 2 开始监听连接                   #s.listen()
# 3 进入循环，不断接受客户端的连接请求              #s.accept()
# 4 然后接收传来的数据，并发送给对方数据         #s.recv() , s.sendall()
#5.如果不使用多线程，造成只能一方可以连接，使用验证字（success）的目的是不乱增加线程，但是造成的是不唯一的认证，
# 6 传输完毕后，关闭套接字 

import socket
import threading
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = '127.0.0.1'
PORT = 5550
s.bind((HOST,PORT))
s.listen(5)
print "Starting listening"
clientlist = []

def addclient(client):
    while 1:
        try:
            data = client.recv(1024)    #客户端发送了必须有接收方，所以要以连接为关键字
            print data
            # print client.getsockname()
            print client.fileno()
        except:
            pass

while True:
    try:
        conn,addr = s.accept()
        buf = conn.recv(1024)
        if buf == 'success':
            mythread = threading.Thread(target=addclient, args=(conn,))
            mythread.setDaemon(True)
            mythread.start()
        else:
            print "bad access"
    except:
        pass
s.close()        
