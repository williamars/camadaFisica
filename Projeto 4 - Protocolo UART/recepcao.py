#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
####################################################

from functions import (
    transformIntToBytes, 
    transformBytesToInt,
    seeError,
    EOP,
    buildHandshakeHeader,
    headerConfirmation
)
from enlace import *
import time
import logging
logging.basicConfig(filename='Server5.txt', level=logging.DEBUG, format='%(asctime)s %(message)s')

sizeHeader   = 10
sizePayload  = 114
sizeEOP      = 4
serialName   = "COM4"
myID         = 200
imageW       = './img/thisIsCopy.png'
idFile       = 0
endOP        = EOP()

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
        print("Comunicação de Recepção aberta!")
        print("Vou esperar alguém se comunicar comigo")

        free = True
        while free:
            firstHeader  = com.rx.getNData(sizeHeader)
            while firstHeader == b'\x00':
                time.sleep(1)
                firstHeader  = com.rx.getNData(sizeHeader)
            firstEOP     = com.rx.getNData(sizeEOP)

            if seeError(firstHeader, firstEOP):
                print("[ERROR]")
                com.disable()
                exit()
            else:
                typeMessage     = transformBytesToInt(firstHeader[0:1])
                myIDReceived    = transformBytesToInt(firstHeader[2:3])
                totalOfPackages = transformBytesToInt(firstHeader[3:4])
                fileID          = transformBytesToInt(firstHeader[5:6])
                lastPayloadSize = transformBytesToInt(firstHeader[8:9])

                if typeMessage == 1:
                    if myIDReceived != myID:
                        print(myIDReceived)
                        print(myID)
                        print("[ERROR] Opa, essa comunicação não é comigo")
                        logging.debug("/ receb / 1 / 14/ [ERROR]")
                        time.sleep(1)
                    else:
                        print("Opa, essa comunicação é comigo mesmo")
                        logging.debug("/ receb / 1 / 14")
                        typeOfMessage = 2
                        time.sleep(1)
                        free = False

        # Enviar a comunicação de que pode começar a enviar os pacotes
        headerAnswer = buildHandshakeHeader(typeOfMessage, 0, myID, idFile, totalOfPackages,lastPayloadSize)
        com.sendData(headerAnswer + endOP)
        logging.debug("/ envio / 2 / 14")
        time.sleep(1)

        txBuffer = b''
        count = 1
        print(totalOfPackages)
        while count <= totalOfPackages:

            print("Pegando o pacote {}". format(count))
            headerPackages    = com.rx.getNData(sizeHeader)

            contadorTempo = 1
            while headerPackages == b'\x00' and contadorTempo <= 4:
                print("\nComunicação foi cortada. Tentando pegar novamente")
                headerPackages = com.rx.getNData(sizeHeader)

                header = headerConfirmation(6, count, count-1)
                com.sendData(header + endOP)
                logging.debug("/ envio / 6 / 14")

                contadorTempo += 1

            if contadorTempo == 5:
                print("O tempo acabou. Comunicação encerrada")
                endingBecauseOfTime(com)

            actualPackage     = transformBytesToInt(headerPackages[4:5])
            if actualPackage == count:
                print("Está correto")
                actualPayloadSize = transformBytesToInt(headerPackages[5:6])
                payloadMessage    = com.rx.getNData(actualPayloadSize)
                eopMessage        = com.rx.getNData(sizeEOP)
                logging.debug("/ receb / 3 / {}". format(actualPayloadSize+14))

                time.sleep(0.1)
                txBuffer += payloadMessage

                print("Enviando confirmação\n")
                header = headerConfirmation(4, 0, count)
                com.sendData(header + endOP)
                logging.debug("/ envio / 4 / 14")

                count += 1
            else:
                print("O pacote está errado, vou pedir para reenviar")
                actualPayloadSize = transformBytesToInt(headerPackages[5:6])
                payloadMessage    = com.rx.getNData(actualPayloadSize)
                eopMessage        = com.rx.getNData(sizeEOP)
                logging.debug("/ receb / 3 / 14")
                header = headerConfirmation(6, count, actualPackage)
                com.sendData(header + endOP)
                logging.debug("/ envio / 6 / 14")
        
        print("Tudo pronto! Arquivo pegado!")

        print("-"*30)
        print ("Salvando dados no arquivo:")
        print (" - {}".format(imageW))

        f = open(imageW, 'wb')
        f.write(txBuffer)
        f.close()
        
        print("Imagem salva com sucesso!")

        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        # print(txBuffer)
        com.disable()

    except Exception as ex:
        print("[ERROR SERVER]: \n", ex)
        com.disable()

if __name__ == "__main__":
    main()
