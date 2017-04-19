import socket
import select

host = ''
port = 60000

master_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master_com.bind((host, port))
master_com.listen(5)
print('Listen on ' + str(port))

run = True
logged_clients_sock = []
while run:

    # Accepting new connections
    requested_coms, wlist, xlist = select.select([master_com], [], [], 0.05)
    for com in requested_coms:
        com_sock, com_data = com.accept()
        logged_clients_sock.append(com_sock)
        com_sock.send(str(com_data[1]).encode())
        print('New client: ' + str(com_data[1]))

    # Update clients
    clients_toUpdate = []
    try:
        # Catch all items that waits
        clients_toUpdate, wlist, xlist = select.select(logged_clients_sock, [], [], 0.05)
    except select.error:
        pass
    else:
        for client in clients_toUpdate:
            broadcast = str(client.getpeername()[1]) + ' -> ' + client.recv(1024).decode()
            print(broadcast)
            #Broadcast to all clients
            for client in logged_clients_sock:
                client.send(broadcast.encode())

print("Closing sockets")
for client in logged_clients_sock:
    client.close()
master_com.close()
