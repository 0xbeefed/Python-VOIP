import socket

host = '127.0.0.1'
host = '192.168.1.29'
port = 60000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
logged = False
while not logged:
    host = input('HOST> ')
    try:
        server.connect((host, port))
        logged = True
        print('Logged on ' + host + ':'+ str(port))
        user_id = server.recv(1024).decode()
        print('You got the com ID: ' + user_id)
    except:
        print('Refused!')

send = b""
while 1:
    msg = input(user_id + '> ')
    if (msg != ''):
        server.send(msg.encode())
    print(server.recv(1024).decode())

server.close()
