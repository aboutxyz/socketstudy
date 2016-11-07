#-*- coding: utf8 -*-
import os,socket, sys, time,traceback,signal
from time import ctime
from threading import *
from optparse import OptionParser
import MySQLdb
#from multiprocessing import Process

ownhost = '127.0.0.1'
ownport = '8989'
host = '127.0.0.1'
textport = '8888'
cv = Condition()  #Condition比lock功能多
spinners = '|/-\\'
spinpos = 0
equeue = []


class MYmsg:
    '''主要是一些信息输出的线程定义以及线程模板'''
    #接受用户input信息
    def fwrite(self,buf):
        sys.stdout.write(buf)
        sys.stdout.flush()
#旋转竖线定义
    def spin(self):
        global spinners, spinpos
        self.fwrite(spinners[spinpos] + "\b")
        spinpos += 1
        if spinpos >= len(spinners):
            spinpos = 0
#把旋转竖线放入线程，运行用户接口,调用wait()使竖线旋转
    def uithread(self):
        global cv, equeue
        while 1:
            cv.acquire()
            while not len(equeue):
                cv.wait(0.15)
                self.spin()


            msg = equeue.pop(0)
            cv.release()
            if msg == 'QUIT':
                self.fwrite("\n")
                sys.exit(0)
            self.fwrite(" \n  %s\r" % msg)
#把打印信息放入线程，调用notify(),添加队列通知其他线程
    def msg(self,message):
        global cv, equeue
        cv.acquire()
        equeue.append(message)
        cv.notify()
        cv.release()
#定义的线程模板方法
    def mythread(self,myth,flag=0):
        if flag:
            t = Thread(target = myth,args = [arg])
        else:
            t = Thread(target = myth)
        t.setDaemon(True)
        t.start()


class Watcher:
    '''用新进程来接受信号后杀掉执行任务进程,主要解决多线程只能杀掉主线程的问题，无法ctrl +c 退出'''
#创建一个子线程，它返回父线程等待一个KeyboardInterrupt，然后杀死子线程
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()
    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            print 'KeyBoardInterrupt'
            self.kill()
        sys.exit()
    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass


class MYconnt(MYmsg):
    '''
    socket连接，打印信息，异常处理
    '''
    def __init__(self):
        self.msg=MYmsg()
    def connt(self):
        self.msg.mythread(self.uithread)  #使用旋转竖线
        try:
            self.msg.msg('Creating socket object')
            time.sleep(3)


            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, e:
            print "Strange error creating socket: %s" % e
            sys.exit(1)


        try:
            port = int(textport)
        except ValueError:
            try:
                port = socket.getservbyname(textport, 'tcp')
            except socket.error, e:
                print "Couldn't find your port: %s" % e
                sys.exit(1)


        self.msg.msg('Connecting to %s:%d' % (host, port))
        time.sleep(2)
        try:
            s.connect((host, port))
        except socket.gaierror, e:
            print "Address-related error connecting to server: %s" % e
            sys.exit(1)
        except socket.error, e:
            print "Connection error: %s" % e
            sys.exit(1)
        self.msg.msg("QUIT")
        return s


class MYtalk(MYconnt):
    '''
    聊天程序接受和发送
    '''
    def __init__(self):
        self.myconnt=MYconnt()
        self.s = self.myconnt.connt()
#根据参数选择发送或者接收socket信息
    def choice(self,th):
        self.mysqlconnt = mysqldb()
        if th == 'sed':
            while 1:
                try:
                    buf = self.s.recv(2048)
                except socket.error, e:
                    print "Error receiving data: %s" % e
                    sys.exit(1)
                except KeyboardInterrupt:
                    raise
                    self.mysqlconnt.close()
                if not len(buf):
                    break
                print "%s says: %s" % ((ownhost,ownport),buf)
                self.mysqlconnt.insert('Client',ownhost,buf.split(']')[0][1:],buf.split(']')[1])
        elif th == 'rev':
            while 1:


                try:
                    sys.stdout.write('>')
                    self.data = sys.stdin.readline()
                    sys.stdout.flush()
                    if not self.data:
                        break
                    elif self.data == "quit":
                        try:
                            self.s.shutdown(1)
                        except socket.error, e:
                            print "Error sending data (detected by shutdown): %s" % e
                            sys.exit(1)


                    self.s.sendall('[%s] %s' % (ctime(),self.data))
                    self.mysqlconnt.insert('Client',socket.gethostbyname(socket.gethostname()),ctime(),self.data)
                except KeyboardInterrupt:
                    raise


                except socket.error, e:
                    print "Error sending data: %s" % e
                    sys.exit(1)
#将接收和发送放在不同的进程
    def process(self):
        plist = []
        for th in ['rev','sed']:
            p = Process(target=self.choice,args = [th])
            plist.append(p)
            p.start()
        for p in plist:
            p.join()
#将接收和发送放在不同的线程
    def mthread(self):
         mlist = []
         for th in ['rev','sed']:
             Watcher()
             t = Thread(target = self.choice,args = [th])
             mlist.append(t)
             t.setDaemon(1)
             t.start()
         for t in mlist:
             t.join()


class mysqldb:
    def __init__(self):
        try :
            self.conn = MySQLdb.connect(host = "127.0.0.1",user = "muxucao",passwd = "900502",db = "socket")
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit (1)
        try :
            self.cursor = self.conn.cursor()
        except :
            raise
    def insert(self,table,ip,time,text):
        sql = "insert into %s(ip,time,text) values('%s','%s','%s');" % (table,ip,time,text)
        try:
            self.cursor.execute(sql)
        except Exception,e:
            print  e
    def select(self,table):
        sql = "select * from %s;" % table
        try:
            self.cursor.execute(sql)
        except Exception,e:
            print e
        for data in self.cursor.fetchall():
            print '%s\t%s\t%s' % data
    def close():
        self.cursor.close()
        self.conn.commit()
        self.conn.close()
#主函数
if __name__ == '__main__':
    argc = len(sys.argv)
    parser = OptionParser(description="Socket Talk Shell",add_help_option=False,prog="Client.py",version="1.0",usage="%prog")
    parser.add_option("-h", "--help",action = "help",help="print help")
    parser.add_option("-p", "--print",action="store_true",help="print data in mysql")
    options, arguments=parser.parse_args()
    if argc == 1:
        mytalk=MYtalk()
        mytalk.mthread()
    if '-h' in sys.argv  or '--help' in sys.argv:
        print __doc__
    elif '-p'  in sys.argv  or '--print' in sys.argv:
        mysqldbconnt=mysqldb()
        mysqldbconnt.select('Client')
    else:
       print 'Please run this script without parameters'
