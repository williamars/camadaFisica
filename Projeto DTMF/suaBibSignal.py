
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal as window



class signalMeu:
    def __init__(self):
        self.init = 0

    def __init__(self):
        self.init = 0

    def generateSin(self, freq, amplitude, time, fs):
        n = time*fs
        x = np.linspace(0.0, time, n)
        s = amplitude*np.sin(freq*x*2*np.pi)
        return (x, s)

    def calcFFT(self, signal, fs):
        # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
        N  = len(signal)
        W = window.hamming(N)
        T  = 1/fs
        xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
        yf = fft(signal*W)
        return(xf, np.abs(yf[0:N//2]))

    def plotFFT(self, signal, fs):
        x,y = self.calcFFT(signal, fs)
        plt.figure()
        plt.plot(x, np.abs(y))
        plt.title('Fourier')

    def sayTheFrequency(self, number):
        if number == 1:
            f = [697, 1209]
        elif number == 2:
            f = [697, 1336]
        elif number == 3:
            f = [697, 1477]
        elif number == 4:
            f = [770, 1209]
        elif number == 5:
            f = [770, 1336]
        elif number == 6:
            f = [770, 1477]
        elif number == 7:
            f = [852, 1209]
        elif number == 8:
            f = [852, 1336]
        elif number == 9:
            f = [852, 1477]
        elif number == 0:
            f = [941, 1336]
        return f
        
    def sayTheNumber(self, list_):
        if list_ == [697, 1209]:
            number = 1
        elif list_ == [697, 1336]:
            number = 2
        elif list_ == [697, 1477]:
            number = 3
        elif list_ == [770, 1209]:
            number = 4
        elif list_ == [770, 1336]:
            number = 5
        elif list_ == [770, 1477]:
            number = 6
        elif list_ == [852, 1209]:
            number = 7
        elif list_ == [852, 1336]:
            number = 8
        elif list_ == [852, 1477]:
            number = 9
        elif list_ == [941, 1336]:
            number = 0
        return number
        
