#!/usr/bin/env python
#!encoding:utf-8
#author: yujun
#dateL 2020-07-02

'''
用于演示如何使用proxy登陆指定服务器
'''

import paramiko

class SSHServerConfig:
    '''
    用于封装SSHClient连接服务器的参数
    '''
    def __init__(self, hostname, port, username, password, key_filename):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename



def login_server_via_proxy(dest_server, proxy_server):
    '''
    使用proxy_server作为代理服务器，通过代理服务器连接目标服务器dest_server
    连接步骤：
            1. 通过ssh登陆上代理服务器
            2. 获取代理服务器连接的channel
            3. 在登陆目标服务器时使用获取到的代理服务器channel
    按照此方法可串联多个服务器登陆到指定服务器。
    :param SSHServerConfig dest_server 需要登陆的目标服务器
    :param SSHServerConfig proxy_server 使用的代理服务器
    :return 登陆到目标服务器的SSHClient
    '''
    if not isinstance(dest_server, SSHServerConfig) or not isinstance(proxy_server, SSHServerConfig):
        raise ValueError("parameter: [dest_server] and [proxy_server] must be SSHServerConfig")
    #1 登陆代理服务器
    proxy_client = paramiko.SSHClient()
    proxy_client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    proxy_client.connect(hostname=proxy_server.hostname, port=proxy_server.port, username=proxy_server.username, password=proxy_server.password)
    
    #2 获取transport
    proxy_transport = proxy_client.get_transport()
    dest_addr = (dest_server.hostname, dest_server.port)
    local_addr = (proxy_server.hostname, proxy_server.port)
    #3 获取代理服务器的channel
    proxy_channel = proxy_transport.open_channel(kind="direct-tcpip", dest_addr=dest_addr, src_addr=local_addr)

    dest_client = paramiko.SSHClient()
    dest_client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
    #4 使用获取到的channel登陆目标服务器，设置sock参数为获取到的channel, eg:sock=proxy_channel
    dest_client.connect(hostname=dest_server.hostname, port=dest_server.port, username=dest_server.username,password=dest_server.password, sock = proxy_channel)
    return dest_client



if __name__ == '__main__':
    proxy = SSHServerConfig(hostname='192.168.1.100', port=22, username='root', password='password',key_filename = None)
    dest = SSHServerConfig(hostname='192.168.1.103', port=22, username='root', password='password',key_filename = None)
    client = login_server_via_proxy(dest, proxy)
    stdin, stdout, stderr = client.exec_command('pwd')
    data = stdout.read(1024*1024)
    print(data.decode('utf-8'))
