#coding:utf-8
import socket
import time
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.connect(('localhost', 5550))
sock.send(b'1')
print(sock.recv(1024))
nickName = raw_input('input your nickname: ')
sock.send(nickName)

def sendThreadFunc():
    while True:
        try:
            myword = raw_input()
            sock.send(myword.encode())
            #print(sock.recv(1024).decode())
        except socket.error:
            break
            print('Server closed this connection!')
        except socket.error:
            break
            print('Server is closed!')
    
def recvThreadFunc():
    while True:
        try:
            otherword = sock.recv(1024)
            if otherword:
                print(otherword)
            else:
                pass
        except socket.error:
            break
            print('Server closed this connection!')

        except socket.error:
            break
            print('Server is closed!')


th1 = threading.Thread(target=sendThreadFunc)
th2 = threading.Thread(target=recvThreadFunc)
threads = [th1, th2]

for t in threads :
    t.setDaemon(True)
    t.start()
t.join()
