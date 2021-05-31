# -*- coding:utf-8 -*-
# noinspection PyUnresolvedReferences
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMessageBox
from Huice_look_client import Ui_Form
import sys
import pymysql
import socket
import threading

db = pymysql.connect(host='写自己的',
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
        self.client_th = None
        self.tcp_socket = None
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
        self.pushButton_11.clicked.connect(lambda: {self.tcp_client_start()})
        self.pushButton_7.clicked.connect(lambda: {self.tcp_send(),self.textEdit.clear()})
        self.pushButton_9.clicked.connect(lambda:self.click_clear())
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

    def tcp_client_start(self):
        """
        功能函数，TCP客户端连接其他服务端的方法
        :return:
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            address = (str(self.lineEdit_9.text()), int(self.lineEdit_8.text()))
        except Exception as ret:
            msg = '请检查目标IP，目标端口\n'
            self.textBrowser_4.append(msg)
        else:
            try:
                msg = '正在连接目标服务器\n'
                self.textBrowser_4.append(msg)
                self.tcp_socket.connect(address)
            except Exception as ret:
                msg = '无法连接目标服务器\n'
                self.textBrowser_4.append(msg)
            else:
                self.client_th = threading.Thread(target=self.tcp_client_concurrency, args=(address,))
                self.client_th.start()
                msg = 'TCP客户端已连接IP:%s端口:%s\n' % address
                self.textBrowser_4.append(msg)
                self.link = True
                self.pushButton_11.setEnabled(False)

    def tcp_client_concurrency(self, address):
        """
        功能函数，用于TCP客户端创建子线程的方法，阻塞式接收
        :return:
        """
        while True:
            recv_msg = self.tcp_socket.recv(1024)
            if recv_msg:
                msg = recv_msg.decode('utf-8')
                sql = "insert into client_chat_save (server_chat ,client_chat) values(%s,%s)"
                cur.execute(sql, [msg, None])
                db.commit()
                msg = '来自IP:{}端口:{}:\n{}\n'.format(address[0], address[1], msg)
                self.textBrowser_4.append(msg)
            else:
                self.tcp_socket.close()
                self.reset()
                msg = '从服务器断开连接\n'
                self.textBrowser_4.append(msg)
                break

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
                msg = '你（客户端）：%s\n' % send_msg
                sql = "insert into client_chat_save (server_chat,client_chat) values(%s,%s)"
                cur.execute(sql, [None, send_msg])
                db.commit()
                self.tcp_socket.send(send_msg.encode('utf-8'))
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
