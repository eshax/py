import socket, json, datetime
from threading import Thread
import struct

clients = []
services = []
tasks = []

def send(cli, data):
    ver = 20200224
    cmd = 1
    body = json.dumps(data).encode("utf-8")
    header = [ver, cmd, len(body)]
    headPack = struct.pack("!3I", *header)
    data = headPack + body
    cli.send(data)

def find_client(addr):
    cli = None
    for o in clients:
        x, y = o
        if x == addr:
            cli = y
            break
    return cli

def find_service(addr = None, type = None):
    cli = None
    for o in services:
        x, y, z = o
        if (not addr or addr == x) and (not type or type == y):
            cli = z
            break
    return cli

def register_service(addr, type, cli):
    b = True
    for o in services:
        x, y, z = o
        if x == addr and y == type:
            b = False
            break
    if b:
        services.append((addr, type, cli, ))
    return b

def parse_register(addr, data, cli):
    if register_service(addr, data["type"], find_client(addr)):
        o = {"cmd": "register", "type": data["type"], "status": "200"}
    else:
        o = {"cmd": "register", "type": data["type"], "status": "400"}
    send(cli, o)

def parse_analysis(addr, data):
    channel = "{0:%y%m%d%H%M%S%f}".format(datetime.datetime.now())
    tasks.append((channel, addr, data, ))
    type = data["type"]
    image = data["image"] # base 64
    cli = find_service(type=type)
    o = {"cmd": "analysis", "channel": channel, "type": type, "image": image}
    send(cli, o)

def parse_analysis_result(data):
    type = data["type"]
    channel = data["channel"]
    object_type = data["object_type"]
    for t in tasks:
        x, y, z = t
        if x == channel:
            cli = find_client(y)
            o = {"cmd": "analysis_result", "type": type, "object_type": object_type}
            send(cli, o)
            tasks.remove(t)
            break

def parse(addr, data):
    if data["cmd"] == "register":
        parse_register(addr, data, cli)

    if data["cmd"] == "analysis":
        parse_analysis(addr, data)

    if data["cmd"] == "analysis_result":
        parse_analysis_result(data)

def leave(addr):
    print(addr, "leave")
    for o in services:
        x, y, z = o
        if x == addr:
            services.remove(o)
    for o in clients:
        x, y = o
        if x == addr:
            clients.remove(o)
    print("service count: ", len(services))
    print(" client count: ", len(clients))
    print("   task count: ", len(tasks))

def chat(cli, addr):

    headerSize = 12
    dataBuffer = bytes()
    print(addr, "come")
    try:
        while 1:
            data = cli.recv(1024)
            if data:
                dataBuffer += data
                if len(dataBuffer) < headerSize:
                    print("too small.")
                    break
                headPack = struct.unpack('!3I', dataBuffer[:headerSize])
                bodySize = headPack[2]
                if len(dataBuffer) < headerSize + bodySize:
                    print("not intact.")
                    break
                body = dataBuffer[headerSize : headerSize + bodySize]
                print(addr, "ver: %s  cmd: %s, bodySize: %s " % headPack)
                print(body.decode("utf-8"))
                parse(addr, json.loads(body.decode("utf-8")))
                dataBuffer = dataBuffer[ headerSize + bodySize : ]

            else:
                leave(addr)
                cli.close()
                break
    except:
        leave(addr)
        cli.close()

ser = socket.socket()
ser.bind(('', 9999))
ser.listen()

while True:

    cli, addr = ser.accept()
    clients.append((addr, cli,))
    Thread(target=chat, args =(cli, addr, )).start()

ser.close()
