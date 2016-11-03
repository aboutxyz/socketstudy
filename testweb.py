#coding:utf-8

# TCP服务端：
# 1 创建套接字，绑定套接字到本地IP与端口
   # # socket.socket(socket.AF_INET,socket.SOCK_STREAM) , s.bind()
# 2 开始监听连接                   #s.listen()
# 3 进入循环，不断接受客户端的连接请求              #s.accept()
# 4 然后接收传来的数据，并发送给对方数据         #s.recv() , s.sendall()
# 5 传输完毕后，关闭套接字 

import socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
HOST = '127.0.0.1'
PORT = 5550
s.bind((HOST,PORT))
s.listen(5)
print "done"
clientlist = []

    
while True:
    conn,addr = s.accept()
    try:
        buf = conn.recv(1024)
        print buf
    except:
        pass
        
conn.close