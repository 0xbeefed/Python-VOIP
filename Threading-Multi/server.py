import socket
from threading import Thread

class thread_home(Thread):
    "' This thread handle new clients '"
    
    def __init__(self, host, port):
        Thread.__init__(self)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((host, port))
        self.conn.listen(5)
        print('[THREAD]: Server listenning on ' + host + ':' + str(port))

    def run(self):
        while True:
            sock, data = self.conn.accept()
            thread = thread_recv(sock, data[1])
            thread.start()
            clients.append([data[1], sock])
            print('[LOG]: New client: ' + str(data))


class thread_recv(Thread):
    "' This thread catch incoming messages '"

    def __init__(self, sock, i):
        Thread.__init__(self)
        self.sock = sock
        self.i = i
        print('[THREAD]: Receving created')

    def run(self):
        while True:
            try:
                data = self.sock.recv(1024)
                for client in clients:
                    if (client[0] != self.i):
                        client[1].send(data)
            except:
                print('[THREAD]: Receving closed')
                break


clients = []
home = thread_home('192.168.1.29', 60000)
home.start()
home.join()
