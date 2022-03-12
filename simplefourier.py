import matplotlib.pyplot as plt
from scipy.io import wavfile as wav
from scipy.fftpack import fft
import numpy as np
from math import sqrt

rate, data = wav.read('C:/Users/gr8en/Documents/Workspace/Python Projects/My Blender Scripts/Erase Master Test.wav')

fourier = fft(data.T[0])

nsdlen = int((int(data.size)/2)/2)

rate = 0.1

out = []

# for x in fourier[:nsdlen] :

f = np.linspace (rate,len(data), endpoint=False)
plt.plot (f, np.abs(fourier))
plt.title ('Magnitude spectrum of the signal')
plt.xlabel ('Frequency (Hz)')

print(out)
