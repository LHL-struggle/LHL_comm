import socket
import json
import pymysql

conf = json.load(open("db.json", encoding='utf8'))    # 读取json文件并转换为字典

# 校验用户名
def check_user_name(user_name):
    '''
    函数功能：校验用户名是否合法
    函数参数：
    user_name 待校验的用户名
    返回值：校验通过返回0，用户名存在返回1
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from user where uname=%s", (user_name,))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()
    if rows:
        # 用户名已存在
        return 1
    return 0

# 登录验证
def check_uname_pwd(user_name, password):
    '''
    函数功能：校验用户名和密码是否合法
    函数参数：
    user_name 待校验的用户名
    password 待校验的密码
    返回值：校验通过返回0，校验失败返回1
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            # cur.execute("select name from login where name=%s and passwd=password(%s)", (user_name, password))
            cur.execute("select uname from user where uname=%s and upass=password(%s)", (user_name, password))
            # 通过游标获取执行结果
            rows = cur.fetchone()
    finally:
        # 关闭数据库连接
        conn.close()

    if rows:
        return 0
    return 1


def user_reg(uname, password):
    '''
    函数功能：将用户注册信息写入数据库
    函数描述：
    uname 用户名
    password 密码
    返回值：成功返回True，失败返回False
    '''
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])

    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("insert into user (uname, upass) values (%s, password(%s))", (uname, password))
            r = cur.rowcount
            conn.commit()
    finally:
        # 关闭数据库连接
        conn.close()
    return bool(r)

# 查看所有用户
def find_uname():
    # 连接数据库，conn为Connection对象
    conn = pymysql.connect(conf["db_server"], conf["db_user"], conf["db_password"], conf["db_name"])
    try:
        with conn.cursor() as cur:  # 获取一个游标对象(Cursor类)，用于执行SQL语句
            # 执行任意支持的SQL语句
            cur.execute("select uname from user",)
            # 通过游标获取执行结果
            rows = cur.fetchall()
    finally:
        # 关闭数据库连接
        conn.close()
    return rows



# 接收消息函数
def recv_msg(client_socket, len_recv):
    '''
    :param client_socket:  套接字
    :param len_recv:    接收文件大小
    :return:    返回接收信息,字符型
    '''
    recv_size = 0  # 接收大小
    msg_content = b""  # 接收内容
    while recv_size <= len_recv:
        recv_content = client_socket.recv(len_recv - recv_size)  # 单次接收内容
        if not recv_content:  # 如果接收文件为空，则跳出循环
            break
        recv_size += len(recv_content.decode())
        msg_content += recv_content
    msg = msg_content.decode()    # 字符型
    return msg

# 发送消息函数
def send_msg(client_socket,send_msg):
    # send_msg 为一个消息元组  由消息类型，发信人，收信人，信息内容 组成
    rsp = {}
    rsp["msg_type"] = send_msg[0]     # 消息类型
    rsp["sender"] = send_msg[1]      # 发信人
    rsp["recipient"] = send_msg[2]   # 收信人
    rsp["content"] = send_msg[3]     # 信息内容
    # 将字典转换为字符串，在求取他的大小，再转换为字符串填充为15B,转换为字节型
    len_rsp = str(len(json.dumps(rsp))).ljust(15).encode()              # 消息大小
    rsp = json.dumps(rsp).encode()   # 将字典转换为字符串在转换为二进制， 消息内容
    client_socket.send(len_rsp)    # 发送消息大小
    client_socket.send(rsp)        # 发送消息内容
