# -*- coding: utf-8 -*-

import json
import socket

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def http_post(url, data=None, timeout=10):
    """
    使用 socket 发送 HTTP POST 请求

    Args:
        url (str):
            HTTP URL

        data (dict):
            发送的 JSON 数据

        timeout (float):
            超时时间

    Returns:
        tuple:
            (status_code, response_headers, response_body)
    """

    parsed = urlparse(url)

    if parsed.scheme.lower() != 'http':
        raise ValueError("只支持 http")

    host = parsed.hostname
    if not host:
        raise ValueError("URL 中没有有效的域名")


    port = parsed.port or 80
    path = parsed.path or '/'

    if parsed.query:
        path += '?' + parsed.query

    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    request = (
        'POST {} HTTP/1.1\r\n'
        'Host: {}\r\n'
        'Content-Type: application/json; charset=utf-8\r\n'
        'Content-Length: {}\r\n'
        'Connection: close\r\n'
        '\r\n'
    ).format(path, host, len(body)).encode('utf-8')

    request += body     # HTTP Header 和 Body 之间通过 \r\n\r\n 分隔

    sock = socket.create_connection((host, port), timeout=timeout)

    try:
        sock.sendall(request)
        response = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

    finally:
        sock.close()
    
    header_data, separator, body_data = response.partition(b'\r\n\r\n')

    if not separator:
        raise RuntimeError("收到的 HTTP 响应格式不正确")

    header_text = header_data.decode('iso-8859-1')
    header_lines = header_text.split('\r\n')
    status_line = header_lines[0]
    parts = status_line.split(' ', 2)
    if len(parts) < 2:
        raise RuntimeError("无法解析 HTTP 状态码")
    status_code = int(parts[1])


    response_headers = {}
    for line in header_lines[1:]:
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        response_headers[key.strip()] = value.strip()

    return status_code, response_headers, body_data


if __name__ == '__main__':

    url = 'http://papi.cgyear.com.cn/taskapi/project/listAllZynn'

    try:
        status_code, headers, body = http_post(url)
        print("Status Code:", status_code)
        print("Headers:", headers)
        print("Body:", body.decode('utf-8'))

    except Exception as e:
        print("POST 请求失败:", e)
