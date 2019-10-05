import socket
import threading
import json
from hanshu import recv_msg, send_msg, check_user_name, check_uname_pwd, user_reg, find_uname
import os

dict_1 = json.load(open("conf.json", encoding='utf8'))    # 读取json文件并转换为字典
server_socket = socket.socket()
IP_address = (dict_1["IP"], dict_1["port"])
server_socket.bind(IP_address)
server_socket.listen(5)

client_socks_dict = {}  # 存用户名与客户端的套接字

uname_list = []   # 存在线用户名

add_fri = []  # 存放好友的列表

if not os.path.exists("friend.json"):     # 判断文件是否存在, 不存在则创建文件
    # friend.json 文件为好友集合文件
    with open("friend.json", "ab+") as f:   # 创建friend.json文件
        f.write(json.dumps({}).encode())

def chat(conn_socket, conn_address):
        try:
            while 1:
                print("1")
                # 接收信息
                size_msg = int(recv_msg(conn_socket, 15).rstrip())  # 1.接收消息大小，接收信息为字符型,去除右边的空白符，转换为int型
                str_msg = recv_msg(conn_socket, size_msg)               # 接收信息，为字符型
                msg = json.loads(str_msg)   # 转换为字典
                print("5", msg)
                msg_type = msg["msg_type"]    # 消息类型
                sender = msg["sender"]        # 发信人
                recipient = msg["recipient"]  # 收信人
                content = msg["content"]      # 接收的信息


                # 聊天请求
                if msg_type == 1:
                    if not client_socks_dict.__contains__(sender):   # 如果
                        client_socks_dict[sender] = conn_socket  # 存用户名与客户端的套接字
                        uname_list.append(sender)  # 导入用户名
                    print("在线用户：", uname_list)
                    # 校验对方是否在线,在线则把用户的消息发给对方
                    if recipient in uname_list:
                        to_client = client_socks_dict[recipient]   # 收信人对应的套接字
                        data = (msg_type, sender, recipient, content)   # 信息
                        send_msg(to_client, data)   # 发送消息
                    else:
                        # 不再线
                        sender = "服务器"
                        content = "对方不在线"
                        data = (msg_type, sender, recipient, content)
                        send_msg(conn_socket, data)          # 发送消息, data为元组

                # 注册请求
                if msg_type == 2:
                    print(content, type(content))
                    user_name = content["user_name"]
                    user_pwd = content["user_pwd"]
                    # 1 校验用户名是否存在， 校验通过返回0，用户名存在返回1
                    if check_user_name(user_name) == 1:   # 用户名已存在
                        recipient = sender
                        sender = "服务器"
                        content = 1   # 表用户名已存在
                        data = (msg_type, sender, recipient, content)
                        send_msg(conn_socket, data)  # 给客户端返回信息
                    if check_user_name(user_name) == 0:   # 用户名不存在
                        recipient = sender
                        sender = "服务器"
                        # 成功返回True，失败返回False
                        if user_reg(user_name, user_pwd):     # 将注册信息存入数据库
                            content = 0     # 注册成功
                        else:
                            content = 2     # 注册失败
                        data = (msg_type, sender, recipient, content)
                        send_msg(conn_socket, data)      # 给客户的返回消息 content = 0注册成功，2失败

                # 登陆请求
                if msg_type == 3:
                    print(content, type(content))
                    user_name = content["user_name"]
                    user_pwd = content["user_pwd"]
                    recipient = sender
                    sender = "服务器"
                    # 校验通过返回0，校验失败返回1
                    content = 1     # 默认校验失败
                    content = check_uname_pwd(user_name, user_pwd)     # 用户名及密码通过验证
                    data = (msg_type, sender, recipient, content)
                    send_msg(conn_socket, data)  # 给客户的返回消息 content = 0校验成功，1校验失败

                # 校验用户名请求
                if msg_type == 4:
                    print(content, type(content))
                    recipient = sender
                    sender = "服务器"
                    # 1 校验用户名是否存在， 不存在返回0，用户名存在返回1
                    if check_user_name(content) == 1:   # 用户名已存在
                        content = 1   # 表用户名已存在
                    else:   # 用户名不存在
                        content = 0
                    data = (msg_type, sender, recipient, content)
                    send_msg(conn_socket, data)  # 给客户端返回信息

                # 查看用户名请求
                if msg_type == 5:
                    recipient = sender
                    sender = "服务器"
                    content = find_uname()
                    print(content, type(content))
                    data = (msg_type, sender, recipient, content)
                    send_msg(conn_socket, data)  # 给客户端返回信息

                # 添加好友请求
                if msg_type == 6:
                    # friend.json 文件为好友集合文件，
                    friends_dict = json.load(open("friend.json", encoding="utf-8"))
                    if content not in add_fri:  # 如果以添加改好友
                        add_fri.append(content)    # 导入好友
                        friends_dict[sender] = add_fri    # 放入字典
                        with open("friend.json", "wb") as f:
                            f.write(json.dumps(friends_dict).encode())    # 将字典转换为字符串，在转换为字节型写入文件
                        content = "添加成功"
                    else:
                        content = "已为好友"
                    recipient = sender
                    sender = "服务器"
                    data = (msg_type, sender, recipient, content)
                    print(data)
                    send_msg(conn_socket, data)  # 给客户端返回信息

                # 获得已添加好友请求
                if msg_type == 7:
                    friends_dict = json.load(open("friend.json", encoding="utf-8"))    # 读取文件内容
                    if friends_dict.__contains__(sender):    # 判断是否有好友存在
                        content = friends_dict[sender]     # 返回列表
                    else:
                        content = ["你还没有好友"]
                    recipient = sender
                    sender = "服务器"
                    data = (msg_type, sender, recipient, content)
                    print(data)
                    send_msg(conn_socket, data)  # 给客户端返回信息

        except Exception as b:
            # print(b)
            print("出错了")
            # 如果用户退出登录，则删除字典和列表中的值
            client_socks_dict.pop(sender)
            uname_list.remove(sender)
            print("在线用户：", uname_list)
            conn_socket.close()

def main():
    try:
        while 1:
            print("等待中")
            conn_socket, conn_address = server_socket.accept()         # 等待连接
            print(conn_address, "已连接服务器")
            threading.Thread(target=chat, args=(conn_socket, conn_address)).start()
    except:
        server_socket.close()
        print("全部结束")

if __name__ == "__main__":
    main()

