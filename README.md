# python-socket-threading-
# 通过pyqt5创建聊天程序客户端，点击设置连接按钮，和服务器端连接，点击发送按钮，将用户名和发送的消息发送给客户端和文本框内显示
数据库用的mysql
库的话没什么要求
表如下
      create table username
      (
          username varchar(20) null,
          password varchar(30) null
      );

      create table client_chat_save
      (
          server_chat varchar(100) null,
          client_chat varchar(100) null
      );


      create table server_chat_save
      (
          server varchar(100) null,
          client varchar(100) null
      );

