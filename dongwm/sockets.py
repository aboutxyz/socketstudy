#-*- coding: utf8 -*-
'''just a Just a server-side script'''
import socket, traceback, os, sys, time
from time import ctime
from threading import *
from client import mysqldb
from optparse import OptionParser



host = ''
port = 8888
MAXTHREADS = 12
lockpool = Lock()
busylist = {}
waitinglist = {}
queue = []
sem = Semaphore(0) #当计数器为0时，acquire()将阻塞线程至同步锁定状态，直到其他线程调用release()


class MYthread(mysqldb):
    def handleconnt(self,clientsock,choice):
        lockpool.acquire() #使线程进入同步阻塞状态，尝试获得锁定
        print "Received new client connection."
        #判断等待线程是否到达最大线程数，是，就会关闭socket
        try:
            if len(waitinglist) == 0 and (activeCount() - 1) >= MAXTHREADS:
                clientsock.close()
                return
            if len(waitinglist) == 0:
                self.mythread(choice)
            queue.append(clientsock) #socket加入队列，semaphore被释放
            sem.release()
        finally:
            lockpool.release()
#多线程模板，启动线程
    def mythread(self,myth):
        print "Starting new client processor thread"
        t = Thread(target = self.threadworker,args= [myth])
        t.setDaemon(1)
        t.start()
#多线程运行的函数，处理终止的线程，初始化waitinglist
    def threadworker(self,choice):
        global waitinglist, lockpool, busylist
        time.sleep(1)
        name = currentThread().getName()
        try:
            lockpool.acquire()
            try:
                waitinglist[name] = 1
            finally:
                lockpool.release()
            self.processclients(choice)
        finally:
            print "** WARNING** Thread %s died" % name
            if name in waitinglist:
                del waitinglist[name]
            if name in busylist:
                del busylist[name]
            self.mythread(choice)
#让接收和发送socket作为2个线程
    def mthread(self,clientsock):
        mlist = []
        for th in ['rev','sed']:
             t = Thread(target = self.handleconnt,args = [clientsock,th])
             mlist.append(t)
             t.setDaemon(1)
             t.start()
        for t in mlist:
             t.join()
#响应客户端连接的处理请求
    def processclients(self,choice):
        global sem, queue, waitinglist, busylist, lockpool
        name = currentThread().getName()
        self.mysqlconnt=mysqldb()


        while 1:
            sem.acquire()
            lockpool.acquire()
            try:
                clientsock = queue.pop(0)
                del waitinglist[name]
                busylist[name] = 1
            finally:
                lockpool.release()


            try:
                print "[%s] Got connection from %s" % \
                        (name, clientsock.getpeername())
                if choice == "sed":
                    while 1:
                        try:
                            sys.stdout.write('>')
                            data = sys.stdin.readline()
                            sys.stdout.flush()
                            if not data:
                                break
                            clientsock.sendall('[%s] %s' % (ctime(),data))
                            self.mysqlconnt.insert('Server',socket.gethostbyname(socket.gethostname()),ctime(),data)
                        except socket.error, e:
                            print "Error sending data : %s" % e
                            sys.exit(1)
                elif choice == "rev":
                     while 1:
                         try:
                             buf = clientsock.recv(2048)
                         except socket.error, e:
                             print "Error receiving data: %s" % e
                             sys.exit(1)
                         if not len(buf):
                             break
                         print "%s says: %s "  % (clientsock.getpeername(),buf)
                         self.mysqlconnt.insert('Server',socket.gethostbyname(socket.gethostname()),ctime(),buf)


            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                traceback.print_exc()


            try:
                clientsock.close()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()


            lockpool.acquire()
            try:
                del busylist[name]
                waitinglist[name] = 1
            finally:
                lockpool.release()
#接收socket，并且指定MYthread类处理
def listener():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen(1)


        while 1:
            try:
                clientsock, clientaddr = s.accept()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()
                continue
            mythread = MYthread()
            mythread.mthread(clientsock)
#主函数
if __name__ == '__main__':
    argc = len(sys.argv)
    parser = OptionParser(description="Socket Talk Shell",add_help_option=False,prog="client.py",version="1.0",usage="%prog")
    parser.add_option("-h", "--help",action = "help",help="print help")
    parser.add_option("-p", "--print",action="store_true",help="print data in mysql")
    options, arguments=parser.parse_args()
    if argc == 1:
        listener()
    if '-h' in sys.argv  or '--help' in sys.argv:
        print __doc__
    elif '-p'  in sys.argv  or '--print' in sys.argv:
        mysqldbconnt=mysqldb()
        mysqldbconnt.select('Server')
    else:
       print 'Please run this script without parameters'
