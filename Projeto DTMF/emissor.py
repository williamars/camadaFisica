import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
from suaBibSignal import signalMeu
import sounddevice as sd
import soundfile as sf
import time
import peakutils

A = 1.5
fs = 44100
T = 3
t = np.linspace(-T/2, T/2, T*fs)

sd.default.samplerate = fs
sd.default.channels = 1

frequencies_1 = [697, 770, 852, 941]
frequencies_2 = [1209, 1336, 1477, 1633]


def aproxima_number(frequencies, f_list, index):
    variable = frequencies[index]
    subtraction_min = 1000000
    for f in f_list:
        sub = frequencies[index] - f
        if np.abs(sub) < subtraction_min:
            subtraction_min = np.abs(sub)
            variable = f
    frequencies[index] = variable
    return frequencies


def main():
    try:
        print("Inicializando o Emissor\n")
        mySignal = signalMeu()

        number = int(input("Digite o número de transmissão: "))
        f1, f2 = mySignal.sayTheFrequency(number)
        print("As frequências a enviar: {} e {}". format(f1, f2))

        # Gerando os sinais
        x, sin1 = mySignal.generateSin(f1, A, T, fs)
        x, sin2 = mySignal.generateSin(f2, A, T, fs)

        # Somando as senoides
        sin = sin1 + sin2

        # Tocando o som
        sound = sd.playrec(sin, fs)
        sd.wait()
        audio_captado = sound[:, 0]
        print("Áudio tocado e recebido")

        # Fourier
        X, Y = mySignal.calcFFT(audio_captado, fs)

        # Pegando as frequências de maior influência
        thres = 0.3
        index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=20)
        if len(index != 2):
            while len(index) > 2:
                thres += 0.005
                index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=50)
            while len(index) < 2:
                thres -= 0.005
                index = peakutils.indexes(np.abs(Y), thres=thres, min_dist=50)
        frequencies = list()
        for freq in X[index]:
            if freq > 0:
                frequencies.append(freq)
        print("As frequências que mais aparecem são: {}".format(frequencies))

        # Aproxima o número para a frequência mais próxima
        change_first = aproxima_number(frequencies, frequencies_1, index=0)
        second = aproxima_number(change_first, frequencies_2, index=1)
        print("\nAproximando, temos as frequências: {}". format(second))

        # Descobre qual era o número
        number_received = mySignal.sayTheNumber(second)

        print("O número dessa frequência é o: {}". format(number_received))

        # Plotando o gráfico temporal do sinal tocado
        plt.figure()
        plt.title("Soma dos senos enviadas [Sinal Tocado]")
        plt.plot(sin)
        plt.xlim(0, 1000)
        plt.savefig('somaDosSenos.png', format='png')
        plt.show()

        # Plotando o gráfico temporal do sinal recebido
        plt.figure()
        plt.plot(audio_captado)
        plt.title("Sinal Ouvido")
        plt.savefig('signalReceived.png', format='png')
        plt.show()

        # Plotando o Fourier do sinal recebido
        plt.figure()
        plt.plot(X, np.abs(Y))
        plt.title("FFT do sinal ouvido")
        plt.savefig('FFTReceived.png', format='png')
        plt.show()

    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
