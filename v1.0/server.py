import socket
from threading import Thread
import datetime

def get_time():
    now = datetime.datetime.now()
    return '<' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + '>'

class thread_home(Thread):
    "' This thread handle new clients '"
    
    def __init__(self, host, port):
        Thread.__init__(self)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((host, port))
        self.conn.listen(5)
        print(get_time() + ' Server listenning on ' + host + ':' + str(port))

    def run(self):
        while True:
            sock, data = self.conn.accept()
            thread = thread_client(sock, data)
            thread.start()

            
class thread_client(Thread):
    "' This thread handle connected clients '"

    def __init__(self, sock, data):
        global clients
        Thread.__init__(self)
        self.sock = sock
        self.data = data
        self.pseudo = self.sock.recv(1024).decode()
        clients[self.pseudo] = [self.data, self.sock]
        
        output = '[SETUP]: '
        for pseudo in clients:
            output += pseudo + ', '
        output = output.encode()
        for pseudo, client in clients.items():
            client[1].send(output)
            
        print(get_time() + ' Client "' + self.pseudo + '" connected: ' + str(self.data[0]) + ' ID: ' + str(data[1]))

    def run(self):
        global clients
        while True:
            try:
                frame = self.sock.recv(1024)
                for pseudo, client in clients.items():
                    if (client[0][1] != self.data[1]):
                        client[1].send(frame)
            except:
                print(get_time() + ' Client "' + self.pseudo + '" disconnected')
                self.sock.close()
                del clients[self.pseudo]
                
                output = '[SETUP]: '
                for pseudo in clients:
                    output += pseudo + ', '
                output = output.encode()
                for pseudo, client in clients.items():
                    client[1].send(output)
                    
                break
            

clients = {}
home = thread_home('192.168.1.29', 60000)
home.start()
home.join()

