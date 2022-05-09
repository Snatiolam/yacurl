#!/bin/python3

from PIL import Image
import sys
import socket
import http.client
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from http.client import HTTPResponse
from io import BytesIO

class FakeSocket():
    def __init__(self, response_bytes):
        self._file = BytesIO(response_bytes)
    def makefile(self, *args, **kwargs):
        return self._file

def main():
    if len(sys.argv) < 3:
        print('Usage: ./yacurl <host> <port>')
        sys.exit(1)
    urlparse("scheme://netloc/path;parameters?query#fragment")
    url = urlparse(sys.argv[1])
    host = url.hostname
    path = url.path

    try:
        host = socket.gethostbyname(host)
    except:
        print(sys.argv[1] + " could not be reached")
        exit(1)
    port = int(sys.argv[2])
    sock = connect(host, port)
    data = send_data(sock, host, path)
    parse_data(data)

def connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ("Attempting to connect to %s on port %s" % (host, port))
    try:
        sock.connect((host, port))
        print("Connected to %s on port %s" % (host, port))
        return sock
    except socket.error as error:
        print("Connection to %s on port %s failed: %s" % (host, port, error))
        return None

def send_data(sock, host, path):
    if path == "":
        path = "/"
    send_buffer = "GET "+ path +" HTTP/1.0\r\n"\
                  "Host: " + host + "\r\n\r\n"
    print('Http request:')
    print(send_buffer)
    sock.sendall(bytes(send_buffer, 'utf-8'))
    data = b''
    while True:
        part = sock.recv(2048)
        data += part
        if part == b'':
            break
    return data

def parse_data(data):
    print('Http response:')
    source = FakeSocket(data)
    response = HTTPResponse(source)
    try:
        response.begin()
        headers = response.headers
        content = ''
        if 'text' in headers['content-type']:
            content = response.read().decode('utf-8')
        else:
            content = response.read()

        print("Status: " + str(response.status))
        print()
        print("Headers: ")
        print(headers)
        contentType = headers['content-type']
        if 'text/html' in contentType:
            print("Content: ")
            print(content)
            print()
            output_file = open('file.html', 'w')
            output_file.write(content)
            output_file.close()
            parse_html(content)
            print('The html has been downloaded')
        if 'image' in contentType:
            img = Image.open(BytesIO(content))
            img.save('img.jpeg')
            print('The image has been downloaded')
        if 'pdf' in contentType:
            output_file = open('PDF.pdf', 'wb')
            output_file.write(content)
            output_file.close()
            print('The pdf has been downloaded')

    except http.client.BadStatusLine:
        print("Bad status line - status unknown")

def parse_html(html):
    parser = BeautifulSoup(html, 'lxml')
    imgTags = parser.findAll('img')
    print("All img tags:")
    print(imgTags)
    print('Img tags sources:')
    print("\n".join(set(tag['src'] for tag in imgTags)))

if __name__=='__main__':
    main()
