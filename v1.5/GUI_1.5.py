from tkinter import *             # For GUI
import socket                     # For networking
from threading import Thread      # For multi-threading
import pyaudio                    # For get micro input
import audioop                    # For rms
from tkinter.filedialog import *  # For loading menu
import pygame                     # To manage musics
import os                         # To recover all files in directory
import time                       # To create delay

class thread_recv(Thread):
    def __init__(self, stream):
        Thread.__init__(self)
        self.stream = stream
        
    def run(self):
        global SOCK, CONNECTED
        while CONNECTED:
            try:
                data = SOCK.recv(1024)
                decoded = data.decode(errors='ignore') # server information can be packed with hexadecimal values, so ignore decoding errors
                if (decoded[0:9] == '[SETUP]: '): # [SETUP] is used to refresh logged clients's list
                    logList = decoded[9:].split(', ') # Create array of logged clients
                    del logList[-1] # remove the last one
                    for logLabel in gui['widget']['user']: # Delete old widgets 
                        logLabel.destroy()
                    gui['widget']['user'] = []
                    for pseudo in logList: # And create new ones
                        gui['widget']['user'].append(Label(gui['frame']['loglist'], text=pseudo)) 
                        gui['widget']['user'][len(gui['widget']['user'])-1].grid(row=len(gui['widget']['user']) + 1, column=0)
                else:
                    self.stream.write(data) # write incoming data in an output pyaudio stream for play it
                    pygame.mixer.music.set_volume(0.3) # When client receives data, decrease the volume of music
                    time.sleep(0.01)
                pygame.mixer.music.set_volume(1) # Restores the initial volume of music
            except:
                CONNECTED = False
                
class thread_send(Thread):
    def __init__(self, stream):
        Thread.__init__(self)
        self.stream = stream
        
    def run(self):
        global CONNECTED, SOCK
        tolerance = 70 # loop countdown tolerance
        trigger = 500  # minimum level for triggering send
        countdown = 0
        while CONNECTED:
            try:
                data = self.stream.read(1024, exception_on_overflow=False) # get a slice of 10 bits from the microphone's stream 
                countdown -= 1
                if (audioop.rms(data, 2) > trigger): # if a high audio level is detected, init countdown
                    countdown = tolerance
                    
                if (countdown > 0): # the countdown allows transmit the whole sentence without breaking it
                    SOCK.send(data)
            except:
                CONNECTED = False

def toggle_connect():
    global CONNECTED, PSEUDO, SOCK

    if not CONNECTED:
        # Connecting
        gui['widget']['ipEntry'].config(state='disabled')       # Input disabling
        gui['widget']['portEntry'].config(state='disabled')     # Input disabling
        gui['widget']['pseudoEntry'].config(state='disabled')   # Input disabling
        gui['widget']['connectButton'].config(state='disabled') # Input disabling
        gui['widget']['connectButton'].config(text='........')
        gui['window'].update_idletasks() # update widget view

        PSEUDO = gui['widget']['pseudoEntry'].get()
        host = gui['widget']['ipEntry'].get()
        port = int(gui['widget']['portEntry'].get())

        try:
            SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            SOCK.connect((host, port)) # Attempting connect to server
            SOCK.send(PSEUDO.encode()) # Send client's name before all
            CONNECTED = True

            audio = pyaudio.PyAudio()
            streamInput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024) # audio stream that's read client microphone
            streamOutput = audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True,
                frames_per_buffer=1024) # audio stream that's play incoming sounds

            receving = thread_recv(streamOutput)
            sending = thread_send(streamInput)
            receving.start() # start the thread
            sending.start()  # start the thread
            
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
        for logLabel in gui['widget']['user']: # Clear logged client's list
            logLabel.destroy()
                        
        gui['widget']['user'] = [] # And reset all
        gui['widget']['ipEntry'].config(state='normal')
        gui['widget']['portEntry'].config(state='normal')
        gui['widget']['pseudoEntry'].config(state='normal')
        gui['widget']['connectButton'].config(state='normal')
        gui['widget']['connectButton'].config(text='Connect')

def loadDir():
    global DIRECTORY, MUSICS, INDEXPLAYLIST
    DIRECTORY = askdirectory(title='Load directory') # Recovers directory with musics  
    if DIRECTORY != '':
        MUSICS = os.listdir(DIRECTORY) # Recovers the list of files in the directory
        MUSICS = [file for file in MUSICS if file[-4:]=='.mp3' or file[-4:]=='.wav'] # If in the directory, there are files that are not music, the deletes in the list 
        if MUSICS != []:
            pygame.mixer.music.load(DIRECTORY + '/' + MUSICS[INDEXPLAYLIST]) # Load the first music in the pygame.mixer
            pygame.mixer.music.play()
            gui['widget']['titleMusic'].config(text=MUSICS[INDEXPLAYLIST])
    
def play():
    global MUSICS
    if MUSICS != []:
        pygame.mixer.music.unpause()
        gui['widget']['playButton'].config(text='Pause', command=pause) # Switch the function of this button with the function pause

def pause():
    global MUSICS
    if MUSICS != []:
        pygame.mixer.music.pause()
        gui['widget']['playButton'].config(text='Play', command=play) # Switch the function of this button with the function play
    
def checkTrack():
    """
    When the music is ended, starts the next music automatically
    """
    global DIRECTORY, MUSICS, INDEXPLAYLIST
    if MUSICS != [] and not pygame.mixer.music.get_busy(): # If the pygame.mixer is not busy
        INDEXPLAYLIST = (INDEXPLAYLIST + 1) % len(MUSICS)
        pygame.mixer.music.load(DIRECTORY + '/' + MUSICS[INDEXPLAYLIST])
        pygame.mixer.music.play()
        gui['widget']['titleMusic'].config(text=MUSICS[INDEXPLAYLIST])
        gui['widget']['playButton'].config(text='Pause', command=pause)
    gui['window'].after(500, checkTrack) # Repeat this function every 500ms
        
def right():
    """
    Changes the music to the right in the list
    """
    global DIRECTORY, MUSICS, INDEXPLAYLIST
    if MUSICS != [] and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        INDEXPLAYLIST = (INDEXPLAYLIST + 1) % len(MUSICS)
        pygame.mixer.music.load(DIRECTORY + '/' + MUSICS[INDEXPLAYLIST])
        pygame.mixer.music.play()
        gui['widget']['titleMusic'].config(text=MUSICS[INDEXPLAYLIST])
        gui['widget']['playButton'].config(text='Pause', command=pause)

def left():
    """
    Changes the music to the left in the list
    """
    global DIRECTORY, MUSICS, INDEXPLAYLIST
    if MUSICS != [] and pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        INDEXPLAYLIST = (INDEXPLAYLIST - 1) % len(MUSICS)
        pygame.mixer.music.load(DIRECTORY + '/' + MUSICS[INDEXPLAYLIST])
        pygame.mixer.music.play()
        gui['widget']['titleMusic'].config(text=MUSICS[INDEXPLAYLIST])
        gui['widget']['playButton'].config(text='Pause', command=pause)

# CAPS variables are usually globals
CONNECTED = False
PSEUDO = 'Groot'
INDEXPLAYLIST = 0
MUSICS = []
DIRECTORY = ''

pygame.init() # Initialize all imported pygame modules

gui = { # gui dictionnary keep all the interface
    'window': Tk(),
    'frame': {},
    'widget': {}
    }

checkTrack()

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
gui['frame']['loglist'].grid(row=2, column=0)
gui['widget']['logBanner'] = Label(gui['frame']['loglist'], text='---------- LOGGED USERS ----------')
gui['widget']['logBanner'].grid(row=0, column=0)
gui['widget']['logFooter'] = Label(gui['frame']['loglist'], text='---------- MUSIC PLAYER ----------')
gui['widget']['logFooter'].grid(row=999, column=0)
gui['widget']['user'] = []

# PLAYER

gui['frame']['musicFrame1'] = Frame(gui['window'])
gui['frame']['musicFrame1'].grid(row=3, column=0)
gui['widget']['dirLoadingButton'] = Button(gui['frame']['musicFrame1'], text='Load directory', width=26, command=loadDir)
gui['widget']['dirLoadingButton'].grid(row=0, column=1)

gui['frame']['musicFrame2'] = Frame(gui['window'])
gui['frame']['musicFrame2'].grid(row=4, column=0)
gui['widget']['leftButton'] = Button(gui['frame']['musicFrame2'], text='<-', width=3, command=left)
gui['widget']['leftButton'].grid(row=0, column=0)
gui['widget']['playButton'] = Button(gui['frame']['musicFrame2'], text='Pause', width=17, command=pause)
gui['widget']['playButton'].grid(row=0, column=1)
gui['widget']['rightButton'] = Button(gui['frame']['musicFrame2'], text='->', width=3, command=right)
gui['widget']['rightButton'].grid(row=0, column=2)


gui['frame']['musicFrame3'] = Frame(gui['window'])
gui['frame']['musicFrame3'].grid(row=5, column=0)
gui['widget']['titleMusic'] = Label(gui['frame']['musicFrame3'], text='No music')
gui['widget']['titleMusic'].grid(row=0, column=0)


gui['window'].mainloop()
