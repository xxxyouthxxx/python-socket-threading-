# noinspection PyUnresolvedReferences
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from Huice_look_server import Ui_Form
import sys
import pymysql
import socket
import threading
import time

db = pymysql.connect(host='',
                     port=写自己的,
                     user='写自己的',
                     passwd='写自己的',
                     database='写自己的',
                     charset='utf8')
cur = db.cursor()


class Main(QtWidgets.QWidget, Ui_Form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.get_ip()
        self.link = False
        self.tcp_socket = None
        self.sever_th = None
        self.client_socket_list = list()
        self.pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.pushButton_2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.pushButton_4.clicked.connect(
            lambda: {self.stackedWidget.setCurrentIndex(0), self.lineEdit.clear(), self.lineEdit_2.clear()})
        self.pushButton_6.clicked.connect(
            lambda: {self.stackedWidget.setCurrentIndex(0), self.lineEdit_3.clear(), self.lineEdit_4.clear(),
                     self.lineEdit_5.clear()})
        self.pushButton_3.clicked.connect(lambda: self.log_in())
        self.pushButton_5.clicked.connect(lambda: self.registered())
        self.pushButton_10.clicked.connect(
            lambda: {self.stackedWidget.setCurrentIndex(0), self.lineEdit.clear(), self.lineEdit_2.clear()})
        self.pushButton_11.clicked.connect(lambda: {self.tcp_server_start(), self.pushButton_11.setEnabled(False)})
        self.pushButton_7.clicked.connect(lambda: {self.tcp_send(), self.textEdit.clear()})
        self.pushButton_9.clicked.connect(lambda: self.click_clear())

    def log_in(self):
        global username
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        sql = "select username from username where username=%s"
        cur.execute(sql, username)
        one_row = cur.fetchone()
        if one_row:
            sql = "select password from username where username=%s"
            cur.execute(sql, username)
            one_row = cur.fetchone()
            if one_row[0] == password:
                reply = QMessageBox.information(self, '标题', '登陆成功', QMessageBox.Ok)
                self.lineEdit_6.setText(username)
                self.stackedWidget.setCurrentIndex(3)

            else:
                reply = QMessageBox.information(self, '标题', '用户名或密码错误', QMessageBox.Ok)
        else:
            reply = QMessageBox.information(self, '标题', '用户名或密码错误', QMessageBox.Ok)

    def registered(self):
        self.username = self.lineEdit_3.text()
        self.password = self.lineEdit_4.text()
        self.password2 = self.lineEdit_5.text()
        sql = "select * from username"
        cur.execute(sql)
        one_row = cur.fetchone()
        if one_row:
            sql = "select * from username where username=%s;"
            cur.execute(sql, self.username)
            one_row = cur.fetchone()
            if (one_row):
                reply = QMessageBox.information(self, '标题', '该用户名已被注册', QMessageBox.Ok)
            else:
                if (self.password == self.password2):
                    sql = "insert into username(username,password) values (%s,%s);"
                    cur.execute(sql, [self.username, self.password])
                    db.commit()
                    reply = QMessageBox.information(self, '标题', '成功注册', QMessageBox.Ok)
                else:
                    reply = QMessageBox.information(self, '标题', '密码不一致', QMessageBox.Ok)
        else:
            if self.password == self.password2:
                sql = "insert into username(username,password) values (%s,%s);"
                cur.execute(sql, [str(self.username), str(self.password)])
                db.commit()
                reply = QMessageBox.information(self, '标题', '成功注册', QMessageBox.Ok)
            else:
                reply = QMessageBox.information(self, '标题', '密码不一致', QMessageBox.Ok)

    def get_ip(self):
        """
        pushbutton_get_ip控件点击触发的槽
        :return: None
        """
        # 获取本机ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            my_addr = s.getsockname()[0]
            self.lineEdit_7.setText(str(my_addr))

        finally:
            s.close()

    def tcp_server_start(self):
        """
        功能函数，TCP服务端开启的方法
        :return: None
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 取消主动断开连接四次握手后的TIME_WAIT状态
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 设定套接字为非阻塞式
        self.tcp_socket.setblocking(False)
        try:
            port = int(self.lineEdit_8.text())
            self.tcp_socket.bind(('', port))
        except Exception as ret:
            msg = '请检查端口号\n'
            self.textBrowser_4.append(msg)
        else:
            self.tcp_socket.listen()
            self.sever_th = threading.Thread(target=self.tcp_server_concurrency)
            self.sever_th.start()
            msg = 'TCP服务端正在监听端口:%s\n' % str(port)
            self.textBrowser_4.append(msg)
            self.link = True

    def tcp_server_concurrency(self):
        """
        功能函数，供创建线程的方法；
        使用子线程用于监听并创建连接，使主线程可以继续运行，以免无响应
        使用非阻塞式并发用于接收客户端消息，减少系统资源浪费，使软件轻量化
        :return:None
        """
        while True:
            try:
                client_socket, client_address = self.tcp_socket.accept()
            except Exception as ret:
                time.sleep(0.001)
            else:
                client_socket.setblocking(False)
                # 将创建的客户端套接字存入列表,client_address为ip和端口的元组
                self.client_socket_list.append((client_socket, client_address))
                msg = 'TCP服务端已连接IP:%s端口:%s\n' % client_address
                self.textBrowser_4.append(msg)
            # 轮询客户端套接字列表，接收数据
            for client, address in self.client_socket_list:
                try:
                    recv_msg = client.recv(1024)
                except Exception as ret:
                    pass
                else:
                    if recv_msg:
                        msg = recv_msg.decode('utf-8')
                        sql = "insert into server_chat_save (server,client) values(%s,%s)"
                        cur.execute(sql, [None, msg])
                        db.commit()
                        msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                        self.textBrowser_4.append(msg)

                    else:
                        client.close()
                        self.client_socket_list.remove((client, address))

    def tcp_send(self):
        """
        功能函数，用于TCP服务端和TCP客户端发送消息
        :return: None
        """
        if self.link is False:
            msg = '请选择服务，并点击连接网络\n'
            self.textBrowser_4.append(msg)
        else:
            try:
                send_msg = (str(self.textEdit.toPlainText()))
                # 向所有连接的客户端发送消息
                for client, address in self.client_socket_list:
                    client.send(send_msg.encode('utf-8'))
                sql = "insert into server_chat_save (server,client) values(%s,%s)"
                cur.execute(sql, [send_msg, None])
                db.commit()
                msg = '你（服务端）:%s\n' % send_msg
                self.textBrowser_4.append(msg)
            except Exception as ret:
                msg = '发送失败\n'
                self.textBrowser_4.append(msg)

    def click_clear(self):
        """
        pushbutton_clear控件点击触发的槽
        :return: None
        """
        # 清空接收区屏幕
        self.textBrowser_4.clear()


QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)  # 使窗体按照Qt设计显示
app = QtWidgets.QApplication(sys.argv)
main = Main()
main.show()
sys.exit(app.exec_())

# 关闭游标和数据库连接
cur.close()
db.close()
