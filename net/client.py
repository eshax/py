from socket import *
import json
import struct

s = socket(AF_INET, SOCK_STREAM)

addr = ("127.0.0.1", 9999)
s.connect(addr)

data = input("   send: ")

ver = 20200224
cmd = 0
body = data.encode("utf-8")
header = [ver, cmd, len(body)]
headPack = struct.pack("!3I", *header)
data = headPack + body

s.send(data)

def parse(addr, data):
    print("receive: ", data)

headerSize = 12
dataBuffer = bytes()

while 1:
    data = s.recv(1024)
    if data:
        dataBuffer += data
        if len(dataBuffer) < headerSize:
            print("!!!too small.")
            break
        headPack = struct.unpack('!3I', dataBuffer[:headerSize])
        bodySize = headPack[2]
        if len(dataBuffer) < headerSize + bodySize:
            print("!!!not intact.")
            break
        body = dataBuffer[headerSize : headerSize + bodySize]
        parse(addr, json.loads(body.decode("utf-8")))
        dataBuffer = dataBuffer[ headerSize + bodySize : ]
    else:
        break

s.close()
