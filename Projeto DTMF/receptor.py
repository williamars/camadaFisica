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
            duration = 3
            myRecording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()

        else:
            exit()

        yAudio = myRecording[:, 0]

        print("Plotando o som real")
        plt.figure()
        plt.plot(yAudio)
        plt.show()

        print("Plotando o Fourier")
        X, Y = mySignal.calcFFT(yAudio, fs)

        plt.figure()
        plt.plot(X, np.abs(Y))
        plt.show()

        thres = 0.87
        index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=50)
        if len(index != 2):
            while len(index) > 2:
                thres += 0.005
                index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=50)
            while len(index) < 2:
                thres -= 0.005
                index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=50)
        list_ = list()
        for freq in X[index]:
            if freq > 0:
                list_.append(freq)

        print("Frequências: ", list_)

        # subtract = 0
        # for i in list_:
        # for i in f1:
        #     result = f1 -

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
