import pyaudio
import wave
import audioop

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 50
WAVE_OUTPUT_FILENAME = "output.wav"
MINI = 500
TOLERANCE = 70

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
streamOut = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

countdown = 0
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    rms = audioop.rms(data, 2)    # here's where you calculate the volume
    countdown -= 1
    if (rms > MINI):
        countdown = TOLERANCE
        streamOut.write(data)
    elif (countdown > 0):
        streamOut.write(data)

stream.stop_stream()
stream.close()
p.terminate()
