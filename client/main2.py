from flask import Flask, render_template, request, redirect, jsonify
import socket
import json
import threading
from hanshu import recv_msg, send_msg
client_socket = socket.socket()
dict_1 = json.load(open("conf.json", encoding="utf-8"))
Ser_Ip = (dict_1["IP"], dict_1["port"])
client_socket.connect(Ser_Ip)  # 连接服务器
LHL = Flask(__name__)

@LHL.route("/")
def home():
    is_login = request.cookies.get("is_login")
    return render_template("home.html", is_login=is_login)

def check(type):
    user_name = request.form.get("user_name")
    user_pwd = request.form.get("user_pwd")
    msg_type, sender, recipient = type, user_name, "服务器"
    content = {"user_name": user_name, "user_pwd": user_pwd}
    data = (msg_type, sender, recipient, content)
    send_msg(client_socket, data)  # 发送消息到服务器
    size_msg = int(recv_msg(client_socket, 15).rstrip())  # 1.接收消息大小，接收信息为字符型,去除右边的空白符，转换为int型
    msg = json.loads(recv_msg(client_socket, size_msg))  # 接收信息，为字符型，将他转换为字典
    return msg

# 登陆
@LHL.route("/login",methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        msg = check(3)  # 接收服务器的消息，字典类型
        if msg["content"] == 0:  # 0 登陆校验通过，1 登陆校验失败
            user_name = request.form.get("user_name")
            dict_uname = {"user_name": user_name}
            with open("uname.json", "wb") as f:
                f.write(json.dumps(dict_uname).encode())
            rsp = redirect("/")
            # 设置Cookie值，如果登录成功则Cookie值is_login = "LHL_struggle" ,max_age值为Cookie值有效时间
            rsp.set_cookie("is_login", "LHL_struggle", max_age=60 * 60)
            return rsp
        else:
            return render_template("login_fail.html")

# 注册
@LHL.route("/register",methods=["POST", "GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        msg = check(2)  # 接收服务器的消息，字典类型
        if msg["content"] == 0:     # 0 注册成功，1用户名已存在 ，2注册失败
            return render_template("login.html")
        else:
            return render_template("reg_fail.html")

# 校验用户名是否存在
@LHL.route("/check_uname")
def check_uname():
    user_name = request.args.get("user_name")
    msg_type, sender, recipient, content = 4, user_name, "服务器", user_name
    data = (msg_type, sender, recipient, content)
    send_msg(client_socket, data)  # 发送消息到服务器
    size_msg = int(recv_msg(client_socket, 15).rstrip())  # 1.接收消息大小，接收信息为字符型,去除右边的空白符，转换为int型
    msg = json.loads(recv_msg(client_socket, size_msg))  # 接收信息，为字符型，将他转换为字典
    rsp = {}
    # 用户名存在返回1，不存在返回0
    rsp["err"] = msg["content"]
    return jsonify(rsp)    # 将字典转换为json格式返回

@LHL.route("/Addfriends")
def Addfriends():
    is_login = request.cookies.get("is_login")
    if is_login == "LHL_struggle":
        print("111")
        uname = json.load(open("uname.json", encoding="utf-8"))["user_name"]
        # msg_type = 代表了查看所有用户名
        msg_type, sender, recipient, content = 5, uname, "服务器", "user"
        data = (msg_type, sender, recipient, content)
        send_msg(client_socket, data)  # 发送消息到服务器
        size_msg = int(recv_msg(client_socket, 15).rstrip())  # 1.接收消息大小，接收信息为字符型,去除右边的空白符，转换为int型
        msg = json.loads(recv_msg(client_socket, size_msg))  # 接收信息，为字符型，将他转换为字典
        content = msg["content"]
        print(content)       # [['123123'], ['123456'], ['1234567'], ['159357'], ['456123']]
        return render_template("Addfriends.html", content=content)
    else:
        return redirect("login.html")

def SendRecv(type,content):
    '''
    :param type:       消息类型
    :param content:    内容
    :return:           接收的消息，为字典型
    '''
    sender = json.load(open("uname.json", encoding="utf-8"))["user_name"]
    msg_type, recipient = type, "服务器"
    data = (msg_type, sender, recipient, content)
    send_msg(client_socket, data)  # 发送消息到服务器
    size_msg = int(recv_msg(client_socket, 15).rstrip())  # 1.接收消息大小，接收信息为字符型,去除右边的空白符，转换为int型
    msg = json.loads(recv_msg(client_socket, size_msg))  # 接收信息，为字符型，将他转换为字典
    return msg

# 添加好友请求
@LHL.route("/addf")
def addf():
    uname = request.args.get("uname")  # 得到用户名
    # 添加好友的数据类型，6
    msg = SendRecv(6, uname)   # msg为字典
    print(msg)
    return msg["content"]

# 获取已添加好友信息
@LHL.route("/friends")
def friends():
    is_login = request.cookies.get("is_login")
    if is_login == "LHL_struggle":
        msg = SendRecv(7, "已添加的好友")  # msg为字典
        print(msg)
        content = msg["content"]
        return render_template("friends.html", content=content)

# 与好友聊天
@LHL.route("/friend_chat")
def friend_chat():
    is_login = request.cookies.get("is_login")
    if is_login == "LHL_struggle":
        uname = request.args.get("uname")  # 得到用户名
        return render_template("friend_chat.html", uname=uname)


if __name__ == "__main__":
    LHL.run(port=80, debug=True)