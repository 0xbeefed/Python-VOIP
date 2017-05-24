#########################################################
##### Python VOIP - Alexandre GAULT, Arthur CHARLES #####
#########################################################

import socket                # For networking
from threading import Thread # For multi-tasking
import datetime              # For log time

def get_time():
    """ Used only for debug, get datetime in a string <HH:MM:SS> """
    now = datetime.datetime.now()
    return '<' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second) + '>'

class thread_home(Thread):
    """ This thread handle new clients """

    def __init__(self, host, port):
        # Method called on creation
        Thread.__init__(self)
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.bind((host, port))
        self.conn.listen(5)
        print(get_time() + ' Server listenning on ' + host + ':' + str(port))

    def run(self):
        # Loop for accepting new connection
        while True:
            sock, data = self.conn.accept()
            thread = thread_client(sock, data)
            thread.start()

            
class thread_client(Thread):
    """ This thread handle connected clients """

    def __init__(self, sock, data):
        # Method called on creation
        global clients
        Thread.__init__(self)
        self.sock = sock
        self.data = data
        self.pseudo = self.sock.recv(1024).decode()
        
        if (self.pseudo not in clients):
            # If the pseudo isn't already used, tell users that a new client is here
            clients[self.pseudo] = [self.data, self.sock]
            output = '[SETUP]: '
            for pseudo in clients:
                output += pseudo + ', '
            output = output.encode()
            for pseudo, client in clients.items():
                client[1].send(output)
            self.running = True
            print(get_time() + ' Client "' + self.pseudo + '" connected: ' + str(self.data[0]) + ' ID: ' + str(self.data[1]))
            
        else:
            # Close connection if pseudo is already used by a client
            self.sock.send(b'[ERROR]: Username already in use')
            self.sock.close()
            self.running = False
            print(get_time() + ' Login error: "' + self.pseudo + '" - pseudo already in use')
            
    def run(self):
        global clients
        while self.running:
            try:
                # Receipt and send incoming messages
                frame = self.sock.recv(1024)
                for pseudo, client in clients.items():
                    if (client[0][1] != self.data[1]):
                        client[1].send(frame)
            except:
                # For any error, disconnect client
                print(get_time() + ' Client "' + self.pseudo + '" disconnected')
                self.sock.close()
                del clients[self.pseudo]
                
                # And update clients list
                output = '[SETUP]: '
                for pseudo in clients:
                    output += pseudo + ', '
                output = output.encode()
                for pseudo, client in clients.items():
                    client[1].send(output)
                self.running = False
                break
            

clients = {}
home = thread_home('169.254.135.23', 60000)
home.start()
home.join()