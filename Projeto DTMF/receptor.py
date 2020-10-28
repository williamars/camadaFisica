import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
from suaBibSignal import signalMeu
import sounddevice as sd
import soundfile as sf
import peakutils


fs = 44100
f1 = [697, 770, 852, 941]
f2 = [1209, 1336, 1477, 1633]


def main():
    try:
        print("Inicializando o Receptor")
        mySignal = signalMeu()
        answer = input("Posso começar a ouvir? S/N: ")

        if answer == "S" or answer == "s":
            duration = 4
            myRecording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()

        else:
            exit()

        print("Plotando o som real")
        plt.plot(myRecording)
        # plt.show()

        yAudio = myRecording[:, 0]

        print("Plotando o Fourier")
        X, Y = mySignal.calcFFT(yAudio, fs)

        plt.plot(X, np.abs(Y))
        # plt.show()

        index = peakutils.indexes(np.abs(Y), thres=0.7, min_dist=50)
        print("index de picos {}" .format(index))
        list_ = list()
        for freq in X[index]:
            if freq > 0:
                list_.append(freq)

        new = [0]*2
        new[0] = list_[0]
        new[1] = list_[1]

        subtract = 0
        for i in f1:
            result = f1 - new[0]

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
