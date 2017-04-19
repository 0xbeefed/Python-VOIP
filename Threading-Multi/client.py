import socket
import pyaudio
from threading import Thread

class thread_recv(Thread):
    def __init__(self):
        Thread.__init__(self)
        print('[THREAD]: Receving Thread Instancied')
        
    def run(self):
        while 1:
            streamOutput.write(com_sock.recv(1024))


class thread_send(Thread):
    def __init__(self, stream):
        Thread.__init__(self)
        self.stream = stream
        print('[THREAD]: Sending Thread Instancied')
        
    def run(self):
        while 1:
            com_sock.send(self.stream.read(1024, exception_on_overflow=False))


host = '192.168.1.29'
port = 60000

com_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
com_sock.connect((host, port))

audio = pyaudio.PyAudio()
streamInput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024)
streamOutput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True,
                frames_per_buffer=1024)

receving = thread_recv()
sending = thread_send(streamInput)

receving.start()
sending.start()

receving.join()
sending.join()
