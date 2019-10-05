import socket
import json

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



