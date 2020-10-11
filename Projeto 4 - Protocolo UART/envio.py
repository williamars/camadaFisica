#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
# python -m serial.tools.list_ports
####################################################

from functions import (
    transformIntToBytes, 
    transformBytesToInt, 
    EOP, numberOfPackages,
    buildHandshakeHeader,
    seeError,
    headerPackages,
)
from enlace import *
import time
import random
import logging
logging.basicConfig(filename='Client1.txt', level=logging.DEBUG, format='%(asctime)s %(message)s')
# import os
# from tkinter import Tk
# from tkinter.filedialog import askopenfilename

# python -m serial.tools.list_ports
serialName   = "COM3"
sizeHeader   = 10
sizePayload  = 114
sizeEOP      = 4

endOP        = EOP() 
idServer     = 200
idSensor     = random.randint(0,10)
idFile       = random.randint(11,20)

def endingBecauseOfTime(com):
    com.sendData(b'\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00' + endOP)
    logging.debug("/ envio / 5 / 14")
    logging.info("Tempo finalizado")
    com.disable()
    exit()

def main():
    try:
        com = enlace(serialName)
        com.enable()
        print("Comunicação de  Envio  aberta!\n")
        
        # Tk().withdraw()
        # image = askopenfilename() 
        print("Transformando imagem em bytes")
        
        image        = './img/teste2.png'
        txBuffer     =  open(image, 'rb').read()
        sizeTxBuffer = len(txBuffer)
        
        print("O arquivo a ser enviado possui {} bytes\n".format(sizeTxBuffer))

        totalOfPackages, lastPayloadSize = numberOfPackages(sizeTxBuffer)

        typeOfMessage = 1
        actualPackage = 0

        CanClientInit = False
        while not CanClientInit:
            headerHandshake = buildHandshakeHeader(typeOfMessage, idSensor, idServer, totalOfPackages, idFile, lastPayloadSize)
            com.sendData(headerHandshake + endOP)
            logging.debug("/ envio / 1 / 14")
        
            headerAnswer  = com.rx.getNData(sizeHeader)
            contador = 0
            while headerAnswer == b'\x00' and contador <= 4:
                print("Enviando o Handshake pela vez {}". format(contador))
                com.sendData(headerHandshake + endOP)
                time.sleep(0.2)
                logging.debug("/ envio / 1 / 14")
                headerAnswer  = com.rx.getNData(sizeHeader)
                contador += 1

            if contador == 5:
                print("\nDeu 20 segundos sem comunicação. Finalizar")
                endingBecauseOfTime(com)

            payloadAnswer = com.rx.getNData(0)
            eopAnswer     = com.rx.getNData(sizeEOP)
            logging.debug("/ receb / 2 / 14")

            if seeError(headerAnswer, eopAnswer):
                print("[ERRO HANDSHAKE]: Header ou EOP")
            
            else:
                print("\nConfirmação recebida \n")
                typeMessage = headerAnswer[0:1]

                if typeMessage == transformIntToBytes(2):
                    typeOfMessage = 3
                    actualPackage = 1
                    CanClientInit = True


        count      = 1
        index_data = 0
        print("Vou começar a transmissão dos pacotes")
        while CanClientInit:
            if count < totalOfPackages:
                print("Enviando o pacote {}". format(count))
                header  = headerPackages(3, totalOfPackages, count, sizePayload)
                payload = txBuffer[index_data:index_data+sizePayload]
                com.sendData(header + payload + endOP)
                time.sleep(0.1)
                logging.debug("/ envio / 3 / {0} / {1} / {2}". format(128, count, sizeTxBuffer))
                
                print("Enviei. Esperando confirmação")
                headerConfirmation = com.rx.getNData(sizeHeader)

                contadorTempo = 1
                while headerConfirmation == b'\x00' and contadorTempo <= 4:
                    headerConfirmation = com.rx.getNData(sizeHeader)
                    contadorTempo += 1
                
                if contadorTempo == 5:
                    print("Acabou o tempo. Comunicação foi cortada")
                    endingBecauseOfTime(com)


                eopConfirmation    = com.rx.getNData(sizeEOP)
                type_ = transformBytesToInt(headerConfirmation[0:1])

                if type_ == 4:
                    print("Ok")
                    logging.debug("/ receb / 4 / 14")
                    count += 1
                    index_data += sizePayload
                elif type_ == 6:
                    print("Deu erro nos pacotes")
                    logging.debug("/ receb / 6 / 14")
                    lastReceived = headerConfirmation[7:8]
                    count = lastReceived + 1


            elif count == totalOfPackages:
                print("Enviando o último pacote")
                header  = headerPackages(3, totalOfPackages, count, lastPayloadSize)
                payload = txBuffer[index_data:index_data+lastPayloadSize]
                com.sendData(header + payload + endOP)
                time.sleep(0.1)
                logging.debug("/ envio / 3 / {0} / {1} / {2}". format(lastPayloadSize+14, count, sizeTxBuffer))
                
                print("Enviei. Esperando confirmação")
                headerConfirmation = com.rx.getNData(sizeHeader)
                eopConfirmation    = com.rx.getNData(sizeEOP)
                type_ = transformBytesToInt(headerConfirmation[0:1])
                
                if type_ == 4:
                    print("Deu certo no último")
                    logging.debug("/ receb / 4 / 14")
                    count += 1
                elif type_ == 6:
                    print("Deu erro no último")
                    logging.debug("/ receb / 6 / 14")
                    lastReceived = headerConfirmation[7:8]
                    count = lastReceived + 1

            else:
                CanClientInit = False
                print("SUCESSO!")

        print("Sucesso!")

    
        # Encerra comunicação
        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com.disable()
    except Exception as ex:
        print("[ERROR CLIENT]: \n", ex)
        com.disable()

if __name__ == "__main__":
    main()
