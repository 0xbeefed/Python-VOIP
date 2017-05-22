from tkinter import *        # For GUI
import socket                # For networking
from threading import Thread # For multi-tasking
import pyaudio               # For get micro input
import audioop               # For rms


class thread_recv(Thread):
    def __init__(self, stream):
        global SOCK
        Thread.__init__(self)
        self.stream = stream
       
    def run(self):
        global SOCK, CONNECTED
        while CONNECTED:
            data = SOCK.recv(1024)
            decoded = data.decode(errors='ignore')
            if (decoded[0:9] == '[SETUP]: '):
                logList = decoded[9:].split(', ')
                del logList[-1]
                for logLabel in gui['widget']['logItem']:
                    logLabel.destroy()
                gui['widget']['logItem'] = []
                for pseudo in logList:
                    gui['widget']['logItem'].append(Label(gui['frame']['loglist'], text=pseudo))
                    gui['widget']['logItem'][len(gui['widget']['logItem'])-1].grid(row=len(gui['widget']['logItem']) + 1, column=0)
            elif (decoded[0:9] == '[ERROR]: '):
                toggle_connect()
            else:
                self.stream.write(data)


class thread_send(Thread):
    def __init__(self, stream):
        Thread.__init__(self)
        self.stream = stream

    def run(self):
        global CONNECTED, SOCK
        tolerance = 70 # loop count tolerance
        trigger = 2000  # minimum level for triggering send
        countdown = 0
        while CONNECTED:
            try:
                data = self.stream.read(1024, exception_on_overflow=False)
                countdown -= 1
                if (audioop.rms(data, 2) > trigger):
                    countdown = tolerance
                    SOCK.send(data)
                elif (countdown > 0):
                    SOCK.send(data)
            except:
                a = 0 # do something

def toggle_connect():
    global CONNECTED, PSEUDO, SOCK

    if not CONNECTED:
        # Connecting
        gui['widget']['ipEntry'].config(state='disabled')
        gui['widget']['portEntry'].config(state='disabled')
        gui['widget']['pseudoEntry'].config(state='disabled')
        gui['widget']['connectButton'].config(state='disabled')
        gui['widget']['connectButton'].config(text='........')
        gui['window'].update_idletasks()

        PSEUDO = gui['widget']['pseudoEntry'].get()
        host = gui['widget']['ipEntry'].get()
        port = int(gui['widget']['portEntry'].get())

        try:
            SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            SOCK.connect((host, port))
            SOCK.send(PSEUDO.encode())
            CONNECTED = True

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

            receving = thread_recv(streamOutput)
            sending = thread_send(streamInput)
            receving.start()
            sending.start()
            
            gui['widget']['connectButton'].config(state='normal')
            gui['widget']['connectButton'].config(text='Disconnect')
        except:
            gui['widget']['ipEntry'].config(state='normal')
            gui['widget']['portEntry'].config(state='normal')
            gui['widget']['pseudoEntry'].config(state='normal')
            gui['widget']['connectButton'].config(state='normal')
            gui['widget']['connectButton'].config(text='Connect')
            CONNECTED = False
        
    else:
        # Disconnecting
        CONNECTED = False
        SOCK.close()
        for logLabel in gui['widget']['logItem']:
            logLabel.destroy()
                        
        gui['widget']['logItem'] = []
        gui['widget']['ipEntry'].config(state='normal')
        gui['widget']['portEntry'].config(state='normal')
        gui['widget']['pseudoEntry'].config(state='normal')
        gui['widget']['connectButton'].config(state='normal')
        gui['widget']['connectButton'].config(text='Connect')

def onClose():
    "' Disconnect by closing window '"

    if (CONNECTED):
        toggle_connect()
    else:
        gui['window'].destroy()
        
CONNECTED = False
PSEUDO = 'Groot'
gui = {
    'window': Tk(),
    'frame': {},
    'widget': {}
    }
gui['window'].wm_title('Python VOIP')

# HEADER
gui['frame']['header'] = Frame(gui['window'])
gui['frame']['header'].grid(row=0, column=0)

gui['frame']['headerRow1'] = Frame(gui['frame']['header'])
gui['frame']['headerRow1'].grid(row=0, column=0)
gui['widget']['ipLabel'] = Label(gui['frame']['headerRow1'], text='Server Ip: ')
gui['widget']['ipLabel'].grid(row=0, column=0)
gui['widget']['ipEntry'] = Entry(gui['frame']['headerRow1'], width=14)
gui['widget']['ipEntry'].grid(row=0, column=1)
gui['widget']['ipSeparator'] = Label(gui['frame']['headerRow1'], text=' : ')
gui['widget']['ipSeparator'].grid(row=0, column=2)
gui['widget']['portEntry'] = Entry(gui['frame']['headerRow1'], width=5)
gui['widget']['portEntry'].grid(row=0, column=3)

gui['frame']['headerRow2'] = Frame(gui['frame']['header'])
gui['frame']['headerRow2'].grid(row=1, column=0)
gui['widget']['pseudoLabel'] = Label(gui['frame']['headerRow2'], text='Pseudo: ')
gui['widget']['pseudoLabel'].grid(row=0, column=0)
gui['widget']['pseudoEntry'] = Entry(gui['frame']['headerRow2'], width=14)
gui['widget']['pseudoEntry'].grid(row=0, column=1)
gui['widget']['connectButton'] = Button(gui['frame']['headerRow2'], text='Connect', command=toggle_connect)
gui['widget']['connectButton'].grid(row=0, column=2)

gui['widget']['ipEntry'].insert(END, '169.254.135.23')
gui['widget']['portEntry'].insert(END, '60000')
gui['widget']['pseudoEntry'].insert(END, PSEUDO)

# LOGLIST
gui['frame']['loglist'] = Frame(gui['window'])
gui['frame']['loglist'].grid(row=3, column=0)
gui['widget']['logBanner'] = Label(gui['frame']['loglist'], text='---------- LOGGED USERS ----------')
gui['widget']['logBanner'].grid(row=0, column=0)
gui['widget']['logFooter'] = Label(gui['frame']['loglist'], text='-------------------------------------')
gui['widget']['logFooter'].grid(row=999, column=0)
gui['widget']['logItem'] = []

# TRIGS
gui['window'].protocol("WM_DELETE_WINDOW", onClose) # Handle closing as a toggle if we are connected

gui['window'].mainloop()
