import socket
import select
import pyaudio
from threading import Thread

class Multithread_Send(Thread):
    def __init__(self):
        Thread.__init__(self)
        print('Sending Tread Instancied')
    def run(self):
        while 1:
            com_sock.send(streamInput.read(4096, exception_on_overflow=False))

class Multithread_Recv(Thread):
    def __init__(self):
        Thread.__init__(self)
        print('Receving Tread Instancied')
    def run(self):
        while 1:
            streamOutput.write(com_sock.recv(4096))

            
host = ''
port = 60000

#Master connection
master_com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
master_com.bind((host, port))
master_com.listen(5)
print('Listen on ' + str(port))

com_sock, com_data = master_com.accept()
print('Client logged')

#Run audio stream
audio = pyaudio.PyAudio()
streamInput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=4096)
streamOutput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True,
                frames_per_buffer=4096)

sending = Multithread_Send()
receving = Multithread_Recv()

sending.start()
receving.start()

sending.join()
receving.join()
