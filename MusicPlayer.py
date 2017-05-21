from tkinter import *
from tkinter.filedialog import *
import pygame

def load():
    global musics
    musics = askopenfilenames(title = "Load musics", filetypes = [("mp3 files", ".mp3")])
    print(musics)
    
def playMusic():
    global musics
    print("play musics")
    pygame.mixer.music.load(musics[0]) #Load the first music
    for i in range(len(musics)-1):
        pygame.mixer.music.queue(musics[i+1]) #Puts the following music in the queue
    pygame.mixer.music.play()
    
def pause():
    pygame.mixer.music.pause()
    pauseButton.configure(command = unpause)

def unpause():
    pygame.mixer.music.unpause()
    pauseButton.configure(command = pause)

def setVolume(volume):
    pygame.mixer.music.set_volume(float(volume))

musics = ()

pygame.init()
pygame.mixer.init()

window = Tk()

loadMusicButton = Button(window, text = "Load musics", width = 20, command = load)
loadMusicButton.pack()

playMusicButton = Button(window, text = "Play musics", width = 20, command = playMusic)
playMusicButton.pack()

pauseButton = Button(window, text = "Pause", width = 20, command = pause)
pauseButton.pack()

volumeScale = Scale(window, to = 1, resolution = 0.01, orient = HORIZONTAL, command = setVolume)
volumeScale.set(pygame.mixer.music.get_volume())
volumeScale.pack()

window.mainloop()
