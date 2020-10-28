import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftshift
from suaBibSignal import signalMeu
import sounddevice as sd
import soundfile   as sf
import time

A  = 1.5
fs = 44100
T  = 10

def main():
    try:
        print("Inicializando o Emissor\n")
        mySignal = signalMeu()

        number = int(input("Digite o número de transmissão: "))
        f1, f2 = mySignal.sayTheFrequency(number)
    
        # Gerando os sinais
        x, sin1 = mySignal.generateSin(f1, A, T, fs)
        x, sin2 = mySignal.generateSin(f2, A, T, fs)

        # Somando as senoides
        sin = sin1 + sin2

        # Esperando 2 segundos para tocar...
        time.sleep(2)
        sd.play(sin, fs)

        # Plotando o gráfico temporal
        plt.figure()
        plt.plot(sin, '.-')
        plt.xlim(0, 1000)
        plt.show()

    except Exception as ex:
        print(ex)
    
if __name__ == "__main__":
    main()