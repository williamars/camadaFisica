#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Adaptação: William Silva
#####################################################

# Para ver as portas: python -m serial.tools.list_ports

from enlace import *
import time
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Porta do PC
serialName = "COM4"

def main():
    try:
        # Interface para pegar a imagem
        Tk().withdraw()
        imageR = askopenfilename() 

        print("Carregando a imagem escolhida para transmissao")
        print (" - {}".format(imageR))
        print("-"*30)
        
        # Começar a contar tempo
        time_init = time.time()

        # Camada inferior da aplicação. Porta COM como parâmetro
        com = enlace(serialName)
    
        # Ativa a comunicação. Inicia os threads e comunicação serial
        com.enable()

        # Transformando imagem em bytes
        txBuffer = open(imageR, 'rb').read()  # txBuffer = bytes([255])
        print("Imagem transformada com sucesso!")
        time.sleep(0.1)

        # Pegando tamanho da imagem. Vai ser útil abaixo
        size_txBuffer = len(txBuffer)
        print("\nExistem {} bytes idealmente".format(size_txBuffer))

    
        # Início do envio do tamanho e imagem
        print("\nA TRANSMISSAO DE ENVIO OFICIAL VAI COMECAR!!!!!!!")
        print("-"*30)
        print("\nEstou enviando o tamanho da imagem primeiro")
        tam_img = (int(size_txBuffer)).to_bytes(2, byteorder='big')
        com.sendData(tam_img)
        time.sleep(0.01)

        print("Estou enviando a imagem agora")
        com.sendData(txBuffer)
        time.sleep(0.5)
        txSize = com.tx.getStatus()
        print("Tamanho do que foi enviado: {}".format(txSize))

        # Inicío da pegada de dados de volta para comparação
        print("-"*30)
        print("Recebendo os dados de volta")
        
        time.sleep(0.5)     

        compair, nCompair = com.getData(2)
        time.sleep(0.1)     
        chegou = int.from_bytes(compair, byteorder='big')

        time.sleep(0.5)        

        # Confere se deu tudo certo
        if chegou == size_txBuffer:
            time_end = time.time()
            print("\nParece que tudo funcionou! Parabens! ;D ")
            print("Os dados enviados e os recebidos sao de tamanhos iguais! ")
            time_final = time_end - time_init
            baud_rate = chegou/time_final
            print("O tempo de transmissão foi de {0:.2f} segundos". format(time_final))
            print("\nBaudRate: {0:.2f}bytes/s". format(baud_rate))

        com.disable()
        print("\nPorta de envio desabilitada")
    except:
        print("Envio falhou")
        com.disable()

if __name__ == "__main__":
    main()
