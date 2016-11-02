#coding:utf-8
import socket
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #协议族和类型 分别是ipv4

sock.bind(('localhost', 5550))  #listen前要bind

sock.listen(5)  #至少是1，一般为5
print('Server', socket.gethostbyname('localhost'), 'listening ...') #gethostbyname是取得ip地址

mydict = dict()
mylist = list()

#把whatToSay传给除了exceptNum的所有人
def tellOthers(exceptNum, whatToSay):
    for c in mylist:
        if c.fileno() != exceptNum :    #返回套接字的文字描述符 fileno
            try:
                c.send(whatToSay)
            except:
                pass

def subThreadIn(myconnection, connNumber):
    nickname = myconnection.recv(1024)  #接受TCP套接字的数据。数据以字符串形式返回
    mydict[myconnection.fileno()] = nickname
    mylist.append(myconnection)
    print('connection', connNumber, ' has nickname :', nickname)
    tellOthers(connNumber, u'【系统提示：'+mydict[connNumber]+u' 进入聊天室】')
    while True:
        try:
            recvedMsg = myconnection.recv(1024)
            if recvedMsg:
                print(mydict[connNumber], ':', recvedMsg)
                tellOthers(connNumber, mydict[connNumber]+' :'+recvedMsg)

        except (OSError, socket.error):
            try:
                mylist.remove(myconnection)
            except:
                pass
            print(mydict[connNumber], 'exit, ', len(mylist), ' person left')
            tellOthers(connNumber, u'【系统提示：'+mydict[connNumber]+u' 离开聊天室】')
            myconnection.close()
            return

while True:
    connection, addr = sock.accept()
    print('Accept a new connection', connection.getsockname(), connection.fileno()) #getsockname获取ip
    try:
        #connection.settimeout(5)
        buf = connection.recv(1024)
        if buf == '1':
            connection.send(b'welcome to server!')

            #为当前连接开辟一个新的线程
            mythread = threading.Thread(target=subThreadIn, args=(connection, connection.fileno()))
            mythread.setDaemon(True)
            mythread.start()
            
        else:
            connection.send(b'please go out!')
            connection.close()
    except :  
        pass

